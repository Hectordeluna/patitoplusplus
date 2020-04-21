from lark import Transformer, Tree

def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

class TransformerLark(Transformer):

    def __init__(self):
        self.functions = {}
        self.currType = ""
        self.currFunction = "___global___"
        self.currVar = ""

    def program_id(self, args):
        self.currFunction = "___global___"
        self.functions["___global___"] = { 'type': 'VOID', 'vars': {} }
        return Tree('program', args)

    def func_name(self, args):
        self.currFunction = args[0]
        if args[0] in self.functions:
          raise ValueError(args[0] + " already defined")
        else:
          self.functions[args[0]] = { 'type': self.currType, 'vars': {} }
        return Tree('func_name', args)
    
    def return_val(self, args):
        self.currType = args[0]
        return Tree('return_val', args)

    def tipo(self, defType):
        self.currType = defType[0]
        return Tree('tipo', defType)

    def decl_var(self, args):
        var = args[1]
        if var in self.functions[self.currFunction]['vars']:
            raise ValueError(var  + " already defined")
        else:
            self.functions[self.currFunction]['vars'][var] = { 'type': self.currType }
        return Tree('decl_var', args)      
    
    def lista_var(self, args):
        var = args[0]

        if var in self.functions[self.currFunction]['vars']:
            raise ValueError(var  + " already defined")
        else:
            self.functions[self.currFunction]['vars'][var] = { 'type': self.currType }
        return Tree('lista_var', args)

    def var(self, args):
        self.currVar = args[0]
        return Tree('var', args)      