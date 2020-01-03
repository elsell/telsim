import time
import multiprocessing
import threading
import numpy as np
import cv2
from network import Network, NoNetwork
from video import Webcam, Video, VideoDisplayer
import planner
import controller
import recognition
import fsm


class Drone:
    """Class for interacting with a drone. You can choose which drone by
setting the 'which' argument to:

planner: plots planned flight path of drone
webcam:  simulated drone using the webcam
drone:   Tello EDU drone using the network

    """
    def __init__(self, which='webcam'):
        self.which = which
        if which == 'planner':
            self.network = self.video = planner.Planner()
            self.displayer = None

        elif which == 'webcam':
            self.network = NoNetwork()
            self.video = Webcam()
            self.displayer = VideoDisplayer(self.video)
            
        elif which == 'drone':
            self.network = Network()
            self.video = Video()
            self.displayer = VideoDisplayer(self.video)
            
        else:
            raise "Unrecognized option: {}".format(which)

        self.stop()
        self.network.sendrecv('streamon')

    def __enter__(self):
        self.network.sendrecv('command')
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.land()
        self.network.close()
        self.video.stop()

        if exc_type is not None:
            print(exc_type, exc_value, traceback)

    def speed(self):
        self.network.sendrecv('speed?')

    def battery(self):
        self.network.sendrecv('battery?')

    def time(self):
        self.network.sendrecv('time?')
        
    def takeoff(self):
        self.network.sendrecv('takeoff')

    def land(self):
        self.network.sendrecv('land')

    def emergency(self):
        self.network.sendrecv('emergency')

    def stop(self):
        self.network.sendrecv('stop')

    def wait(self, seconds):
        time.sleep(seconds)

    def up(self, x):
        self.network.sendrecv('up {}'.format(int(x)))

    def down(self, x):
        self.network.sendrecv('down {}'.format(int(x)))

    def left(self, x):
        self.network.sendrecv('left {}'.format(int(x)))

    def right(self, x):
        self.network.sendrecv('right {}'.format(int(x)))

    def forward(self, x):
        self.network.sendrecv('forward {}'.format(int(x)))

    def back(self, x):
        self.network.sendrecv('back {}'.format(int(x)))

    def cw(self, degree):
        self.network.sendrecv('cw {}'.format(int(degree)))

    def ccw(self, degree):
        """ this function turns ccw """
        self.network.sendrecv('ccw {}'.format(int(degree)))
        
    def go(self, x, y, z, speed=40):
        self.network.sendrecv('go {} {} {} {}'.format(int(x), int(y), int(z), int(speed)))

    def rc(self, left_right, forward_backward, up_down, yaw):
        # send rc controls, don't wait for a response
        self.network.send('rc {} {} {} {}'.format(int(left_right), int(forward_backward),
                                                  int(up_down), int(yaw)))

    def align_to_target(self):
        """Align the drone to the first target seen"""
        if self.which == 'planner':
            return

        control = controller.DroneController(self)
        color_outer = 'fuschia'
        color_inner = 'blue'
        identifier = recognition.TargetIdentifier(color_outer, color_inner)
        aligner = fsm.AlignmentFSM(identifier, control)

        # pause the fast running VideoDisplayer thread since we want
        # to sync up frames received and the calculation and display
        # of target data
        self.displayer.pause() 
        while True:
            frame = self.video.get_frame()
            if aligner.on_frame(frame) is None:
                # succeeded in alignment
                break

            # send to VideoDisplayer a single frame that has overlay
            # of target data
            self.displayer.send_single_frame(frame)

        # resume fast running VideoDisplayer thread
        self.displayer.resume()

