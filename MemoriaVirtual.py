# Valor de pointer 
pointerMin = 160000*100000000000000
# Crear dirs para semantica
class MemoriaVirtual:
	def __init__(self): 
		self.memVirtual = {
			"global": {"int": -1, "float": 999, "char": 1999, "bool": 2999}, 
			"local": {"int": 3999, "float": 4999, "char": 5999, "bool": 6999}, 
			"temp": {"int": 7999, "float": 8999, "char": 9999, "bool": 10999}, 
			"cte": {"int": 11999, "float": 12999, "char": 13999, "bool": 14999},
			"pointer": {"int": pointerMin - 1, "float": pointerMin - 1 + 1000, "char": pointerMin - 1 + 2000, "bool": pointerMin - 1 + 3000}}

	def getAddress(self, indice, scope):
		if scope != False:
			self.memVirtual[indice][scope] = self.memVirtual[indice][scope] + 1
			return self.memVirtual[indice][scope]

	def setNextAddress(self, indice, scope, value):
		if scope != False:
			self.memVirtual[indice][scope] = self.memVirtual[indice][scope] + value - 1

class Memory:
	# Se hace init con la memoria vacia
	def __init__(self, inicial):
		self.arrInt = {}
		self.arrFloat = {}
		self.arrChar = {}
		self.arrBool = {}
		self.valInicial = inicial

	def setVar(self, address, variable):
		address = address - self.valInicial
		if address >= 0 and address < 1000:
			self.arrInt[address] = int(variable)
		elif address >= 1000 and address < 2000:
			self.arrFloat[address - 1000] = float(variable)
		elif address >= 2000 and address < 3000:
			self.arrChar[address - 2000] = variable
		elif address >= 3000 and address < 4000:
			self.arrBool[address - 3000] = variable
		else:
			return False

	def getVar(self, address):
		address = address - self.valInicial
		if address >= 0 and address < 1000:
			if address in self.arrInt:
				return int(self.arrInt[address])
			else:
				return -1
		elif address >= 1000 and address < 2000:
			address = address - 1000
			if address in self.arrFloat:
				return float(self.arrFloat[address])
			else:
				return -1
		elif address >= 2000 and address < 3000:
			return self.arrChar[address - 2000]
		elif address >= 3000 and address < 4000:
			return self.arrBool[address - 3000]
		else:
			return False

	def printInt(self):
		print(self.arrInt)

	def printBool(self):
		print(self.arrBool)

	def printFloat(self):
		print(self.arrFloat)

	def clearMemory(self):
		self.arrInt = {}
		self.arrFloat = {}
		self.arrChar = {}
		self.arrBool = {}