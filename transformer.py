from lark import Transformer, Tree
from Quadruple import *
from Stack import *
from Semantic import *
from MemoriaVirtual import *
from virtualMachine import *

# Se definen los stacks para operacion
memVirtual = MemoriaVirtual()
stackOp = Stack(False)
stackJumps = Stack(False)
stackVar = Stack(False)
# Stack para operaciones en arreglos/matrices
stackArrs = Stack(False)
stackArrName = Stack(False)
stackDim = Stack(False)
stackType = Stack(False)
# Init de tabla semantica
semTable = Semantic()
currParams = Stack(False)
# Stack para el trato de vars en el for loop
# Para el auto incremento de la variable
forloopvar = Stack(False)
quadruples = []
t_num = 0

# Para imprimir objetos y listas claramente
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

# Generacion de quadruples de logica 
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
                posMemVirtual = memVirtual.getAddress('temp', result_type)
                quad = Quadruple(operator, left_operand, right_operand, posMemVirtual)
                quadruples.append(quad.getQuad())
                stackVar.push(posMemVirtual)
                stackType.push(result_type)
            else:
                raise TypeError("ERROR: You can't perform that operation! 😥")

# Generacion de quadruples de expresion
def genQuadOpExp(cond):
    if stackOp.size() > 0:
        top = stackOp.peek()
        if top in cond:
            right_operand = stackVar.pop()
            right_type = stackType.pop()
            # Cuando son estas ops se genera el res asi mismo, el left y right operand son iguales
            if top not in ["$", "?", "¡"]:
                left_operand = stackVar.pop()
                left_type = stackType.pop()
            else:
                left_operand = right_operand
                left_type = right_type
            operator = stackOp.pop()
            result_type = semTable.result(left_type, right_type, operator)
            if result_type != False:
                posMemVirtual = 0
                # Se verifica que sea una op de arreglos o matrices
                if stackArrs.size() > 0:
                    leftArr = stackArrs.pop()
                    sze = 1
                    # Si es una + - * se toma en cuenta el right
                    if stackArrs.size() > 0 and top not in ["$", "?", "¡"]:
                        rightArr = stackArrs.pop()
                        # Se verifican que sea de la misma dim
                        if len(leftArr['arrList']) != len(rightArr['arrList']):
                            raise TypeError("ERROR: A list with a Matrix")
                        index = 0
                        # Se verifica que tengan el mismo numero de col y rows
                        # Ademas de guardar el tamano de la matriz y num de cols rows
                        while (index < len(leftArr['arrList'])):
                            if leftArr['arrList'][index][0] != rightArr['arrList'][index][0]:
                                raise TypeError("ERROR: Different sizes for operation 😥")
                            sze = sze * leftArr['arrList'][index][0]
                            index = index + 1
                            operator = operator + operator[0]
                    else:
                        if top in ["$", "?", "¡"] and len(leftArr['arrList']) != 2:
                            raise TypeError("ERROR: This operation can be only done in Matrix 😥")
                        index = 0
                        # Guarda el tamano y el row y col
                        while (index < len(leftArr['arrList'])):
                            sze = sze * leftArr['arrList'][index][0]                        
                            index = index + 1
                    dimtwo = None
                    if len(leftArr['arrList']) > 1:
                        dimtwo = leftArr['arrList'][1][0]
                    # Se genera un quad size que contiene los tamanos de la matriz o lista
                    quad = Quadruple("SIZE", leftArr['arrList'][0][0], dimtwo, sze)
                    quadruples.append(quad.getQuad())
                    posMemVirtual = None
                    if operator == "$":
                        if leftArr['arrList'][0][0] != leftArr['arrList'][1][0]:
                            raise TypeError("ERROR: Matrix must be square")
                        posMemVirtual = memVirtual.getAddress("temp", result_type)
                    else:
                        arrsizes = leftArr['arrList']
                        # En esta op se cambian las rows y cols para siguientes ops
                        if operator == "¡":
                            tmp = leftArr['arrList'][0]
                            leftArr['arrList'][0] = leftArr['arrList'][1]
                            leftArr['arrList'][1] = tmp 
                        stackArrs.push({ 'dir': posMemVirtual, 'arrList': arrsizes })
                        if stackOp.peek() != "[":
                            posMemVirtual = memVirtual.getAddress("pointer", result_type)
                            memVirtual.setNextAddress("pointer", result_type, sze)
                        else:
                            posMemVirtual = memVirtual.getAddress("temp", result_type)
                            memVirtual.setNextAddress("temp", result_type, sze)                           
                else:
                    posMemVirtual = memVirtual.getAddress('temp', result_type)
                quad = Quadruple(operator, left_operand, right_operand, posMemVirtual)
                quadruples.append(quad.getQuad())
                stackVar.push(posMemVirtual)
                stackType.push(result_type)
            else:
                print("error termino")

