from lark import Lark
from transformer import TransformerLark
import os
import sys
import codecs

calc_grammar = r"""
    start: program

    program_id : ID
    program : PROGRAM program_id SEMI program_es
    program_es : vars (func bloque)* main_func
    | bloque
    main_func : MAIN LPAREN RPAREN bloque

    var : ID arrm? arrm? "$"?
    decl_var : tipo ID arrm? arrm? "$"?
    var_id : decl_var lista_var? SEMI var_id?
    lista_var : "," ID arrm? arrm? "$"? lista_var?
    vars : VAR var_id

    arrm : LBRAKE (INTEGER | ID) RBRAKE

    tipo : INT 
    | FLOAT 

    return_val: VOID
    | INT
    | FLOAT 

    args_func : decl_var
    func : FUNCTION return_val func_name LPAREN args_func? ("," args_func)* RPAREN vars?
    func_name: ID

    bloque : LBRACE estatuto* RBRACE 

    read: READ LPAREN ID RPAREN SEMI

    estatuto : asignacion 
    | condicion 
    | escritura
    | while
    | return
    | read
    | for_loop

    asignacion : var ASSIGN expresion SEMI -> assign_var

    escritura : PRINT LPAREN escritura_exp RPAREN SEMI
    escritura_exp: STRING escritura_exp_comma?
    | expresion escritura_exp_comma?
    escritura_exp_comma: "," escritura_exp

    return: RETURN LPAREN exp RPAREN SEMI

    condicion : IF LPAREN expresion RPAREN THEN bloque else?
    else : ELSE bloque

    while: WHILE LPAREN expresion RPAREN DO bloque
    for_loop: FROM var ASSIGN expresion TO expresion DO (bloque | estatuto)

    exp : termino exp_2?
    exp_2 : PLUS exp 
    | MINUS exp

    termino : factor ter?
    ter : TIMES termino
    | DIVIDE termino

    call: ID LPAREN call_args RPAREN
    call_args: expresion "," call_args
    | expresion

    factor : LPAREN expresion RPAREN
            | call
            | PLUS var_cte 
            | MINUS var_cte 
            | var_cte

    var_cte : var 
    | cte EXCL
    | cte QUES
    | cte

    cte : INTEGER
    | NUMBER


    expresion : exp
    | expresion exp_l expresion
    | exp exp_s exp
    exp_l : OR
    | AND
    exp_s : GREATER ASSIGN
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
    VOID: "void"

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

duck_parser = Lark(calc_grammar, parser='lalr',debug=True, transformer=TransformerLark())
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
    print(duck(cadena2).pretty())


if __name__ == '__main__':
    test()