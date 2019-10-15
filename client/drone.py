import socket
import threading

class Drone:
	def __init__(self, ip='192.168.10.1', port=8889):
		"""Initialize connection
		Args: Takes the drone ip and port number to send commands to, 
			defaults to the Tello ip and the approprate port number for the
			startup command as detailed in the Tello documentation
		Result: binds a socket connection and sends the 'command' command 
			which enters the drone into dev mode"""
		self.address = (ip, port)
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.bind(('', port))
		self.send('command')
		# history list 
		# TODO: Determine if this should become its own class
		self.pos_hist = [(0,0,0)]
		# x, y, z rotation of drone
		self.rot = [0,0,0]

	# --with functions--
	def __enter__(self):
		self.takeoff()
		return self
        
	def __exit__(self, exc_type, exc_value, traceback):
		self.land()
		self.socket.close()

		if exc_type is not None:
			print(exc_type, exc_value, traceback)

	def send(self, command):
		""" Send command to the drone via the bound socket
		Args: takes a string ressebmling a command detailed in the Tello 
			drone documentation
		Result: sends the text command over UDP packets to the drone,
			 prints the command and response to console."""
		ip, port = self.address
		self.socket.sendto(command.encode('utf-8'), self.address)
		print('Send: {}'.format(command))
		# Hardcoded response port, see Tello documentation
		response, _ = self.socket.recvfrom(1024)
		print('Recv: {}'.format(response.decode('utf-8')))
 
	# --Drone Diagnostics--
	def speed(self):
		self.send('speed?')

	def battery(self):
		self.send('battery?')

	def time(self):
		self.send('time?')
 
	# --Macro drone commands--    
	def takeoff(self):
		self.send('takeoff')
		# TODO:	Placeholder starting position (0,0,0), 
		# Find if this is documented or if it can be calculated	

	def land(self):
		self.send('land')
		# Set final position to the current x, z, but set y to zero
		lpos = self.pos_hist[-1] 
		# TODO: determine if descent can be calculated
		self.pos_hist.append((lpos[0],0,lpos[2]));

	def emergency(self):
		self.send('emergency')

	# --Combined movement functions--
	def go(self, x_pos, y_pos, z_pos, speed):
		"""	Send relative coordinate based movement command
		Args: x, y, and z positions as either integers or floats
		Result: Sends the relative coordinate movement command with the
			given values"""	
		self.send('go {} {} {}'.format(int(x_pos), int(y_pos), int(z_pos), int(speed)))
		return

	# --Individual movement functions--
	def up(self, x):
		self.send('up {}'.format(int(x)))
		new_pos(0, 0, x)

	def down(self, x):
		self.send('down {}'.format(int(x)))
		new_pos(0, 0, -x)

	def left(self, x):
		self.send('left {}'.format(int(x)))
		new_pos(0, x, 0)

	def right(self, x):
		self.send('right {}'.format(int(x)))
		new_pos(0, -x, 0)

	def forward(self, x):
		self.send('forward {}'.format(int(x)))
		new_pos(x, 0, 0)

	def back(self, x):
		self.send('back {}'.format(int(x)))
		new_pos(-x, 0, 0)
	
	def cw(self, degree):
		self.send('cw {}'.format(int(degree)))
	
	def ccw(self, degree):
		self.send('ccw {}'.format(int(degree)))
	
	# --position history manipulators--

	# TODO: Make position updates take into account the rotation of the
	# 		drone
	def new_pos(self, dx, dy, dz):
		""" Naive relative position change. Take the current position 
			and add the change in relative position
		Args: delta-x, delta-y, delta-z
		Result: A new position is appended that is the last position
			plus the change in each direction"""
		cpos = self.pos_hist[-1]
		self.pos_hist.append((cpos[0] + int(dx), cpos[1] + int(dy), cpos[2] + int(dz)))	
