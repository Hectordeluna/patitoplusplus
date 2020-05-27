from MemoriaVirtual import *
from Stack import *
import numpy as np

globalMem = Memory(0)
tmpMem = Memory(8000)
cteMem = Memory(12000)
pointMem = Memory(16000)
funcNames = Stack(False)
quadPos = Stack(False)
memStack = Stack(False)
tmpStack = Stack(False)
tmpMem = Memory(8000)
tmpStack.push(tmpMem)

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

def getVarValue(dirVar):
  if dirVar >= 16000:
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

def setVarValue(dirVar, value):
  if dirVar >= 16000:
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
  pretty(functions)
  for currVar in functions["___cte___"]["vars"]:
    cteMem.setVar(functions["___cte___"]["vars"][currVar]["dir"],functions["___cte___"]["vars"][currVar]["value"])

  for currVar in functions["___global___"]["vars"]:
    globalMem.setVar(functions["___global___"]["vars"][currVar]["dir"],functions["___global___"]["vars"][currVar]["value"])

  i = -1
  currentArraySize = 0
  currentArrayWH = [0,0]
  newMem = None
  newTmp = None
  while i < len(quadruples):
    i = i + 1

    if i >= len(quadruples):
      break
    [op, leftDir, rightDir, resDir] = quadruples[i]

    if op == "=":
      currVar = getVarValue(leftDir)
      if currVar > 15999:
        leftDir = currVar
      resVar = getVarValue(resDir)
      if resVar > 15999:
        resVar = getVarValue(resVar)
      setVarValue(leftDir, resVar)

    if op in ["+","-","/","*","<",">","==","!=","<=",">=", "AND", "OR"]:
      if leftDir > 15999:
        leftVar = leftDir
      else:
        leftVar = getVarValue(leftDir)
        if leftVar > 15999:
          leftVar = getVarValue(leftVar)
      if rightDir > 15999:
        rightVar = rightDir
      else:
        rightVar = getVarValue(rightDir)
        if rightVar > 15999:
          rightVar = getVarValue(rightVar)
      
      res = ops[op](leftVar, rightVar)

      setVarValue(resDir, res)

    if op == "Goto":
      i = resDir - 1

    if op == "GotoF":
      resBool = getVarValue(leftDir)
      if resBool == False:
        i = resDir - 1

    if op == "print":
      if resDir > 15999:
        size = currentArraySize
        resultPointer = resDir
        [w, h] = currentArrayWH

        index = 0  
        cw = 0
        while cw < w:
          j = 0
          while j < h:
            value = getVarValue(resDir + j + cw)
            print(value, end=' ')
            j = j + 1
          cw = cw + 1
          print("")
      else:
        val = getVarValue(resDir)
        if isinstance(val, int) and val > 15999:
          val = getVarValue(val)
        print(val)

    if op == "$":
      [w, h] = currentArrayWH
      Matrix = [[0 for x in range(w)] for y in range(h)] 
      
      M = leftDir

      cw = 0
      while cw < w:
        j = 0
        while j < h:
          value = getVarValue(leftDir + j + cw)
          Matrix[cw][j] = value
          j = j + 1
        cw = cw + 1
      res = np.linalg.det(Matrix)
      setVarValue(resDir, res)

    if op == "¡":
      [w, h] = currentArrayWH
      Matrix = [[0 for x in range(h)] for y in range(w)] 
      
      M = leftDir

      cw = 0
      while cw < w:
        j = 0
        while j < h:
          value = getVarValue(leftDir + j + cw)
          Matrix[cw][j] = value
          j = j + 1
        cw = cw + 1
      m = np.array(Matrix)
      res = m.T
      cw = 0
      j = 0
      while cw < h:
        j = 0
        while j < w:
          setVarValue(resDir + j + cw, res[cw][j])
          j = j + 1
        cw = cw + 1

    if op == "?":
      [w, h] = currentArrayWH
      Matrix = [[0 for x in range(h)] for y in range(w)] 
      
      M = leftDir

      cw = 0
      while cw < w:
        j = 0
        while j < h:
          value = getVarValue(leftDir + j + cw)
          Matrix[cw][j] = value
          j = j + 1
        cw = cw + 1
  
      m = np.array(Matrix)
      res = np.linalg.inv(m)
      cw = 0
      j = 0
      while cw < w:
        j = 0
        while j < h:
          setVarValue(resDir + j + cw, res[cw][j])
          j = j + 1
        cw = cw + 1

    if op in ["+++","---","***","///","++"]:
      size = currentArraySize
      leftPointer = leftDir
      rightPointer = rightDir
      resultPointer = resDir

      index = 0  

      while index < size:
          leftPointerValue = getVarValue(leftPointer)
          rightPointerValue = getVarValue(rightPointer)
          res = ops[op[0]](leftPointerValue, rightPointerValue)
          setVarValue(resultPointer, res)
          index = index + 1
          leftPointer = leftPointer + 1
          rightPointer = rightPointer + 1
          resultPointer = resultPointer + 1
    
    if op in ["===M","==M"]:
      size = currentArraySize
      leftPointer = leftDir
      resultPointer = resDir 
      index = 0  

      while index < size:
          resultPointerValue = getVarValue(resultPointer)
          setVarValue(leftPointer, resultPointerValue)
          index = index + 1
          leftPointer = leftPointer + 1
          resultPointer = resultPointer + 1

    if op == "SIZE":
      currentArraySize = resDir
      currentArrayWH[0] = leftDir
      currentArrayWH[1] = rightDir

    if op == "ERA":
      funcNames.push(leftDir)
      newMem = Memory(4000)
      newTmp = Memory(8000)
      for currVar in functions[leftDir]["vars"]:
        newMem.setVar(functions[leftDir]["vars"][currVar]["dir"],functions[leftDir]["vars"][currVar]["value"])

    if op == "VER":
      target = getVarValue(leftDir)
      limInf = getVarValue(rightDir)
      limSup = getVarValue(resDir)

      if target < limInf or target > limSup:
        print("Error en rango de indice")
        break
    if op == "GOSUB":
      quadPos.push(i)
      memStack.push(newMem)
      tmpStack.push(newTmp)
      i = functions[funcNames.peek()]['quad_count'] - 1
      
    if op == "read":
      value = input()
      setVarValue(resDir, value)

    if op == "PARAMETER":
      param = getVarValue(leftDir)
      nameVar = functions[funcNames.peek()]['params'][resDir-1]['var']
      dirVar = functions[funcNames.peek()]['vars'][nameVar]['dir']
      newMem.setVar(dirVar, param)

    if op == "ENDFunc":
      i = quadPos.pop()
      funcNames.pop()
      memStack.pop()
      tmpStack.pop()

    if op == "return":
      dirToRes = functions['___global___']['vars'][funcNames.peek()]['dir']
      resValue = getVarValue(resDir)
      setVarValue(dirToRes, resValue)