# Se ejecuta al finalizar la expresion, como = print etc
def genQuadEndExp(cond):
    if stackOp.size() > 0:
        top = stackOp.peek()
        if top in cond:
            right_operand = stackVar.pop()
            right_type = stackType.pop()
            operator = stackOp.pop()
            if stackVar.size() > 0 and top not in ["$", "?", "¡"]:
                left_operand = stackVar.pop()
                left_type = stackType.pop()
                result_type = semTable.result(left_type, right_type, operator)
            else:
                left_operand = None
                result_type = True
            if result_type != False:
                if stackArrs.size() > 0:
                    leftArr = stackArrs.pop()
                    sze = 1
                    if stackArrs.size() > 0:
                        sze = 1
                        rightArr = stackArrs.pop()
                        if len(leftArr['arrList']) != len(rightArr['arrList']):
                            raise TypeError("ERROR: A list with a Matrix 😥")
                        index = 0
                        while (index < len(leftArr['arrList'])):
                            if leftArr['arrList'][index][0] != rightArr['arrList'][index][0]:
                                raise TypeError("ERROR: Different sizes for operation 😥")
                            sze = sze * leftArr['arrList'][index][0]
                            index = index + 1
                            operator = operator + operator[0]  
                        operator = operator + "M"
                    else:
                        index = 0
                        while (index < len(leftArr['arrList'])):
                            sze = sze * leftArr['arrList'][index][0]
                            index = index + 1
                    dimtwo = None
                    if len(leftArr['arrList']) > 1:
                        dimtwo = leftArr['arrList'][1][0]
                    quad = Quadruple("SIZE", leftArr['arrList'][0][0], dimtwo, sze)
                    quadruples.append(quad.getQuad())
                quad = Quadruple(operator, left_operand, None, right_operand)
                quadruples.append(quad.getQuad())
            else:
                raise TypeError("ERROR: Cant perform that operation 😥")
        else:
            raise TypeError("ERROR: Exp ended too soon ", top)
    else:
        raise TypeError("ERROR: Stack Op 0")

# Se generan los goto saltos
def genQuadGoto(): 
    if stackJumps.size() > 0:
        end = stackJumps.pop()
        quadruples[end][3] = len(quadruples)
    else:
        raise TypeError("ERROR: Goto Error, No jumps left")

