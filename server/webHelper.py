class Entscheider():
	""" Entscheider Klasse zum dynamischen Entscheiden """

	def __init__(self, trigger_cmd: str, give_func):
		self.trigger = trigger_cmd
		self.exefunction = give_func
	
	def ispossible(self, cmd : str):
		if cmd ==self.trigger:
			return True
		else:
			return False
	
	def run2(self,response,modeSelect):
		self.exefunction(response,modeSelect)
	
	def run0(self):
		self.exefunction()

	def run1(self, cmd):
		self.exefunction(cmd)