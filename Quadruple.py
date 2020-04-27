class Quadruple:
  def __init__(self, op, leftop, rightop, result):
    self.op = op
    self.quad = [op, leftop, rightop, result]

  def getQuad(self):
    return self.quad