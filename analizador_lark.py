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

    read: read_emp LPAREN ID RPAREN read_end
    read_emp : READ
    read_end : SEMI

    estatuto : asignacion 
    | condicion 
    | escritura
    | while
    | return
    | read
    | for_loop

    asignacion : var assign exp ended -> assign_var
    ended: SEMI


    escritura : print_exp LPAREN escritura_exp RPAREN end_print
    end_print : SEMI
    print_exp : PRINT
    escritura_exp: STRING escritura_exp_comma?
    | exp escritura_exp_comma?
    escritura_exp_comma: "," escritura_exp

    return: RETURN LPAREN exp RPAREN SEMI

    condicion: IF LPAREN exp if_key THEN if_bloque
    if_bloque: bloque else?
    if_key: RPAREN
    else: else_key bloque
    else_key: ELSE

    while: while_key LPAREN exp end_exp_log DO fin_bloque 
    fin_bloque: bloque
    end_exp_log: RPAREN
    while_key: WHILE

    for_loop: for_key var assign exp TO exp DO (bloque | estatuto)
    for_key: FROM

    exp : termino op1?
    op1 : plus_minus exp 
          
    plus_minus: PLUS_MINUS

    termino : factor op2?
    op2 : times_divide termino

    times_divide: TIMES_DIVIDE

    factor : var
            | number
            | call
            | PLUS var_cte 
            | MINUS var_cte 
            | LPAREN exp_log_or RPAREN

    call: ID LPAREN call_args? RPAREN
    call_args: exp call_args_comma?
    call_args_comma: "," call_args


    var_cte : cte EXCL
    | cte QUES
    | cte

    cte : integer
    | number
    integer: INTEGER
    number: NUMBER


    exp_log_or: exp_log_and op3?
    op3: OR exp_log_or
    exp_log_and: exp_comp op4?
    op4: AND exp_log_and
    exp_comp: exp op5 exp
    | exp
    op5 : GREATER ASSIGN
    | LESS ASSIGN 
    | LESS 
    | GREATER 
    | DIFF
    | EQUAL


    assign: ASSIGN
    lparen: LPAREN
    rparen: RPAREN

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
    TIMES_DIVIDE: "*" | "/"
    PLUS_MINUS: "+" | "-"
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