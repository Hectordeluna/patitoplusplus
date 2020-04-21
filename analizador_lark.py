from lark import Lark, Transformer, v_args, Tree
import os
import sys
import codecs

calc_grammar = """
    ?start: program

    ?program : PROGRAM ID SEMI program_es
    ?program_es : vars (func bloque)* MAIN LPAREN RPAREN bloque
    | bloque

    ?var : ID arrm? arrm? "$"?
    ?var_id : tipo var lista_var? SEMI var_id?
    ?lista_var : "," var lista_var?
    ?vars : VAR var_id

    ?arrm : LBRAKE (INTEGER | ID) RBRAKE

    ?tipo : INT
    | FLOAT 

    ?return_val: "void"
    | tipo 

    ?args_func : tipo var ("," tipo var)?
    ?func : FUNCTION return_val ID LPAREN args_func* RPAREN vars?

    ?bloque : LBRACE estatuto* RBRACE 

    ?read: READ LPAREN ID RPAREN SEMI

    ?estatuto : asignacion 
    | condicion 
    | escritura
    | while
    | return
    | read
    | for_loop

    ?asignacion : var ASSIGN expresion SEMI -> assign_var

    ?escritura : PRINT LPAREN escritura_exp RPAREN SEMI
    ?escritura_exp: STRING escritura_exp_comma?
    | expresion escritura_exp_comma?
    ?escritura_exp_comma: "," escritura_exp

    ?return: RETURN LPAREN exp RPAREN SEMI

    ?condicion : IF LPAREN expresion RPAREN THEN bloque else?
    ?else : ELSE bloque

    ?while: WHILE LPAREN expresion RPAREN DO bloque
    ?for_loop: FROM var ASSIGN expresion TO expresion DO (bloque | estatuto)

    ?exp : termino exp_2?
    ?exp_2 : PLUS exp 
    | MINUS exp

    ?termino : factor ter?
    ?ter : TIMES termino
    | DIVIDE termino

    ?call: ID LPAREN call_args RPAREN
    ?call_args: expresion "," call_args
    | expresion

    ?factor : LPAREN expresion RPAREN
            | call
            | PLUS var_cte 
            | MINUS var_cte 
            | var_cte

    ?var_cte : var 
    | cte EXCL
    | cte QUES
    | cte

    ?cte : INTEGER
    | NUMBER


    ?expresion : exp
    | expresion exp_l expresion
    | exp exp_s exp
    ?exp_l : OR
    | AND
    ?exp_s : GREATER ASSIGN
    | LESS ASSIGN
    | LESS 
    | GREATER 
    | DIFF
    | EQUAL

    IF: "si"
    THEN: "entonces"
    ELSE: "sino"
    PROGRAM: "programa"
    PRINT: "escribe"
    VAR: "var"
    FLOAT: "float"
    INT: "int"
    FUNCTION: "funcion"
    RETURN: "regresa"
    WHILE: "mientras"
    DO: "haz" | "hacer"
    MAIN: "principal"
    READ: "lee"
    FROM: "desde"
    TO: "hasta"

    ID : WORD
    NUMBER : /[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?/
    PLUS: "+"
    MINUS: "-"
    ASSIGN: "="
    TIMES: "*"
    COLON: ":"
    DIVIDE: "/"
    SEMI: ";"
    LESS: "<"  
    GREATER: ">"  
    EQUAL: "=="  
    DOT: "."  
    AND: "&&"
    OR: "||"
    LPAREN: "("  
    RPAREN: ")"  
    LBRACE: "{"  
    RBRACE: "}"  
    LBRAKE: "["  
    RBRAKE: "]"
    EXCL: "!"  
    QUES: "?"  
    DIFF: "!=" | "<>"  
    INTEGER: /([+-]?[1-9]\d*|0)/
    COMMENT: "%%" /(.|\\n|\\r)+/

    %import common.WS_INLINE
    %import common.NEWLINE
    %import common.WORD
    %import common.ESCAPED_STRING -> STRING
    %ignore NEWLINE
    %ignore WS_INLINE
    %ignore COMMENT
"""

class tablaVars(Transformer):
    from operator import add, sub, mul, truediv as div, neg

    def __init__(self):
        self.vars = {}

    def assign_var(self, name, value):
        if name in self.vars:
            raise ValueError(name + " already defined")
        else:
            self.vars[name] = { 'type': self.currType, 'value': value }
        return Tree('var', self.vars[name])

    def tipo(self, tipo):
        self.currType = tipo

    def var(self, name):
        return Tree('var', self.vars[name])

duck_parser = Lark(calc_grammar, parser='lalr',debug=True)
duck = duck_parser.parse

def main():
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        print(duck(s))


def test():

    fp = codecs.open('./test/' + 'testCorrecto','r','utf-8')
    cadena2 = fp.read()
    fp.close()
    print(duck(cadena2))


if __name__ == '__main__':
    test()