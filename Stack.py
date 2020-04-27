class Stack:
	def __init__(self, toPrint):
		self.toPrint = toPrint
		self.items = []
	
	def isEmpty(self):
	  return self.items == []

	def push(self, item):
		self.items.insert(0,item)
		if self.toPrint:
			print("Push", self.items)

	def pop(self):
		poped = self.items.pop(0)
		if self.toPrint:
			print("Pop", self.items)
		return poped

	def peek(self):
		if self.toPrint:
			print("Peek", self.items)
		return self.items[0]

	def size(self):
	    return len(self.items)	

	def print(self):
		print(self.items)