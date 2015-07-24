import functools as ft
import time
import random
import sys

"""
Befunge-93 Interpreter
"""


stack = [] #list vs deque performance is comparable in this use case
IP = (0,0)
IP_delta = (1,0)
bounds = (79,79)
funge = {}
string_mode = False
max_ticks = 2000
tick_counter = 0

def stack_pop():
    try:
        return stack.pop()
    except IndexError:
        return 0

def add():
    # '+' : Addition: Pop a and b, then push a+b
    stack.append(stack_pop() + stack_pop())

def subtract():
    # '-' : Subtraction: Pop a and b, then push b-a
    a = stack_pop()
    b = stack_pop()
    stack.append(b-a)

def multiply():
    # '*' : Multiplication: Pop a and b, then push a*b
    stack.append(stack_pop() * stack_pop())

def divide():
    # '/' : Integer division: Pop a and b, then push b/a, rounded down. 
    #       If a is zero, ask the user what result they want.
    #stack.append(stack_pop() / stack_pop())
    a = stack_pop()
    b = stack_pop()
    if not a: 
        ask_num()
    else: 
        c = int(b) / int(a)
        stack.append(c)

def modulo():
    # '%' : Modulo: Pop a and b, then push the remainder of the integer division of b/a.
    stack.append(stack_pop() % stack_pop())

def logical_not():
    # '!'' : Logical NOT: Pop a value. If the value is zero, push 1; otherwise, push zero.
    if not stack_pop(): 
        stack.append(1)
    else:
        stack.append(0)

def greater_than():
    # '`' : Greater than: Pop a and b, then push 1 if b>a, otherwise zero.
    a = stack_pop()
    b = stack_pop()
    if b>a:
        stack.append(1)
    else:
        stack.append(0)

def change_direction(new_direction):
    global IP_delta
    if new_direction in ['right', 'left', 'up', 'down']:
        if new_direction == 'right':
            IP_delta = (1,0)
        elif new_direction == 'left':
            IP_delta = (-1,0)
        elif new_direction == 'up':
            IP_delta = (0,-1)
        elif new_direction == 'down':
            IP_delta = (0,1)
    else:
        raise KeyError

def random_direction():
    # '?' : Start moving in a random cardinal direction
    change_direction(random.choice(['right', 'left', 'up', 'down']))

def left_right_choice():
    # '_' : Pop a value; move right if value=0, left otherwise
    if stack_pop():
        change_direction('left') 
    else:
        change_direction('right')

def up_down_choice():
    # '|' : Pop a value; move down if value=0, up otherwise
    if stack_pop():
        change_direction('up')
    else:
        change_direction('down')

def switch_string_mode():
    # '"' : Start sring mode: push each character's ASCII value all the way to the next "
    #       yes, '"' does indeed work as intended, even though it looks fugly as hell
    global string_mode
    string_mode = not string_mode

def duplicate():
    # ':' : Duplicate value on top of the stack
        value = stack_pop()
        stack.append(value)
        stack.append(value)

def swap():
    # '\' : Swap two values on top of the stack
    # there might be an issue with escape characters, 
    # since \ will usually escape the next character, 
    # so in the dictionary it is listed as '\\', check 
    # to see if this matches with just a standard backslash
    a = stack_pop()
    b = stack_pop()
    stack.append(a)
    stack.append(b)

def discard():
    # '$' : Pop value from the stack and discard it
    stack_pop()

def print_int():
    # '.' : Pop value and output as an integer
    print(stack_pop(), end = '')

def print_ASCII():
    # ','   Pop value and output as an ASCII character
    popped = stack_pop()
    if popped == 10:
        print('\n')
    else:
        print(chr(popped), end = '')

def trampoline():
    global IP
    # '#' : Trampoline: Skip next cell
    #
    #  *  *  *   This *should* work, but might be buggy   *  *  *  
    #
    IP = (IP[0] + IP_delta[0], IP[1] + IP_delta[1])
    

def put():
    global funge
    # 'p' : A "put" call (a way to store a value for later use). 
    #       Pop y, x, and v, then change the character at (x,y) 
    #       in the program to the character with ASCII value v
    y = stack_pop()
    x = stack_pop()
    v = stack_pop()
    funge[(x,y)] = chr(v)

