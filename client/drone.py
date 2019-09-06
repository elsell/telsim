import socket
import threading

class Drone:
    def __init__(self, ip='192.168.10.1', port=8889):
        self.address = (ip, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))
        self.send('command')

    def __enter__(self):
        self.takeoff()
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
        self.send('ccw {}'.format(int(degree)))
        
    
