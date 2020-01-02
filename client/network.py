import time
import threading
import socket

class NoNetwork:
    def __init__(self):
        self.command_history = []

    def close(self):
        pass
    
    def send(self, command):
        self.command_history.append(command)
        print('Send: {}'.format(command))

    def recv(self):
        print('Recv: ok')

    def sendrecv(self, command):
        self.send(command)
        self.recv()


class Network:
    def __init__(self, ip='192.168.10.1', port=8889):
        # socket settings for sending commands
        self.address = (ip, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))

        self.thread_keep_alive = threading.Thread(target=self.keep_alive)
        self.thread_keep_alive.daemon = True
        self.thread_keep_alive.start()

        self.command_history = []

    def close(self):
        self.socket.close()

    def keep_alive(self):
        """Send 'command' every 5 seconds to keep the drone from becoming inactive"""
        while True:
            self.send('command')
            time.sleep(5)

    def send(self, command):
        """Send command through socket"""
        ip, port = self.address
        self.socket.sendto(command.encode('utf-8'), self.address)
        print('Send: {}'.format(command))
        self.command_history.append(command)

    def recv(self):
        """Wait for a response from socket"""
        response, _ = self.socket.recvfrom(1024)
        print('Recv: {}'.format(response.decode('utf-8')))
            
    def sendrecv(self, command):
        """Send command through socket, wait for a response"""
        self.send(command)
        self.recv()


