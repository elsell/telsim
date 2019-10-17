class HistoryL:
	"""	A class to handle a list of absolute positions and a variable 
		direction for relative movement coordinates"""
	def __init__(self):
		self.rot = 0.0 
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
		"""	Adds a new position that is relative to the previous given the
			passed deltas"""
		cur = self.hist[-1]
		self.append(cur[0] + int(dx), cur[1] + int(dy), cur[2] + int(dz))
