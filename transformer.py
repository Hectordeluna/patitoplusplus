from lark import Transformer, Tree

currFunction = ""
currType = ""

def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

class TransformerLark(Transformer):
    from operator import add, sub, mul, truediv as div, neg

    def __init__(self):
        self.functions = {}

    def program_id(self, args):
        self.currFunction = "___global___"
        self.functions["___global___"] = { 'type': 'VOID', 'vars': {} }
        pretty(self.functions)
        return Tree('program', args)

    def func_name(self, args):
        self.currFunction = args[0]
        if args[0] in self.functions:
          raise ValueError(args[0] + " already defined")
        else:
          self.functions[args[0]] = { 'type': self.currType, 'vars': {} }
        pretty(self.functions)
        return Tree('func', args)
    
    def return_val(self, args):
        self.currType = args[0].type
        return Tree('return_val', args)

    # def args_func(self, args):
    #     if args[1] in self.functions[self.currFunction]['vars']:
    #       raise ValueError(args[1], " is alredy defined!")  
    #     else:
    #       self.functions[self.currFunction]['vars'][args[1]] = { 'type': args[0] }
    #       pretty(self.functions)
    #     return Tree('args_func', args)
