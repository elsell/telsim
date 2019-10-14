import time
import socket
import threading
import sys
sys.path.append('.')
import numpy as np
import cv2
import libh264decoder

class Drone:
    """Class for sending network commands to the Tello EDU drone"""
    def __init__(self, ip='192.168.10.1', port=8889):
        # socket settings for sending commands
        self.address = (ip, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))

        # socket settings for the video stream
        self.socket_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_video.bind(('0.0.0.0', 11111))
        libh264decoder.disable_logging()
        self.decoder = libh264decoder.H264Decoder()
        self.frame = None # current video frame stored as a numpy array of RGB

        self.thread_video = threading.Thread(target=self.recv_video)
        self.thread_video.daemon = True
        self.thread_video.start()

        self.send('command')
        self.send('streamon')

    def __enter__(self):
        self.send('command')
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.land()
        self.socket.close()

        if exc_type is not None:
            print(exc_type, exc_value, traceback)
        
    def send(self, command):
        ip, port = self.address
        self.socket.sendto(command.encode('utf-8'), self.address)
        print('Send: {}'.format(command))
        response, _ = self.socket.recvfrom(1024)
        print('Recv: {}'.format(response.decode('utf-8')))

    def send_udp(self, command):
        ip, port = self.address
        self.socket.sendto(command.encode('utf-8'), self.address)
        print('Send: {}'.format(command))

    def recv_video(self):
        packet_data = b''
        while True:
            try:
                data, ip = self.socket_video.recvfrom(2048)
                packet_data += data
                if len(data) != 1460:
                    for frame in self.decode_h264(packet_data):
                        self.frame = frame
                    packet_data = b''

            except socket.error as err:
                print("Caught exception socket.error : {}".format(err))

    def decode_h264(self, packet_data):
        frame_list = []
        frames = self.decoder.decode(packet_data)

        for framedata in frames:
            (frame, width, height, linesize) = framedata
            if frame is not None:
                frame = np.frombuffer(frame, dtype=np.ubyte, count=len(frame))
                frame = (frame.reshape((height, linesize//3, 3)))
                frame = frame[:, :width, :]
                frame_list.append(frame)

        return frame_list

    def get_frame(self):
        while self.frame is None:
            time.sleep(0.1)
        return cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
    
    def speed(self):
        self.send('speed?')

    def battery(self):
        self.send('battery?')

    def time(self):
        self.send('time?')
        
    def takeoff(self):
        self.send('takeoff')

    def land(self):
        self.send('land')

    def emergency(self):
        self.send('emergency')

    def up(self, x):
        self.send('up {}'.format(int(x)))

    def down(self, x):
        self.send('down {}'.format(int(x)))

    def left(self, x):
        self.send('left {}'.format(int(x)))

    def right(self, x):
        self.send('right {}'.format(int(x)))

    def forward(self, x):
        self.send('forward {}'.format(int(x)))

    def back(self, x):
        self.send('back {}'.format(int(x)))

    def cw(self, degree):
        self.send('cw {}'.format(int(degree)))

    def ccw(self, degree):
        """ this function turns ccw """
        self.send('ccw {}'.format(int(degree)))
        
    def go(self, x, y, z, speed=100):
        self.send('go {} {} {} {}'.format(int(x), int(y), int(z), int(speed)))

    def rc(self, left_right, forward_backward, up_down, yaw):
        self.send_udp('rc {} {} {} {}'.format(int(left_right), int(forward_backward),
                                              int(up_down), int(yaw)))
        
class WebcamDrone:
    """Simulated drone for testing rc controls. Uses webcam for video stream."""
    def __init__(self):
        self.frame = None
        
        self.thread_video = threading.Thread(target=self.recv_video)
        self.thread_video.start()
        self.capturing = True

        self.command_num = 0

    def get_frame(self):
        while self.frame is None:
            time.sleep(0.1)

        return self.frame
        
    def recv_video(self):
        self.capture = cv2.VideoCapture(0)
        
        while self.capturing:
            _, frame = self.capture.read()
            self.frame = frame

        self.capture.release()

    def battery(self):
        print('battery')

    def takeoff(self):
        print('takeoff')

    def land(self):
        self.capturing = False
        print('land')
        
    def rc(self, a, b, c, d):
        self.command_num += 1
        print(self.command_num, ': rc {} {} {} {}'.format(a, b, c, d))