class TransformerLark(Transformer):

    # Se hace init a las vars locales
    def __init__(self):
        self.functions = {}
        self.currType = ""
        self.currFunction = "___global___"
        self.currVar = ""
        self.currArr = ""
        self.currFuncCounter = 0
        self.dim = 1
        self.R = 0
        self.currNodes = []
        self.calledFunction = ""

    # Hacemos init a la function global y generamos el goto al main
    def program_id(self, args):
        self.currFunction = "___global___"
        self.functions["___global___"] = { 'type': 'VOID', 'vars': {} }
        self.functions["___cte___"] = { 'type': 'VOID', 'vars': {} }
        quad = Quadruple("Goto", None, None, None)
        quadruples.append(quad.getQuad())
        return Tree('program', args)

    # Al llegar a principal reemplazamos el goto del main
    def main(self, args):
        quadruples[0][3] = len(quadruples)
        self.currFunction = "___global___"

    # Se crea los datos de la function que se declaro ademas de hacer verificacion de que no exista
    def func_name(self, args):
        self.currFunction = args[0].value
        currParams.clean()
        self.currFuncCounter = 0
        if args[0] in self.functions:
          raise ValueError(args[0] + " already defined")
        else:
          self.functions[args[0]] = { 'type': self.currType, 'vars': {}, 'params': {} }
          if self.currType != "void":
                self.saveVar(args[0], "___global___")
        return Tree('func_name', args)

    # Guardamos el tamano de los parametros
    def end_func_decl(self, args):
        self.functions[self.currFunction]['params_size'] = self.currFuncCounter
        return Tree('end_func_decl', args)

    # Agregamos los parametros a la function con el tipo
    def args_func(self, args):
        if currParams.size() > 0:
            top = currParams.pop()
            var = top["var"]
            typ = top["type"]
            self.functions[self.currFunction]['params'][self.currFuncCounter] = { 'var': var, 'type': typ }
            self.currFuncCounter = self.currFuncCounter + 1

    # Se genera el endfunc
    def func_bloque(self, args):
        quad = Quadruple("ENDFunc", None, None, None)
        quadruples.append(quad.getQuad())        

    # Se guarda el tamaño de las vars y el inicio de la func
    def func(self, args):
        self.functions[self.currFunction]['local_size'] = abs(len(self.functions[self.currFunction]['vars']) - self.functions[self.currFunction]['params_size'])
        self.functions[self.currFunction]['quad_count'] = len(quadruples)
        return Tree('end_func_decl', args)     

    # Se verifica que exista y que esa funcion exista
    def call_name(self, args):
        if args[0].value not in self.functions:
            raise TypeError("ERROR: " + args[0].value + " cant be found!")
        self.calledFunction = args[0].value
        return Tree('call_name', args)  

    def gen_era(self, args):
        quad = Quadruple("ERA", self.calledFunction, None, None)
        quadruples.append(quad.getQuad())
        self.currFuncCounter = 0
        return Tree('gen_era', args)

    # Se crean los quads de parametros
    def call_var(self, args):
        if stackVar.size() > 0:
            argument = stackVar.pop()
            typ = stackType.pop()
            param = self.functions[self.calledFunction]['params'][self.currFuncCounter]
            if param["type"] == typ:
                quad = Quadruple("PARAMETER", argument, None, self.currFuncCounter + 1) 
                self.currFuncCounter = self.currFuncCounter + 1
                quadruples.append(quad.getQuad())
            else:
                raise TypeError("ERROR: Parameters type mismatch 😥")
        return Tree('call_var', args)
    
    # Se hace el gosub, ademas de guardar el resultado de la llamada en el stack de vars para ops, y guardar el valor en un tmp
    def call_end(self, args):
        if self.currFuncCounter < len(self.functions[self.calledFunction]['params']):
            raise TypeError("ERROR:" + self.currFuncCounter + " parameters given, expecting " + len(self.functions[self.calledFunction]['params']))
        else:
            quad = Quadruple("GOSUB", None, None, self.calledFunction) 
            quadruples.append(quad.getQuad())
            if self.functions[self.calledFunction]['type'] != "void":
                scope = "local"
                if self.currFunction == "___global___":
                    scope = "global"
                mem = memVirtual.getAddress(scope,self.functions["___global___"]["vars"][self.calledFunction]["type"])
                res = self.functions["___global___"]["vars"][self.calledFunction]["dir"]
                quad = Quadruple("=", mem, None, res) 
                quadruples.append(quad.getQuad())           
                stackVar.push(mem)
                stackType.push(self.functions["___global___"]["vars"][self.calledFunction]["type"])
        return Tree('call_end', args)

    def return_val(self, args):
        self.currType = args[0].value
        return Tree('return_val', args)

    def tipo(self, defType):
        self.currType = defType[0]
        return Tree('tipo', defType)

    # Se guarda la variable con los atts como tamano, tipo etc
    def saveVar(self, var, scope = ""):
        if scope == "":
            scope = self.currFunction
        if var in self.functions[scope]['vars']:
            raise ValueError(var  + " already defined")
        else:
            if scope == "___global___":
                scopeMem = "global"
            else:
                scopeMem = "local"
            posMemVirtual = memVirtual.getAddress(scopeMem, self.currType)
            self.functions[scope]['vars'][var] = { 'type': self.currType, 'value': 0, 'dir': posMemVirtual, 'dim': 0, 'arrList': [] }
            currParams.push({ "var": var, "type": self.currType })   

    # Al momento de encontrar un id se empuja al stack de vars
    # ademas de que si es arreglo se empuja
    # a la lista de arreglos
    def id(self, args):
        exists = self.findbyMem(args[0].value)
        self.currVar = args[0].value
        arr = self.getArray(self.currVar)
        sze = len(arr)
        if sze > 0:
            stackArrs.push({ 'dir': exists, 'arrList': arr })
        stackVar.push(exists)
        stackType.push(self.findbyType(args[0]))
        if sze > 0:
            stackArrName.push(self.currVar)
        return Tree('id',args) 
    
    # Se guarda la variable nueva
    def id_new(self, args):
        self.saveVar(args[0].value)
        self.currVar = args[0].value
        sze = len(self.getArray(self.currVar))
        if sze > 0:
            stackArrName.push(self.currVar)
        return Tree('id_new', args)

    def arrms(self, args):
        if stackArrs.size() > 0:
            stackArrs.pop()
        return Tree('arrms', args)

    def lbrake(self, args):
        if self.R > 1:
            self.dim = self.dim + 1
        else:
            self.R = 1
            self.dim = 1
        self.getArray(self.currVar).append([0,0])
        return Tree('lbrake', args) 
    
    # se guardan las dims en stack para accesar despues, y agarran los nodos actuales
    def arrbrake(self, args):
        if stackVar.size() > 0:
            var = stackVar.pop()
            if len(self.getArray(stackArrName.peek())) > 0:
                self.dim = 1
                stackDim.push({ 'var': var, 'dim' : 1 })
                self.currNodes = self.getArray(stackArrName.peek()).copy()
                stackOp.push("[")
        return Tree('arrbrake', args)
    
    # Se guarda el tamano del arreglo
    def size(self, args):
        self.R = int(args[0].value) * self.R
        sze = len(self.getArray(self.currVar))
        self.getArray(self.currVar)[sze - 1][0] = int(args[0].value)
        return Tree('size', args)
    
    # Se hace el quad de ver, ademas de los de acceso
    def arrexpsize(self, args):
        if stackOp.size() > 0:
            top = stackOp.peek()
            if top in ["["]:
                dimension = self.currNodes[0]
                var = stackVar.peek()
                cteDirZero = self.insertToCte(-1)
                cteDirDim = self.insertToCte(dimension[0])
                quad = Quadruple("Ver", var, cteDirZero, cteDirDim)
                quadruples.append(quad.getQuad())
                if len(self.currNodes) > 1:
                    aux = stackVar.pop()
                    posMemVirtual = memVirtual.getAddress('temp', "int")
                    quad = Quadruple("*", aux, cteDirDim, posMemVirtual)
                    quadruples.append(quad.getQuad())
                    stackVar.push(posMemVirtual)
                if self.dim > 1:
                    aux2 = stackVar.pop()
                    aux1 = stackVar.pop()
                    posMemVirtual = memVirtual.getAddress('temp', "int")
                    quad = Quadruple("+", aux1, aux2, posMemVirtual)
                    quadruples.append(quad.getQuad())
                    stackVar.push(posMemVirtual)
            return Tree('arrexpsize', args)

    # Cuando se encuentra otra dim se trata como tal
    def lbrakesecond(self, args):
        self.dim = self.dim + 1
        currDim = stackDim.pop()
        currDim['dim'] = self.dim
        stackDim.push(currDim)
        self.currNodes.pop(0)
        return Tree('lbrakesecond', args)        

    # Al finalizar el arreglo se guarda el resultado del acesso mas pointer
    def arr(self, args):
        if stackArrs.size() > 0:
            stackArrs.pop()
        if stackVar.size() > 0:
            aux1 = stackVar.pop()
            posMemVirtual2 = memVirtual.getAddress('temp', "int")
            posMemVirtual3 = self.findbyMem(stackArrName.pop())
            quad = Quadruple("+", aux1, posMemVirtual3, posMemVirtual2)
            stackVar.push(posMemVirtual2)
            quadruples.append(quad.getQuad())
            stackOp.pop()
            self.dim = 1
    
    # cuando se decalra una variable, si es arreglo se crean el tamano de memroia
    def decl_var(self, args):
        dimTmp = 0
        offset = 0
        sze = self.R
        last = len(self.getArray(self.currVar))

        if last == 0:
            return Tree('decl_var', args)

        posMemVirtual = memVirtual.getAddress("pointer", self.currType)
        memVirtual.setNextAddress("pointer", self.currType, self.R)
        self.functions[self.currFunction]['vars'][self.currVar]["dir"] = posMemVirtual
        for node in self.getArray(self.currVar):
            mDim = self.R / node[0]
            self.R = mDim
            node[1] = mDim
            offset = offset + mDim
        K = offset
        self.getArray(self.currVar)[last - 1][1] = -K
        self.dim = 1
        self.R = 0

    # Las siguientes funciones son para guardar los valores en ctes
    def string(self, args):
        dirCte = self.findbyMemCte(args[0].value)
        if dirCte == -1:
            dirCte = memVirtual.getAddress('cte', 'char')
            slicedString = args[0].value[1:len(args[0].value) - 1]
            self.functions["___cte___"]['vars'][args[0].value] = { 'type': "char", 'value': slicedString, 'dir': dirCte }
        stackVar.push(dirCte)
        stackType.push("char")
        return Tree('string', args) 

    def insertToCte(self, value):
        dirCte = self.findbyMemCte(value)
        if dirCte == -1:
            dirCte = memVirtual.getAddress('cte', 'int')
            self.functions["___cte___"]['vars'][value] = { 'type': "int", 'value': value, 'dir': dirCte }
        return dirCte

    def integer(self, args):
        dirCte = self.findbyMemCte(args[0].value)
        if dirCte == -1:
            dirCte = memVirtual.getAddress('cte', 'int')
            self.functions["___cte___"]['vars'][args[0].value] = { 'type': "int", 'value': args[0].value, 'dir': dirCte }
        stackVar.push(dirCte)       
        stackType.push('int')
        return Tree('integer', args)  

    def number(self, args):
        dirCte = self.findbyMemCte(args[0].value)
        if dirCte == -1:
            dirCte = memVirtual.getAddress('cte', 'float')
            self.functions["___cte___"]['vars'][args[0].value] = { 'type': "float", 'value': args[0].value, 'dir': dirCte }
        stackVar.push(dirCte)
        stackType.push('float')
        return Tree('number', args) 
    
    def boolean(self, args):
        dirCte = self.findbyMemCte(args[0].value)
        if dirCte == -1:
            dirCte = memVirtual.getAddress('cte', 'bool')
            self.functions["___cte___"]['vars'][args[0].value] = { 'type': "bool", 'value': args[0].value, 'dir': dirCte }
        stackVar.push(dirCte)
        stackType.push('bool')     
        return Tree('bool', args) 

    # Las siguientes funciones agregan las ops al stack
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
    
    def opmatrix(self, args):
        stackOp.push(args[0].value)
        return Tree('opmatrix', args)

    # Se guarda donde se empezo el loop
    def while_key(self, args):
        stackJumps.push(len(quadruples))
        return Tree('while_key', args)

    def to(self, args):
        stackJumps.push(len(quadruples))
        return Tree('to', args)

    def return_str(self, args):
        stackOp.push('return')
        funcType = self.functions[self.currFunction]['type']
        stackType.push(funcType)
        return Tree('return_str', args)

    # Fin de exp logica para generar el gotof, y se guarda donde se genero
    def end_exp_log(self, args):
        if stackType.size() > 0:
            exp_type = stackType.pop()
            if exp_type == "bool":
                res = stackVar.pop()
                quad = Quadruple("GotoF", res, None, None)
                quadruples.append(quad.getQuad())
                stackJumps.push(len(quadruples) - 1)
            else:
                raise TypeError("ERROR: Logical operation error")
        return Tree('end_exp_log', args)

    # Se genera el goto con el retorno, si se puede
    # y reemplaza el gotof
    def fin_bloque(self, args):
        end = stackJumps.pop()
        if stackJumps.size() > 0:
            ret = stackJumps.pop()
            quad = Quadruple("Goto", None, None, ret)
            quadruples.append(quad.getQuad()) 
        quadruples[end][3] = len(quadruples)
        return Tree('fin_bloque', args)
    
    # Se genera los quads para el auto increment de las variables
    # Se genera el goto para el loop y reemplaza el gotof
    def fin_for_loop(self, args):
        aux = forloopvar.pop()
        posMemVirtual = memVirtual.getAddress('temp', "int")
        numone = self.insertToCte(1)
        quad = Quadruple("+", aux, numone, posMemVirtual)
        quadruples.append(quad.getQuad())
        quad = Quadruple("=", aux, None, posMemVirtual)
        quadruples.append(quad.getQuad())
        end = stackJumps.pop()
        if stackJumps.size() > 0:
            ret = stackJumps.pop()
            quad = Quadruple("Goto", None, None, ret)
            quadruples.append(quad.getQuad()) 
        quadruples[end][3] = len(quadruples)
        return Tree('fin_for_loop', args)

    # Se guarda la variable que se modificara
    def exp_end_for(self, args):
        quadsze = len(quadruples)
        currVar = quadruples[quadsze - 1][1]
        forloopvar.push(currVar)
        return Tree('exp_end_for', args)

    # Se hace un goto generico
    def if_bloque(self, args):
        genQuadGoto()
        return Tree('if_bloque', args)       

    # Se genera el gotof y se guarda
    def if_key(self, args):
        if stackType.size() > 0:
            exp_type = stackType.pop()
            if exp_type == "bool":
                result = stackVar.pop()
                quad = Quadruple("GotoF", result, None, None)
                quadruples.append(quad.getQuad())
                stackJumps.push(len(quadruples) - 1)
            else:
                raise TypeError("ERROR: You cant do that in an IF, no boolean was returned")
        return Tree('if_key', args)

    # Se hace el goto para el if y se reemplaza el pasado del if
    def else_key(self, args):
        if stackJumps.size() > 0:
            end = stackJumps.pop()
            quad = Quadruple("Goto", None, None, None)
            quadruples.append(quad.getQuad()) 
            stackJumps.push(len(quadruples) - 1)
            quadruples[end][3] = len(quadruples)
        return Tree('else_key', args)

    # Las ops para print y read
    def print_exp(self, args):
        stackOp.push("print")
        stackType.push("print")
        return Tree('print_exp', args)

    def read_emp(self, args):
        stackOp.push("read")
        stackType.push("read")
        return Tree("read_emp", args)

    def comma_read(self, args):
        stackOp.push("read")
        stackType.push("read")
        return Tree("comma_read", args)

    def comma(self, args):
        stackOp.push("print")
        stackType.push("print")
        return Tree('comma', args)       

    # Para hacer los end exp para print read
    def print_exp_fin(self, args):
        genQuadEndExp(["print"])    
        return Tree('print_exp_fin', args)

    def id_finished(self, args):
        genQuadEndExp(['read'])
        return Tree('id_read', args)

    # Genera quad logicos
    def exp_comp(self, args):
        genQuadOpLog([">","<","!=","==","<=",">="])
        return Tree('exp_comp', args)

    def exp_log_or(self, args):
        genQuadOpLog(["OR"])
        return ('exp_log_or', args)     

    def exp_log_and(self, args):
        genQuadOpLog(["AND"])
        return ('exp_log_or', args)      

    # Se generan quads de exp
    def termino(self, args):
        genQuadOpExp(['+','-'])
        return ('termino', args)

    def factor(self, args):
        genQuadOpExp(["*","/","$","?","¡"])
        return ('factor', args)

    def assign_var(self, args):
        genQuadEndExp(['='])

    def return_exp(self, args):
        genQuadEndExp(['return'])   

    # Funciones helpers
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
        return -1

    def getArray(self, var):
        if var in self.functions[self.currFunction]['vars']:
            return self.functions[self.currFunction]['vars'][var]['arrList']
        elif var in self.functions["___global___"]['vars']:
            return self.functions["___global___"]['vars'][var]['arrList']
        return []

    def findbyMemCte(self, var):
        if var in self.functions['___cte___']['vars']:
            return self.functions['___cte___']['vars'][var]['dir']
        return -1

    def setbyValue(self, var, value):
        if var in self.functions[self.currFunction]['vars']:
            self.functions[self.currFunction]['vars'][var]['value'] = value
        elif var in self.functions["___global___"]['vars']:
            self.functions["___global___"]['vars'][var]['value'] = value
        return False

    # Se guardan las ops de lparen y se popean al final del arreglo
    def lparen(self, args):
        stackOp.push(args[0].value)
        return Tree("lparen", args)

    def rparen(self, args):
        stackOp.pop()
        return Tree("rparen", args)

    # Se ejecuta al final del programa
    def program(self, args):
        #prettyList(quadruples)
        #pretty(self.functions)
        runMachine(quadruples, self.functions)
        return Tree("program",args)
