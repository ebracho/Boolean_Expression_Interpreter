from bei_functions import *
from bei_exceptions import *
from util import *
from itertools import product

keywords = ['true', 'false', 'and', 'or', 'not', '(', ')']

literals  = {'true': True, 'false': False}
operators = {'and': bei_and, 'or': bei_or, 'not': bei_not}
num_args  = {'and': 2, 'or': 2, 'not': 1}

# en.wikipedia.org/wiki/Shunting-yard_algorithm
# all operators have equal precedence and are left-associative
def shunting_yard(tokens, symbols): # -> [str]
    """
    tokens: [token]
    symbols: {symbol: True|False}
    """
    queue = []
    stack = []
    for token in tokens:
        if token in symbols or token in literals:
            queue.append(token)
        elif token in operators or token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                queue.append(stack.pop())
            if not stack: raise UnbalancedParen
            else: stack.pop()
        else: raise InvalidExpression

    if '(' in stack: raise UnbalancedParen
    return queue + list(reversed(stack))

# http://en.wikipedia.org/wiki/Reverse_Polish_notation
def rpn(tokens, symbols): # -> Boolean
    """
    tokens: [token]
    symbols: {symbol: True|False}
    """
    stack = []
    for token in tokens:
        if token in symbols:
            stack.append(symbols[token])
        elif token in literals:
            stack.append(literals[token])
        elif token in operators:
            if num_args[token] > len(stack):
                raise InvalidExpression
            args = [stack.pop() for i in range(num_args[token])]
            stack.append(operators[token](*args))
        else: raise InvalidExpression

    if len(stack) != 1: raise InvalidExpression
    return stack[0]

def evaluate(expr, symbols): # -> Boolean
    """
    expr: str
    symbols: {symbol: True|False}
    """
    tokens = expr.split()
    tokens = shunting_yard(tokens, symbols)
    return rpn(tokens, symbols)

def get_unique_symbols(expr): # -> [str]
    """
    expr: str
    """
    symbols = filter(lambda x: x not in keywords, expr.split())
    symbols = del_duplicates(symbols)
    return symbols

def create_truth_table(expr, extra_symbols = []): 
    """
    expr: str
    -> [[(s1,T|F), (s2,T|F)... expr_result]... ] 
    """
    # pad parentheses with white space for token split
    expr = expr.replace('(', ' ( ')   
    expr = expr.replace(')', ' ) ')
    symbols = del_duplicates(get_unique_symbols(expr) + extra_symbols)
    permutations = list(product((True, False), repeat=len(symbols))) 

    truth_table = []
    for p in permutations:
        row = []
        symbol_vals = {}
        for i, s in enumerate(symbols):
            row.append((s,p[i]))
            symbol_vals[s] = p[i]
        row.append(evaluate(expr, symbol_vals))
        truth_table.append(row)
    return truth_table

# Sorts the symbols in each row of the truth table
def sort_tt_symbols(tt): # -> None
    """
    tt: see create_truth_table()
    """
    for i, row in enumerate(tt):
        tt[i][0:len(row)-1] = sorted(tt[i][0:len(row)-1], key=lambda s: s[0])

def compare_exprs(expr1, expr2): # -> Boolean
    """
    expr1: str
    expr2: str
    """
    eq_symbols = get_unique_symbols(expr1) + get_unique_symbols(expr2)
    tt1 = create_truth_table(expr1, eq_symbols)
    tt2 = create_truth_table(expr2, eq_symbols)
    sort_tt_symbols(tt1)
    sort_tt_symbols(tt2)
    for row in tt1:
        if row not in tt2:
            return False
    return True



# so ugly
def print_tt(tt, expr): # -> None
    """
    tt: see create_truth_table()
    expr: str
    """
    rows = []
    last_col_len = 8
    if len(expr)>6: last_col_len += len(expr)-6
    bar_len = 8*(len(tt[0])-1)+last_col_len
    header = '|'
    for s in tt[0][:-1]: header += '   ' + s[0] + '   |'
    if last_col_len == 8: header += ' '*(7-len(expr))+expr+' |'
    else: header += ' ' + expr + ' |'
    rows.append('+'+'-'*bar_len+'+')
    rows.append(header)
    for r in tt:
        rows.append('|'+'-'*bar_len+'|')
        values_row = '|'
        for s in r[:-1]:
            if s[1]: values_row += ' True  |'
            else: values_row += ' False |'
        if r[-1]: values_row += ' '*(last_col_len - 7) +'  True ' + '|'
        else: values_row += ' '*(last_col_len - 7) +' False ' + '|'
        rows.append(values_row)
    rows.append('+'+'-'*bar_len+'+')

    for r in rows: print r
    
expr = '(x or y) or (z and y)'
tt = create_truth_table(expr)
print_tt(tt, expr)
