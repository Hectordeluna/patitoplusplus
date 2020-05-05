from lark import Transformer, Tree
from Quadruple import *
from Stack import *
from Semantic import *

stackOp = Stack(False)
stackJumps = Stack(False)
stackVar = Stack(False)
stackType = Stack(False)
semTable = Semantic()
ops = {
    "+": (lambda a,b: a+b), 
    "-": (lambda a,b: a-b), 
    "*": (lambda a,b: a*b), 
    "/": (lambda a,b: a/b), 
    "AND": (lambda a,b: a and b), 
    "OR": (lambda a,b: a or b), 
    ">": (lambda a,b: a > b),
    ">=": (lambda a,b: a >= b),
    "==": (lambda a,b: a == b),
    "<": (lambda a,b: a < b),
    "!=": (lambda a,b: a != b),
    "<=": (lambda a,b: a <= b)
}
t_num = 0
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
        self.quadruples = []

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
        stackVar.push(args[0].value)
        stackType.push(self.findbyType(args[0].value))
        return Tree('var', args)     

    def integer(self, args):
        stackVar.push(int(args[0].value))
        stackType.push('int')
        return Tree('integer', args)  

    def number(self, args):
        stackVar.push(int(args[0].value))
        stackType.push('int')
        return Tree('integer', args) 

    def times_divide(self, args):
        stackOp.push(args[0].value)
        return Tree('times', args)  

    def plus_minus(self, args):
        stackOp.push(args[0].value)
        return Tree('plus', args)  

    def assign(self, args):
        stackOp.push("=")
        return Tree('equal', args)

    def op4(self, args):
        stackOp.push("AND")
        return Tree('op4', args)

    def op3(self, args):
        stackOp.push("OR")
        return Tree('op3', args)

    def op5(self, args):
        stackOp.push(args[0].value)
        return Tree('op5', args)

    def while_key(self, args):
        stackJumps.push(len(self.quadruples))
        return Tree('while_key', args)

    def for_key(self, args):
        stackJumps.push(len(self.quadruples))
        return Tree('for_key', args)

    def end_exp_log(self, args):
        if stackType.size() > 0:
            exp_type = stackType.pop()
            if exp_type != "bool":
                res = stackVar.pop()
                quad = Quadruple("GotoF", res, None, None)
                self.quadruples.append(quad.getQuad())
                stackJumps.push(len(self.quadruples) - 1)
            else:
                print("error")
        return Tree('end_exp_log', args)

    def fin_bloque(self, args):
        if stackJumps.size() > 0:
            end = stackJumps.pop()
            if stackJumps.size() > 0:
                ret = stackJumps.pop()
                quad = Quadruple("Goto", ret, None, None)
                self.quadruples.append(quad.getQuad()) 
            self.quadruples[end][3] = len(self.quadruples)
        return Tree('fin_bloque', args)

    def if_key(self, args):
        if stackType.size() > 0:
            exp_type = stackType.pop()
            if exp_type != "bool":
                result = stackVar.pop()
                quad = Quadruple("GotoF", result, None, None)
                self.quadruples.append(quad.getQuad())
                stackJumps.push(len(self.quadruples) - 1)
            else:
                print("error")
        return Tree('if_key', args)

    def else_key(self, args):
        if stackJumps.size() > 0:
            res = stackVar.pop()
            quad = Quadruple("Goto", res, None, None)
            self.quadruples.append(quad.getQuad())
            stackJumps.push(len(self.quadruples) - 1)
        else:
            print("error")
        return Tree('else_key', args)

    def print_exp(self, args):
        stackOp.push("print")
        return Tree('print_exp', args)

    def end_print(self, args):
        if stackOp.size() > 0:
            top = stackOp.peek()
            if top == "print":
                result = stackVar.pop()
                operator = stackOp.pop()
                quad = Quadruple(operator, None, None, result)
                self.quadruples.append(quad.getQuad())     
        return Tree('end_print', args)

    def exp_comp(self, args):
        if stackOp.size() > 0:
            top = stackOp.peek()
            if top == ">" or top == "<" or top == "!=" or top == "==" or top == "<=" or top == ">=":
                right_operand = stackVar.pop()
                right_type = stackType.pop()
                left_operand = stackVar.pop()
                left_type = stackType.pop()
                operator = stackOp.pop()
                result_type = semTable.result(left_type, right_type, operator)
                if result_type != False:
                    result = ops[operator](left_operand, right_operand)
                    quad = Quadruple(operator, left_operand, right_operand, result)
                    self.quadruples.append(quad.getQuad())
                    stackVar.push(result)
                    stackType.push(result_type)
                else:
                    print("error")
        return Tree('exp_comp', args)

    def exp_log_or(self, args):
        if stackOp.size() > 0:
            top = stackOp.peek()
            if top == "OR":
                right_operand = stackVar.pop()
                right_type = stackType.pop()
                left_operand = stackVar.pop()
                left_type = stackType.pop()
                operator = stackOp.pop()
                result_type = semTable.result(left_type, right_type, operator)
                if result_type != False:
                    result = ops[operator](left_operand, right_operand)
                    quad = Quadruple(operator, left_operand, right_operand, result)
                    self.quadruples.append(quad.getQuad())
                    stackVar.push(result)
                    stackType.push(result_type)
                else:
                    print("error")
        return ('exp_log_or', args)     

    def exp_log_and(self, args):
        if stackOp.size() > 0:
            top = stackOp.peek()
            if top == "AND":
                right_operand = stackVar.pop()
                right_type = stackType.pop()
                left_operand = stackVar.pop()
                left_type = stackType.pop()
                operator = stackOp.pop()
                result_type = semTable.result(left_type, right_type, operator)
                if result_type != False:
                    result = ops[operator](left_operand, right_operand)
                    quad = Quadruple(operator, left_operand, right_operand, result)
                    self.quadruples.append(quad.getQuad())
                    stackVar.push(result)
                    stackType.push(result_type)
                else:
                    print("error")
        return ('exp_log_or', args)      

    def termino(self, args):
        if stackOp.size() > 0:
            top = stackOp.peek()
            if top == "+" or top == "-":
                right_operand = stackVar.pop()
                right_type = stackType.pop()
                left_operand = stackVar.pop()
                left_type = stackType.pop()
                operator = stackOp.pop()
                result_type = semTable.result(left_type, right_type, operator)
                if result_type != False:
                    if result_type == "int":
                        left_typed = int(left_operand)
                        right_typed = int(right_operand)
                    elif result_type == "float":
                        left_typed = float(left_operand)
                        right_typed = float(right_operand)
                    result = ops[operator](left_typed, right_typed)
                    quad = Quadruple(operator, left_operand, right_operand, result)
                    self.quadruples.append(quad.getQuad())
                    stackVar.push(result)
                    stackType.push(result_type)
                else:
                    print("error")
        return ('termino', args)


    def factor(self, args):
        if stackOp.size() > 0:
            top = stackOp.peek()
            if top == "*" or top == "/":
                right_operand = stackVar.pop()
                right_type = stackType.pop()
                left_operand = stackVar.pop()
                left_type = stackType.pop()
                operator = stackOp.pop()
                result_type = semTable.result(left_type, right_type, operator)
                if result_type != False:
                    if result_type == "int":
                        left_typed = int(left_operand)
                        right_typed = int(right_operand)
                    elif result_type == "float":
                        left_typed = float(left_operand)
                        right_typed = float(right_operand)
                    result = ops[operator](left_typed, right_typed)
                    quad = Quadruple(operator, left_operand, right_operand, result)
                    self.quadruples.append(quad.getQuad())
                    stackVar.push(result)
                    stackType.push(result_type)
                else:
                    print("error")
        return ('factor', args)
           

    def ended(self, args):
        if stackOp.size() > 0:
            top = stackOp.peek()
            if top == "=":
                right_operand = stackVar.pop()
                right_type = stackType.pop()
                left_operand = stackVar.pop()
                left_type = stackType.pop()
                operator = stackOp.pop()
                result_type = semTable.result(left_type, right_type, operator)
                if result_type != False:
                    quad = Quadruple(operator, right_operand, None, left_operand)
                    self.quadruples.append(quad.getQuad())
                else:
                    print("error")

    def findbyType(self, var):
        if var in self.functions[self.currFunction]['vars']:
            return self.functions[self.currFunction]['vars'][var]['type'].value
        elif var in self.functions["___global___"]['vars']:
            return self.functions["___global___"]['vars'][var]['type'].value
        return False

    def lparen(self, args):
        stackOp.push(args[0].value)
        return Tree("lparen", args)

    def rparen(self, args):
        stackOp.pop()
        return Tree("rparen", args)