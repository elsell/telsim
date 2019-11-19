# x - forward/backward, y - left/right, z - up/down

import * from math

class HistoryL:
	"""	A class to handle a list of absolute positions and a variable 
		direction for relative movement coordinates"""
	def __init__(self):
		self.rot = 0.0
		# {	xcos(t)-ysin(t),
		# 	xsin(t)+ycos(t) }
		# Rotation matrix, calculated when a new rotation is set
		self.rotM = [1,0,1,0] 
		self.hist = []

	def last(self):
		try:
			return self.hist[-1]
		except IndexError:
			print("Exception Occured: IndexError in HistoryL")

	def append(self, x, y, z):
		"""Appends a position as passed"""
		self.hist.append((x,y,z))

	def rel_pos(self, dx, dy, dz):
		"""	Adds a new position that is relative to the previous given 
			the passed deltas"""
		cur = self.hist[-1]
		# dx and dy when rotation is taken into account
		rotx = int(dx) * rotM[0] - int(dy) * rotM[1]
		roty = int(dy) * rotM[2] + int(dy) * rotM[3]
		self.hist.append(cur[0] + rotx, cur[1] + roty, cur[2] + dz)

	def rotate(self, r):
		self.rot += r
		# Convert to radians
		rad = self.rot / math.pi
		self.rotM[0] = math.cos(rad)
		self.rotM[1] = math.sin(rad)
		self.rotM[2] = self.rotM[1]
		self.rotM[3] = self.rotM[0]
