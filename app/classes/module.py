class ModuleException(Exception):
	def __init__(self, obj=None, *args):
		super().__init__(obj,*args)
		self.obj = obj

class Module:
    def __init__(self, blueprint, url_prefix: str, name: str):
        self.blueprint = blueprint
        self.url_prefix = url_prefix
        self.name = name