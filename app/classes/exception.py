class ModuleException(Exception):
	def __init__(self, text, *args):
		super().__init__(text, *args)
		self.text = text