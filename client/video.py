import time
import threading
import multiprocessing
import socket
import sys
sys.path.append('.') # to find module libh264decoder
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import libh264decoder
import cv2
plt.rcParams['toolbar'] = 'None'

class Webcam:
    def __init__(self):
        self.frame = None
        self.capturing = True
        self.thread_video = threading.Thread(target=self.recv_video)
        self.thread_video.start()

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

    def stop(self):
        self.capturing = False


class Video:
    def __init__(self, ip='0.0.0.0', port=11111):
        # socket settings for the video stream
        self.socket_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_video.bind(('0.0.0.0', 11111))
        libh264decoder.disable_logging()
        self.decoder = libh264decoder.H264Decoder()
        self.frame = None # current video frame stored as a numpy array of RGB

        self.capturing = True
        self.thread_video = threading.Thread(target=self.recv_video)
        self.thread_video.daemon = True
        self.thread_video.start()

    def recv_video(self):
        packet_data = b''
        while self.capturing:
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

    def stop(self):
        self.capturing = False


class VideoDisplayer:
    def __init__(self, video):
        self.video = video
        self.recv_pipe, self.send_pipe = multiprocessing.Pipe(duplex=False)
        self.receiver = multiprocessing.Process(target=self.recv,
                                                daemon=True)
        self.receiver.start()

        self.paused = False
        self.sender = threading.Thread(target=self.send_frames, daemon=True)
        self.sender.start()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False
        
    def send_single_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.send_pipe.send(frame)        
        
    def send_frames(self):
        while not self.paused:
            self.send_single_frame(self.video.get_frame())
        
    def recv_frame(self):
        return self.recv_pipe.recv()
    
    def recv(self):
        fig = plt.figure()
        fig.canvas.set_window_title('VideoStream')
        self.im = plt.imshow(self.recv_frame(), animated=True)
        fig.gca().axis('off')
        fig.tight_layout(pad=0)
        anim = animation.FuncAnimation(fig, self.update, interval=25, blit=True)
        plt.show()
        
    def update(self, *args):
        frame = self.recv_frame()
        self.im.set_array(frame)
        return self.im,

        
