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