from lark import Lark
from transformer import TransformerLark
import os
import sys
import codecs

calc_grammar = r"""
    start: program

    program_id : ID
    program : PROGRAM program_id SEMI program_es
    program_es : vars (exec_func func_bloque)* main_func
    | bloque
    exec_func: func
    func_bloque : bloque
    main_func : main LPAREN RPAREN bloque
    main: MAIN
    var : id arr?
    arr: arrmexp (lbrakesecond arrexpsize rbrakearr)?
    lbrakesecond: LBRAKE
    decl_var : tipo id_new arrm? arrm?
    id_new: ID
    id: ID
    var_id : decl_var lista_var? SEMI var_id?
    lista_var : "," ID arrm? arrm? lista_var?
    vars : VAR var_id

    arrm : lbrake size rbrake
    arrmexp : arrbrake arrexpsize rbrakearr
    rbrakearr: RBRAKE
    arrexpsize : exp
    arrbrake: LBRAKE
    lbrake: LBRAKE
    rbrake: RBRAKE
    size: INTEGER | NUMBER

    tipo : INT 
    | FLOAT 
    | LETRAS

    return_val: VOID
    | INT
    | FLOAT 
    | LETRAS

    args_func : decl_var
    func : FUNCTION return_val func_name LPAREN args_func? ("," args_func)* end_func_decl func_vars?
    func_vars: vars
    end_func_decl: RPAREN
    func_name: ID

    bloque : LBRACE estatuto* RBRACE

    estatuto : asignacion 
    | condicion 
    | escritura
    | while
    | return
    | read
    | for_loop
    | call semi_call
    semi_call: SEMI

    asignacion : var assign exp ended? -> assign_var 
    ended: SEMI

    read: read_emp LPAREN id_read RPAREN read_end
    id_read: id_finished read_comma?
    id_finished: id
    read_comma: comma_read id_read
    comma_read: ","
    read_emp : READ
    read_end : SEMI

    escritura : print_exp LPAREN escritura_exp RPAREN end_print
    end_print : SEMI
    print_exp : PRINT
    escritura_exp: print_exp_fin escritura_exp_comma?
    print_exp_fin: exp
    escritura_exp_comma: comma escritura_exp
    comma: ","

    return: return_str LPAREN return_exp RPAREN SEMI
    return_str: RETURN
    return_exp: exp

    condicion: IF exp if_key if_bloque
    if_bloque: bloque else?
    if_key: THEN
    else: else_key bloque
    else_key: ELSE

    while: while_key exp end_exp_log fin_bloque 
    fin_bloque: bloque
    end_exp_log: DO
    while_key: WHILE

    for_loop: for_key LPAREN asignacion exp_end_for to exp end_exp_log fin_for_loop
    exp_end_for: RPAREN
    fin_for_loop: bloque
    to: TO
    for_key: FROM

    exp : termino op1?
    op1 : plus_minus exp 
          
    plus_minus: PLUS_MINUS

    termino : factor op2?
    op2 : times_divide termino

    times_divide: TIMES_DIVIDE

    factor : boolean
            | var opmatrix?
            | call
            | number
            | string
            | integer
            | PLUS var_cte 
            | MINUS var_cte 
            | LPAREN exp_log_or RPAREN
    
    opmatrix: SIGN
    | QUES
    | EXCLD

    SIGN: "$"
    EXCLD: "¡"

    string: STRING
    boolean: BOOLEAN
    call: call_name gen_era call_args? call_end
    call_end: rparen
    gen_era: lparen
    call_name: ID
    call_args: call_var call_args_comma?
    call_var: exp
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
    exp_comp: log_exp_comp | exp
    log_exp_comp: exp op5 exp
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
    LETRAS: "char"
    BOOL: "bool"
    FUNCTION: "funcion"
    RETURN: "regresa"
    WHILE: "mientras"
    DO.10: "haz" | "hacer"
    MAIN: "principal"
    READ: "lee"
    FROM: "desde"
    TO: "hasta"
    VOID: "void"

    BOOLEAN.10: "True" | "False"
    ID : WORD
    NUMBER : /[-+]?[0-9]*\.[0-9]+([eE][-+]?[0-9]+)?/
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
    AND: "&"
    OR: "|"
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


def test(file):
    fp = codecs.open(file,'r','utf-8')
    cadena2 = fp.read()
    fp.close()
    duck(cadena2).pretty


if __name__ == '__main__':
    test(sys.argv[1])