from MemoriaVirtual import *
from Stack import *
import numpy as np
# La memoria init para el pointer
pointerMin = 160000*100000000000000

# Se hacen las memorias iniciales
# Para local y tmp se tienen stacks de memoria
globalMem = Memory(0)
cteMem = Memory(12000)
pointMem = Memory(pointerMin)
funcNames = Stack(False)
quadPos = Stack(False)
memStack = Stack(False)
tmpStack = Stack(False)
tmpMem = Memory(8000)
tmpStack.push(tmpMem)

# Se hacen las operaciones
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

def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value)) 

# optiene el valor de la variable en base al numero de dir
def getVarValue(dirVar):
  if dirVar >= pointerMin:
    currVar = pointMem.getVar(dirVar)
  elif dirVar >= 12000:
    currVar = cteMem.getVar(dirVar)
  elif dirVar >= 8000:
    tmpMem = tmpStack.peek()
    currVar = tmpMem.getVar(dirVar) 
  elif dirVar >= 4000:
    localMem = memStack.peek()
    currVar = localMem.getVar(dirVar)
  elif dirVar >= 0:
      currVar = globalMem.getVar(dirVar)
  return currVar

# hace set al valor de la variable en base al numero de dir
def setVarValue(dirVar, value):
  if dirVar >= pointerMin:
    currVar = pointMem.setVar(dirVar, value)
  elif dirVar >= 12000:
    currVar = cteMem.setVar(dirVar, value)
  elif dirVar >= 8000:
    tmpMem = tmpStack.peek()
    currVar = tmpMem.setVar(dirVar, value)
  elif dirVar >= 4000:
    localMem = memStack.peek()
    currVar = localMem.setVar(dirVar, value)
  elif dirVar >= 0:
      currVar = globalMem.setVar(dirVar, value)
  return currVar

