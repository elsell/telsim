<<<<<<< HEAD
import socket
import time
import functools
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

# decorators for putting constraints on arguments passed to drone
# class methods
def force_integer_arguments(func):
    """Decorator to coerce all positional and keyword arguments to integers"""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(self, *map(int, args), **{k: int(v) for k, v in kwargs.items()})
    return wrapper

def ensure_valid_range(minimum, maximum):
    """Decorator to check if arguments are between the minimum and maximum values"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            valid_args = [x for x in args if minimum <= x <= maximum]
            if len(valid_args) == len(args):
                return func(self, *args, **kwargs)
            else:
                msg = 'Error in {}({}): argument must be between {} and {}'
                raise RuntimeError(msg.format(func.__name__, ', '.join(map(str, args)), minimum, maximum))
        return wrapper
    return decorator


# main class interface to drone
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
        """Prompt the drone to receive text commands at the beginning of a
with-statement"""
        self.network.sendrecv('command')
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        """Land the drone at the end of a with-statement or upon breaking out
of a with-statement when an error occurs

        """
        self.land()
        self.network.close()
        self.video.stop()

        if exc_type is not None:
            print(exc_value)
            return True

    def speed(self):
        """Ask for the current speed (cm/s)"""
        self.network.sendrecv('speed?')

    def battery(self):
        """Ask for the battery charge percentage"""
        self.network.sendrecv('battery?')

    def time(self):
        """Ask for the accumulated flight time (s)"""
        self.network.sendrecv('time?')
        
    def takeoff(self):
        """Tell the drone to takeoff and hover in place"""
        self.network.sendrecv('takeoff')

    def land(self):
        """Tell the drone to land"""
        self.network.sendrecv('land')

    def emergency(self):
        """Signal emergency shutoff of drone motors - the drone will
immediately fall to the ground!

        """
        self.network.sendrecv('emergency')

    def stop(self):
        """Tell the drone to stop moving and hover in place"""
        self.network.sendrecv('stop')

    @ensure_valid_range(0, 15)
    def wait(self, seconds):
        """Tell the drone to pause for the specified number of seconds. Valid
durations are between 0 and 15."""
        time.sleep(seconds)

    @force_integer_arguments
    @ensure_valid_range(20, 500)
    def up(self, x):
        """Tell the drone to move up x centimeters. Valid distances are
between 20 and 500."""
        self.network.sendrecv('up {:d}'.format(x))

    @force_integer_arguments
    @ensure_valid_range(20, 500)
    def down(self, x):
        """Tell the drone to move down x centimeters. Valid distances are
between 20 and 500."""
        self.network.sendrecv('down {:d}'.format(x))

    @force_integer_arguments
    @ensure_valid_range(20, 500)
    def left(self, x):
        """Tell the drone to move left x centimeters. Valid distances are
between 20 and 500."""
        self.network.sendrecv('left {:d}'.format(x))

    @force_integer_arguments
    @ensure_valid_range(20, 500)
    def right(self, x):
        """Tell the drone to move right x centimeters. Valid distances are
between 20 and 500."""
        self.network.sendrecv('right {:d}'.format(x))

    @force_integer_arguments
    @ensure_valid_range(20, 500)
    def forward(self, x):
        """Tell the drone to move forward x centimeters. Valid distances are
between 20 and 500."""
        self.network.sendrecv('forward {:d}'.format(x))

    @force_integer_arguments
    @ensure_valid_range(20, 500)
    def back(self, x):
        """Tell the drone to move back x centimeters. Valid distances are
between 20 and 500."""
        self.network.sendrecv('back {:d}'.format(x))

    @force_integer_arguments
    @ensure_valid_range(1, 360)
    def cw(self, x):
        """Tell the drone to rotate x degrees clockwise. Valid angles are
between 1 and 360."""
        self.network.sendrecv('cw {:d}'.format(x))

    @force_integer_arguments
    @ensure_valid_range(1, 360)
    def ccw(self, x):
        """Tell the drone to rotate x degrees counter-clockwise. Valid angles
are between 1 and 360."""
        self.network.sendrecv('ccw {:d}'.format(x))

    @force_integer_arguments
    @ensure_valid_range(-500, 500)
    def go(self, x, y, z, speed=40):
        """Tell the drone to move in 3D-space relative to its current
position. All units are in centimeters.

x : forward/back
y : right/left
z : up/down

Valid ranges for x, y, and z are -500 to 500, but at least one
direction must be outside the range of -20 and 20.

        """
        if -20 < x < 20 and -20 < y < 20 and -20 < z < 20:
            raise RuntimeError('Error in go({:d} {:d} {:d}): One of x, y, z must be outside range of -20 to 20'.format(x, y, z))
        else:
            self.network.sendrecv('go {:d} {:d} {:d} {:d}'.format(x, y, z, speed))

    @force_integer_arguments
    @ensure_valid_range(-100, 100)
    def rc(self, left_right, forward_backward, up_down, yaw):
        """Send radio control commands. The values correspond to joystick
positions with values between -100 and 100. To stop the drone moving,
you must call rc(0, 0, 0, 0) or stop().

        """
        # send rc controls, don't wait for a response
        self.network.send('rc {:d} {:d} {:d} {:d}'.format(left_right, forward_backward,
                                                          up_down, yaw))

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

>>>>>>> master
