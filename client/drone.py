import socket
import time

class Drone:

	"""Class for sending network commands to the Tello EDU drone"""
	def __init__(self, ip='192.168.10.1', port=8889):
		"""Initialize connection
		Args: Takes the drone ip and port number to send commands to, 
			defaults to the Tello ip and the approprate port number for the
			startup command as detailed in the Tello documentation
		Result: binds a socket connection and sends the 'command' command 
			which enters the drone into dev mode"""
        # socket settings for sending commands
		self.address = (ip, port)
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.bind(('', port))
		self.send('command')

		# Create the 'running' thread to keep the drone awake
		self.running = threading.Thread(target=keep_awake, args=(self, 5,))
		self.running.start()		

		# history list
		self.pos_hist = HistoryL() 

	# --with functions--
	def __enter__(self):
		self.takeoff()
		return self
        
	def __exit__(self, exc_type, exc_value, traceback):
		self.land()
		self.running.kill()
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
		# TODO:	Placeholder starting position, 
		# Find if this is documented or if it can be calculated	
		self.pos_hist.append(0,25,0)

	def land(self):
		self.send('land')
		# Set final position to the current x, z, but set y to zero
		lpos = self.pos_hist.last() 
		# TODO: determine if descent can be calculated
		self.pos_hist.append(lpos[0],0,lpos[2]);

	def emergency(self):
		self.send('emergency')

	# --Combined movement functions--
	def go(self, x_pos, y_pos, z_pos, speed):
		"""	Send relative coordinate based movement command
		Args: x, y, and z positions as either integers or floats
		Result: Sends the relative coordinate movement command with the
			given values"""	
		self.send('go {} {} {}'.format(int(x_pos), int(y_pos), int(z_pos), int(speed)))	
		self.pos_hist.rel_pos(x_pos, y_pos, z_pos)

	# --Individual movement functions--
	# A simple right hand rule is used for finding axis that the drone
	# moves along, x is the index finger pointed straight forward from 
	# the drone, y is a finger that lays horizontally, points left of x,
	# and is perpendicular to x, and z is the thumb pointing up, 
	# perpendicular to x and y
	def up(self, x):
		self.send('up {}'.format(int(x)))
		self.pos_hist.rel_pos(0, 0, x)

	def down(self, x):
		self.send('down {}'.format(int(x)))
		self.pos_hist.rel_pos(0, 0, -x)

	def left(self, x):
		self.send('left {}'.format(int(x)))
		self.pos_hist.rel_pos(0, x, 0)

	def right(self, x):
		self.send('right {}'.format(int(x)))
		self.pos_hist.rel_pos(0, -x, 0)

	def forward(self, x):
		self.send('forward {}'.format(int(x)))
		self.pos_hist.rel_pos(x, 0, 0)

	def back(self, x):
		self.send('back {}'.format(int(x)))
		self.pos_hist.rel_pos(-x, 0, 0)
	
	def cw(self, degree):
		self.send('cw {}'.format(int(degree)))
		self.pos_hist.rot += degree
	
	def ccw(self, degree):
		self.send('ccw {}'.format(int(degree)))
		self.pos_hist.rot -= degree
	
	def keep_awake(drone, interval):
		"""Function to keep a drone awake"""
		while (True):
			drone.send('command')
			time.sleep(interval)	
