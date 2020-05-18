class MemoriaVirtual:
	def __init__(self): 
		self.memVirtual = {"global": {"int": -1, "float": 999, "string": 1999, "bool": 2999}, "local": {"int": 3999, "float": 4999, "string": 5999, "bool": 6999}, "temp": {"int": 7999, "float": 8999, "string": 9999, "bool": 10999}, "cte": {"int": 11999, "float": 12999, "string": 13999, "bool": 14999}}

	def getAddress(self, indice, scope):
		if scope != False:
			self.memVirtual[indice][scope] = self.memVirtual[indice][scope] + 1
			return self.memVirtual[indice][scope]

class Memory:
	def __init__(self, inicial):
		self.arrInt = []
		self.arrFloat = []
		self.arrChar = []
		self.arrBool = []
		self.valInicial = inicial

	def setVar(self, address, variable):
		address = address - self.valInicial

		if address < 1000:
			self.arrInt.append(variable)
		elif address >= 1000 and address < 2000:
			self.arrFloat.append(variable)
		elif address >= 2000 and address < 3000:
			self.arrChar.append(variable)
		elif address >= 3000:
			self.arrBool.append(variable)

	def getVar(self, address):
		address = address - self.valInicial
		
		if address < 1000:
			return self.arrInt[address]
		elif address >= 1000 and address < 2000:
			return self.arrFloat[address - 1000]
		elif address >= 2000 and address < 3000:
			return self.arrChar[address - 2000]
		elif address >= 3000:
			return self.arrBool[address - 3000]
		else:
			return False