def get():
    # 'g' : A "get" call (a way to retrieve data in storage). 
    #       Pop y and x, then push ASCII value of the character 
    #       at that position in the program. 
    #       If (x,y) is out of bounds, push 0. 
    y = stack_pop()
    x = stack_pop()
    stack.append(ord(funge[(x,y)]))

def ask_num():
    # '&' : Ask user for a number and push it
    #     doesn't handle bad input
    push_num(input())

def ask_char():
    # '~' : Ask user for a character and push its ASCII value
    #      doesn't handle bad input
    push_char(input())

def nop():
    # no op
    pass

def leave():
    #funge_print(funge)
    quit()

def push_num(num):
    stack.append(int(num))

def push_char(char):
    stack.append(ord(char))

def tick():
    #print('t', end = '')
    ruleset[funge.get(IP, ' ')]()
    move()

def move():
    # idealy one could use timeit to try different implementations of this
    # function and find which way is fastest, but this seems good enough 
    # for now at least

    global IP 
    #print('m', end = '')
    # left right movement first
    if IP[0] + IP_delta[0] < bounds[0]:
        # normal movement
        IP = (IP[0] + IP_delta[0], IP[1])
    elif IP[0] + IP_delta[0] < 0:
        # going off the left side
        IP = (bounds[0], IP[1])
    else:
        # going off the right side
        IP = (0, IP[1])
    # updown movement next
    if IP[1] + IP_delta[1] < bounds[1]:
        # normal movement
        IP = (IP[0], IP[1] + IP_delta[1])
    elif IP[1] + IP_delta[1] < 0:
        # going off the top
        IP = (IP[0], bounds[1])
    else:
        # going off the bottom
        IP = (IP[0], 0)

def initilize(input_string):
    global funge
    global stack
    stack = []
    input_lines = input_string.splitlines()
    for y, line in enumerate(input_lines):
        #print(line)
        padding_amount = bounds[0]-len(line)
        line = line + ' ' * padding_amount
        for x, letter in enumerate(line):
            funge[(x,y)] = letter

def funge_print(fungespace):
    output_string = '\n'
    for y in range(bounds[1]):
        for x in range(bounds[0]):
            output_string+=str(fungespace.get((x,y),' '))
        output_string+='\n'
    print(output_string.rstrip())


ruleset = {'+' : add, 
           '-' : subtract,
           '*' : multiply,
           '/' : divide,
           '%' : modulo,
           '!' : logical_not,
           '`' : greater_than,
           '>' : ft.partial(change_direction, 'right'),
           '<' : ft.partial(change_direction, 'left'),
           '^' : ft.partial(change_direction, 'up'),
           'v' : ft.partial(change_direction, 'down'),
           '?' : random_direction,
           '_' : left_right_choice,
           '|' : up_down_choice,
           '"' : switch_string_mode,
           ':' : duplicate,
           '\\': swap,
           '$' : discard,
           '.' : print_int,
           ',' : print_ASCII,
           '#' : trampoline, 
           'p' : put,
           'g' : get,
           '&' : ask_num,
           '~' : ask_char,
           '@' : leave,
           ' ' : nop,
           '0' : ft.partial(push_num, 0),
           '1' : ft.partial(push_num, 1),
           '2' : ft.partial(push_num, 2),
           '3' : ft.partial(push_num, 3),
           '4' : ft.partial(push_num, 4),
           '5' : ft.partial(push_num, 5),
           '6' : ft.partial(push_num, 6),
           '7' : ft.partial(push_num, 7),
           '8' : ft.partial(push_num, 8),
           '9' : ft.partial(push_num, 9),
           }


with open(sys.argv[1], 'r') as f:
    initilize(f.read())

while tick_counter < max_ticks:
    if not string_mode:
        tick()
    else:
        if funge[IP] == '"': 
            switch_string_mode()
            move()
        else: 
            push_char(funge[IP])
            move()
    tick_counter += 1
    #time.sleep(.01)
