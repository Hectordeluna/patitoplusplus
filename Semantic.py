class Semantic:
	def __init__(self):
		self.table = [[]]

	def result(self, left, right, op):
		if op == "+" or op == "-":
			if left == "float" and right == "int":
				return "float"
			elif left == "int" and right == "float":
				return "float"
			elif left == "int" and right == "int":
				return "int"
			elif left == "float" and right == "float":
				return "float"
			elif left == "char" and right == "char":
				return "char"
			else:
				return False
		elif op == "*":
			if left == "float" and right == "int":
				return "float"
			elif left == "int" and right == "float":
				return "float"
			elif left == "int" and right == "int":
				return "int"
			elif left == "float" and right == "float":
				return "float"
			elif left == "char" and right == "int":
				return "char"
			elif left == "int" and right == "char":
				return "char"
			else:
				return False
		elif op == "/":
			if left == "float" and right == "int":
				return "float"
			elif left == "int" and right == "float":
				return "float"
			elif left == "int" and right == "int":
				return "float"
			elif left == "float" and right == "float":
				return "float"
			else:
				return False
		elif op == ">" or op == "<" or op == "==":
			if left == "int" and right == "int":
				return "bool"
			elif left == "int" and right == "float":
				return "bool"
			elif left == "float" and right == "int":
				return "bool"
			else:
				return False
		elif op == "AND" or op == "OR":
			if left == "bool" and right == "bool":
				return "bool"
			else:
				return False
		elif op == "$":
			if left == "float" and right == "float":
				return "float"
			elif left == "int" and right == "int":
				return "float"
			else:
				return False
		elif op == "?":
			if left == "float" and right == "float":
				return "float"
			elif left == "int" and right == "int":
				return "float"
			else:
				return False
		elif op == "¡":
			if left == "float" and right == "float":
				return "float"
			elif left == "int" and right == "int":
				return "int"
			else:
				return False
		elif op == "return":
			return left == right
		elif op == "print":
			return True