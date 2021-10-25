# Author: Sam Bradshaw

class CLIOption:
	""" class for Command Line Interface Options """

	def __init__(self, long, short, description, arg_name=None):
		self.long = long
		self.short = short
		self.description = description
		self.arg_name = arg_name # None if option does not require a value

	def __eq__(self, other):
		""" Returns True if equal to either the long or short option """
		return other in (self.short, self.long)

	def __hash__(self):
		return hash(self.long)

