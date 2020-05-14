class MemoriaVirtual:
	def __init__(self): 
		self.memVirtual = {"global": {"int": -1, "float": 999, "char": 1999, "bool": 2999}, "local": {"int": 3999, "float": 4999, "char": 5999, "bool": 6999}, "temp": {"int": 7999, "float": 8999, "char": 9999, "bool": 10999}}

	def getAddress(self, indice, scope):
		if scope != False:
			self.memVirtual[indice][scope] = self.memVirtual[indice][scope] + 1
			return self.memVirtual[indice][scope]
		else:
			return 69