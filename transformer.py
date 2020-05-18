from lark import Transformer, Tree
from Quadruple import *
from Stack import *
from Semantic import *
from MemoriaVirtual import *

memVirtual = MemoriaVirtual()
stackOp = Stack(False)
stackJumps = Stack(False)
stackVar = Stack(False)
stackType = Stack(False)
semTable = Semantic()
currParams = Stack(False)
quadruples = []
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

def prettyList(d, indent=0):
    count = 0
    for value in d:
        print(str(count) + " " + '\t' * indent + str(value))
        count = count + 1

def genQuadOpLog(cond):
    if stackOp.size() > 0:
        top = stackOp.peek()
        if top in cond:
            right_operand = stackVar.pop()
            right_type = stackType.pop()
            left_operand = stackVar.pop()
            left_type = stackType.pop()
            operator = stackOp.pop()
            result_type = semTable.result(left_type, right_type, operator)
            if result_type != False:
                # result = ops[operator](left_operand, right_operand)
                posMemVirtual = memVirtual.getAddress('temp', result_type) # falta cambiar a que sea segun el tipo
                quad = Quadruple(operator, left_operand, right_operand, posMemVirtual)
                quadruples.append(quad.getQuad())
                stackVar.push(posMemVirtual)
                stackType.push(result_type)
            else:
                print("error exp_log_or")

def genQuadOpExp(cond):
    if stackOp.size() > 0:
        top = stackOp.peek()
        if top in cond:
            right_operand = stackVar.pop()
            right_type = stackType.pop()
            left_operand = stackVar.pop()
            left_type = stackType.pop()
            operator = stackOp.pop()
            result_type = semTable.result(left_type, right_type, operator)
            if result_type != False:
                # result = ops[operator](left_typed, right_typed)
                posMemVirtual = memVirtual.getAddress('temp', result_type) # falta cambiar a que sea segun el tipo
                quad = Quadruple(operator, left_operand, right_operand, posMemVirtual)
                quadruples.append(quad.getQuad())
                stackVar.push(posMemVirtual)
                stackType.push(result_type)
            else:
                print("error termino")

def genQuadEndExp(cond):
    if stackOp.size() > 0:
        top = stackOp.peek()
        if top in cond:
            right_operand = stackVar.pop()
            right_type = stackType.pop()
            operator = stackOp.pop()
            if stackVar.size() > 0:
                left_operand = stackVar.pop()
            else:
                left_operand = None
            left_type = stackType.pop()
            result_type = semTable.result(left_type, right_type, operator)
            if result_type != False:
                quad = Quadruple(operator, left_operand, None, right_operand)
                quadruples.append(quad.getQuad())
            else:
                print("error")

def genQuadGoto(): 
    if stackJumps.size() > 0:
        end = stackJumps.pop()
        if stackJumps.size() > 0:
            ret = stackJumps.pop()
            quadruples[ret][3] = len(quadruples)
            quad = Quadruple("Goto", None, None, ret)
            quadruples.append(quad.getQuad()) 
        quadruples[end][3] = len(quadruples)