def runMachine(quadruples, functions):

  # Se crean las tablas para function global y las ctes que se definieron
  for currVar in functions["___cte___"]["vars"]:
    cteMem.setVar(functions["___cte___"]["vars"][currVar]["dir"],functions["___cte___"]["vars"][currVar]["value"])

  for currVar in functions["___global___"]["vars"]:
    globalMem.setVar(functions["___global___"]["vars"][currVar]["dir"],functions["___global___"]["vars"][currVar]["value"])

  i = -1
  # Para la op de arreglos
  currentArraySize = 0
  currentArrayWH = [0,0]
  # Tmps para llamadas
  newMem = None
  newTmp = None
  while i < len(quadruples):
    i = i + 1

    if i >= len(quadruples):
      break
    [op, leftDir, rightDir, resDir] = quadruples[i]

    # Guarda el resultado en la memoria
    # Si el valor es un pointer se vuelve a accesar para el resultado
    if op == "=":
      currVar = getVarValue(leftDir)
      if currVar > pointerMin - 1:
        leftDir = currVar
      resVar = getVarValue(resDir)
      if isinstance(resVar, int) and resVar > pointerMin - 1:
        resVar = getVarValue(resVar)
      setVarValue(leftDir, resVar)

    # Genera el resultado y lo guarda en la memoria
    # Si el valor es un pointer se vuelve a accesar para el resultado
    if op in ["+","-","/","*","<",">","==","!=","<=",">=", "AND", "OR"]:
      if leftDir > pointerMin - 1:
        leftVar = leftDir
      else:
        leftVar = getVarValue(leftDir)
        if isinstance(leftVar, int) and leftVar > pointerMin - 1:
          leftVar = getVarValue(leftVar)
      if rightDir > pointerMin - 1:
        rightVar = rightDir
      else:
        rightVar = getVarValue(rightDir)
        if isinstance(rightVar, int) and rightVar > pointerMin - 1:
          rightVar = getVarValue(rightVar)
      res = ops[op](leftVar, rightVar)
      setVarValue(resDir, res)

    # Cambia el i al valor del goto
    if op == "Goto":
      i = resDir - 1

    if op == "GotoF":
      resBool = getVarValue(leftDir)
      if resBool == False:
        i = resDir - 1

    # se ejecuta la action de print
    if op == "print":
      # Los arreglos y matrices se imprimen diferente
      if isinstance(resDir, int) and resDir > pointerMin - 1:
        size = currentArraySize
        resultPointer = resDir
        [w, h] = currentArrayWH
        index = 0  
        cw = 0
        # Si es de una dim se imprime como lista
        if h == None:
          while cw < w:
            value = getVarValue(resDir + cw)
            print(value, end=' ')
            cw = cw + 1
          print("")  
        else:       
          # Se imprime como matrix
          # el off sirve para el salto de renglon
          off = 0
          while cw < w:
            j = 0
            while j < h:
              value = getVarValue(resDir + j + cw + off)
              print(value, end=' ')
              j = j + 1
            off = off + 1
            cw = cw + 1
            print("")
      else:
        # Se imprime normal, si es un pointer al igual se busca el valor real
        # para momentos como b = 16000000000;
        val = getVarValue(resDir)
        if isinstance(val, int) and val > pointerMin - 1:
          val = getVarValue(val)
        print(val)

    # Operacion para matrix
    if op == "$":
      [w, h] = currentArrayWH
      # Se genera matrix temporal con los valores de tamano
      Matrix = [[0 for x in range(w)] for y in range(h)] 
      
      M = leftDir

      cw = 0
      off= 0
      # Se guarda en la matrix tmp
      while cw < w:
        j = 0
        while j < h:
          value = getVarValue(leftDir + j + cw + off)
          Matrix[cw][j] = value
          j = j + 1
        off=off+1
        cw = cw + 1
      # Se saca la determinante
      res = np.linalg.det(Matrix)
      setVarValue(resDir, res)

    if op == "¡":
      [w, h] = currentArrayWH
      Matrix = [[0 for x in range(h)] for y in range(w)] 
      
      M = leftDir

      cw = 0
      off=0
      while cw < w:
        j = 0
        while j < h:
          value = getVarValue(leftDir + j + cw + off)
          Matrix[cw][j] = value
          j = j + 1
        off=off+1
        cw = cw + 1
      # Se hace la transpuesta
      m = np.array(Matrix)
      res = m.T
      cw = 0
      j = 0
      off=0
      # Se guarda el resultado en la direction del pointer tmp
      while cw < h:
        j = 0
        while j < w:
          setVarValue(resDir + j + cw + off, res[cw][j])
          j = j + 1
        off=off+1
        cw = cw + 1

    if op == "?":
      [w, h] = currentArrayWH
      Matrix = [[0 for x in range(h)] for y in range(w)] 
      
      M = leftDir

      cw = 0
      off=0
      while cw < w:
        j = 0
        while j < h:
          value = getVarValue(leftDir + j + cw + off)
          Matrix[cw][j] = value
          j = j + 1
        off=off+1
        cw = cw + 1
      # Se saca la inversa
      m = np.array(Matrix)
      res = np.linalg.inv(m)
      cw = 0
      j = 0
      off = 0
      while cw < w:
        j = 0
        while j < h:
          setVarValue(resDir + j + cw + off, res[cw][j])
          j = j + 1
        off = off + 1
        cw = cw + 1

    # Operaciones de matrices y arreglos
    if op in ["+++","---","***","///","++","--","**", "//"]:
      size = currentArraySize
      leftPointer = leftDir
      rightPointer = rightDir
      resultPointer = resDir

      index = 0  
      # Matriz y lista se tratan igual en este caso, se genera la op por cada uno
      while index < size:
          leftPointerValue = getVarValue(leftPointer)
          rightPointerValue = getVarValue(rightPointer)
          res = ops[op[0]](leftPointerValue, rightPointerValue)
          setVarValue(resultPointer, res)
          index = index + 1
          leftPointer = leftPointer + 1
          rightPointer = rightPointer + 1
          resultPointer = resultPointer + 1
    
    # Asignacion especial para matriz y lista
    if op in ["===M","==M"]:
      size = currentArraySize
      leftPointer = leftDir
      resultPointer = resDir 
      index = 0  
      # Igual que la op pero se guarda en el res
      while index < size:
          resultPointerValue = getVarValue(resultPointer)
          setVarValue(leftPointer, resultPointerValue)
          index = index + 1
          leftPointer = leftPointer + 1
          resultPointer = resultPointer + 1
    # Se guardan las dimensiones
    if op == "SIZE":
      currentArraySize = resDir
      currentArrayWH[0] = leftDir
      currentArrayWH[1] = rightDir

    # Se generan las memorias proximas
    if op == "ERA":
      # Para recursividad
      funcNames.push(leftDir)
      newMem = Memory(4000)
      newTmp = Memory(8000)
      # Se hacen init a las vars
      for currVar in functions[leftDir]["vars"]:
        newMem.setVar(functions[leftDir]["vars"][currVar]["dir"],functions[leftDir]["vars"][currVar]["value"])

    # Se verifica los rangos
    if op == "Ver":
      target = getVarValue(leftDir)
      if target > pointerMin - 1:
        target = getVarValue(target)
      limInf = getVarValue(rightDir)
      limSup = getVarValue(resDir)
      if target <= limInf or target > limSup:
        print("Error en rango de indice", target, limInf, limSup)
        break

    # Pasa la memoria al stack y se cambia la i, y se guarda su pos
    if op == "GOSUB":
      quadPos.push(i)
      memStack.push(newMem)
      tmpStack.push(newTmp)
      i = functions[funcNames.peek()]['quad_count'] - 1
    
    # Se lee el input y se guarda
    if op == "read":
      value = input()
      setVarValue(resDir, value)

    # se hace init de cada param, en la mem nueva, que no esta en el stack todavia
    if op == "PARAMETER":
      param = getVarValue(leftDir)
      nameVar = functions[funcNames.peek()]['params'][resDir-1]['var']
      dirVar = functions[funcNames.peek()]['vars'][nameVar]['dir']
      newMem.setVar(dirVar, param)

    # Se borra la memoria y se regresa a la i original
    if op == "ENDFunc":
      i = quadPos.pop()
      funcNames.pop()
      memStack.pop()
      tmpStack.pop()

    # Se guarda el return en el valor, y se trata como un endfunc
    if op == "return":
      dirToRes = functions['___global___']['vars'][funcNames.peek()]['dir']
      resValue = getVarValue(resDir)
      setVarValue(dirToRes, resValue)
      i = quadPos.pop()
      funcNames.pop()
      memStack.pop()
      tmpStack.pop()