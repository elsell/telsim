# Drone status tracker
import threading
from datetime import datetime
from network import Listener
from drone import Drone

# A very generic number regular expression
	# probably missing a few cases
number_re = "(-+)?[0-9]+(\.[0-9]+)?(e(-+)?[0-9])"

# Drone state components
components = [
	'pitch',
	'roll', 
	'yaw', 
	'vgx', 
	'vgy', 
	'vgz', 
	'templ', 
	'temph',
	'tof',
	'h',
	'bat',
	'baro',
	'time',
	'agx',
	'agy',
	'agz'
]

# Drone status tracker
class Status (threading.Thread):
	# Arguments:
	#	UDP connection for polling the drone
	#	Interval between listening
	def __init__(self, poller, interval = .05):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.interval = interval
		# Add all component variables
		for comp in components:
			setattr(self, comp, None)
		self.running = True	# Thread kill variable

		# Create a status listener without the daemon
		self.listener = Network()
		self.pos_hist = [(0,0,0)] 	# positional history
		return

	def kill(self):
		self.running = False
		return self.pos_hist	# return position history
	
	def run(self):
		# Time in seconds, precise to milliseconds platform permitting
		prev_t = datetime.now()	
		while self.running:
			cur_t = datetime.now()
			dt = cur_t - prev_t
			if (dt.total_seconds() > self.interval):
				self.getState()	
				prev_t = cur_t
	
	def getState(self):
		state = listener.recv()
		if not state: print("Error, no state message received")
		else: self.decompose(state)
			
	def decompose(self, str(state)):
		for comp in components:
			state = replace(comp, '')