class TransformerLark(Transformer):

    def __init__(self):
        self.functions = {}
        self.currType = ""
        self.currFunction = "___global___"
        self.currVar = ""
        self.currFuncCounter = 0

    def program_id(self, args):
        self.currFunction = "___global___"
        self.functions["___global___"] = { 'type': 'VOID', 'vars': {} }
        self.functions["___cte___"] = { 'type': 'VOID', 'vars': {} }
        return Tree('program', args)

    def func_name(self, args):
        self.currFunction = args[0].value
        currParams.clean()
        self.currFuncCounter = 0
        if args[0] in self.functions:
          raise ValueError(args[0] + " already defined")
        else:
          self.functions[args[0]] = { 'type': self.currType, 'vars': {}, 'params': {} }
        return Tree('func_name', args)

    def end_func_decl(self, args):
        self.functions[self.currFunction]['params_size'] = self.currFuncCounter
        return Tree('end_func_decl', args)

    def args_func(self, args):
        if currParams.size() > 0:
            top = currParams.pop()
            var = top["var"]
            typ = top["type"].value
            self.functions[self.currFunction]['params'][self.currFuncCounter] = { 'var': var, 'type': typ }
            self.currFuncCounter = self.currFuncCounter + 1

    def func_bloque(self, args):
        self.functions[self.currFunction]['vars'] = {}
        quad = Quadruple("ENDFunc", None, None, None)
        quadruples.append(quad.getQuad())
        # Falta el numbero de Ts usadas
        

    def func_vars(self, args):
        self.functions[self.currFunction]['local_size'] = abs(len(self.functions[self.currFunction]['vars']) - self.functions[self.currFunction]['params_size'])
        self.functions[self.currFunction]['quad_count'] = len(quadruples)
        return Tree('end_func_decl', args)     

    def call_name(self, args):
        if args[0].value not in self.functions:
            print("ERROR func not found")
        return Tree('call_name', args)  

    def gen_era(self, args):
        quad = Quadruple("ERA", self.functions[self.currFunction]['params_size'], None, None)
        quadruples.append(quad.getQuad())
        self.currFuncCounter = 0
        return Tree('gen_era', args)

    def call_var(self, args):
        if stackVar.size() > 0:
            argument = stackVar.pop()
            typ = stackType.pop()
            param = self.functions[self.currFunction]['params'][self.currFuncCounter]
            if param["type"] == typ:
                quad = Quadruple("PARAMETER", argument, self.currFuncCounter + 1, None) 
                self.currFuncCounter = self.currFuncCounter + 1
                quadruples.append(quad.getQuad())
            else:
                print("TYPE mismatch")
        return Tree('call_var', args)
    
    def call_end(self, args):
        if self.currFuncCounter < len(self.functions[self.currFunction]['params']):
            print("error not enough parameters")
        else:
            quad = Quadruple("GOSUB", self.currFunction, None, self.functions[self.currFunction]['quad_count']) 
            quadruples.append(quad.getQuad())

    def return_val(self, args):
        self.currType = args[0].value
        return Tree('return_val', args)

    def tipo(self, defType):
        self.currType = defType[0]
        return Tree('tipo', defType)

    def saveVar(self, var):
        if var in self.functions[self.currFunction]['vars']:
            raise ValueError(var  + " already defined")
        else:
            if self.currFunction == "___global___":
                scope = "global"
            else:
                scope = "local"
            posMemVirtual = memVirtual.getAddress(scope, self.currType) # falta cambiar a que sea segun el tipo
            self.functions[self.currFunction]['vars'][var] = { 'type': self.currType, 'value': 0, 'dir': posMemVirtual }
            currParams.push({ "var": var, "type": self.currType })

    def decl_var(self, args):
        self.saveVar(args[1].value)
        return Tree('decl_var', args)      
    
    def lista_var(self, args):
        self.saveVar(args[0].value)
        return Tree('lista_var', args)

    def var(self, args):
        self.currVar = args[0]
        stackVar.push(self.findbyMem(args[0].value))
        stackType.push(self.findbyType(args[0].value))
        return Tree('var', args)     

    def string(self, args):
        dirCte = self.findbyMemCte(args[0].value)
        if dirCte == False:
            dirCte = memVirtual.getAddress('cte', 'string')
            self.functions["___cte___"]['vars'][args[0].value] = { 'type': "string", 'value': args[0].value, 'dir': dirCte }
        stackVar.push(dirCte)
        stackType.push("string")
        return Tree('string', args) 

    def integer(self, args):
        dirCte = self.findbyMemCte(args[0].value)
        if dirCte == False:
            dirCte = memVirtual.getAddress('cte', 'int')
            self.functions["___cte___"]['vars'][args[0].value] = { 'type': "int", 'value': args[0].value, 'dir': dirCte }
        stackVar.push(dirCte)       
        stackType.push('int')
        return Tree('integer', args)  

    def number(self, args):
        dirCte = self.findbyMemCte(args[0].value)
        if dirCte == False:
            dirCte = memVirtual.getAddress('cte', 'int')
            self.functions["___cte___"]['vars'][args[0].value] = { 'type': "int", 'value': args[0].value, 'dir': dirCte }
        stackVar.push(dirCte)
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
        stackJumps.push(len(quadruples))
        return Tree('while_key', args)

    def for_key(self, args):
        stackJumps.push(len(quadruples))
        return Tree('for_key', args)

    def return_str(self, args):
        stackOp.push('return')
        funcType = self.functions[self.currFunction]['type']
        stackType.push(funcType)
        return Tree('return_str', args)

    def end_exp_log(self, args):
        if stackType.size() > 0:
            exp_type = stackType.pop()
            if exp_type != "bool":
                res = stackVar.pop()
                quad = Quadruple("GotoF", res, None, None)
                quadruples.append(quad.getQuad())
                stackJumps.push(len(quadruples) - 1)
            else:
                print("error end_exp_log")
        return Tree('end_exp_log', args)

    def fin_bloque(self, args):
        genQuadGoto()
        return Tree('fin_bloque', args)

    def if_bloque(self, args):
        genQuadGoto()
        return Tree('if_bloque', args)       

    def if_key(self, args):
        if stackType.size() > 0:
            exp_type = stackType.pop()
            if exp_type == "bool":
                result = stackVar.pop()
                quad = Quadruple("GotoF", result, None, None)
                quadruples.append(quad.getQuad())
                stackJumps.push(len(quadruples) - 1)
            else:
                print("error if_key")
        return Tree('if_key', args)

    def else_key(self, args):
        if stackJumps.size() > 0:
            end = stackJumps.pop()
            quad = Quadruple("Goto", None, None, None)
            quadruples.append(quad.getQuad()) 
            stackJumps.push(len(quadruples) - 1)
            quadruples[end][3] = len(quadruples)
        return Tree('else_key', args)

    def print_exp(self, args):
        stackOp.push("print")
        stackType.push("print")
        return Tree('print_exp', args)

    def escritura_exp_comma(self, args):
        stackOp.push("print")
        stackType.push("print")
        return Tree('print_exp', args)       

    def escritura_exp(self, args):
        genQuadEndExp(["print"])    
        return Tree('end_print', args)

    def exp_comp(self, args):
        genQuadOpLog([">","<","!=","==","<=",">="])
        return Tree('exp_comp', args)

    def exp_log_or(self, args):
        genQuadOpLog(["OR"])
        return ('exp_log_or', args)     

    def exp_log_and(self, args):
        genQuadOpLog(["AND"])
        return ('exp_log_or', args)      

    def termino(self, args):
        genQuadOpExp(['+','-'])
        return ('termino', args)

    def factor(self, args):
        genQuadOpExp(["*","/"])
        return ('factor', args)

    def ended(self, args):
        genQuadEndExp(['='])
        # TEMPORAL

    def return_exp(self, args):
        genQuadEndExp(['return'])   

    def findbyType(self, var):
        if var in self.functions[self.currFunction]['vars']:
            return self.functions[self.currFunction]['vars'][var]['type'].value
        elif var in self.functions["___global___"]['vars']:
            return self.functions["___global___"]['vars'][var]['type'].value
        return False

    def findbyValue(self, var):
        if var in self.functions[self.currFunction]['vars']:
            return self.functions[self.currFunction]['vars'][var]['value']
        elif var in self.functions["___global___"]['vars']:
            return self.functions["___global___"]['vars'][var]['value']
        return False

    def findbyMem(self, var):
        if var in self.functions[self.currFunction]['vars']:
            return self.functions[self.currFunction]['vars'][var]['dir']
        elif var in self.functions["___global___"]['vars']:
            return self.functions["___global___"]['vars'][var]['dir']
        return False

    def findbyMemCte(self, var):
        if var in self.functions['___cte___']['vars']:
            return self.functions['___cte___']['vars'][var]['dir']
        return False

    def setbyValue(self, var, value):
        if var in self.functions[self.currFunction]['vars']:
            self.functions[self.currFunction]['vars'][var]['value'] = value
        elif var in self.functions["___global___"]['vars']:
            self.functions["___global___"]['vars'][var]['value'] = value
        return False

    def lparen(self, args):
        stackOp.push(args[0].value)
        return Tree("lparen", args)

    def rparen(self, args):
        stackOp.pop()
        return Tree("rparen", args)

    def program(self, args):
        prettyList(quadruples)
        return Tree("program",args)
