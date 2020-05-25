from MemoriaVirtual import *

localMem = Memory(4000)
globalMem = Memory(0)
tmpMem = Memory(8000)
cteMem = Memory(12000)
pointMem = Memory(16000)

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
    currVar = tmpMem.getVar(dirVar) 
  elif dirVar >= 4000:
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
    currVar = tmpMem.setVar(dirVar, value)
  elif dirVar >= 4000:
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
      val = getVarValue(resDir)
      if val > 15999:
        val = getVarValue(val)
      print(val)

