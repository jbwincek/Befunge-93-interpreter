import functools as ft
import math
import time
import random
import sys

"""
Befunge-98 Interpreter
"""


stack = [] #list vs deque performance is comparable in this use case
IP = (0,0)
IP_delta = (1,0)
storage_offset = (0,0)
IP_list = [(IP, IP_delta, storage_offset), ]
bounds = (79,79)
funge = {}
string_mode = False
max_ticks = 20000
tick_counter = 0
_debug = False

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
    a = stack_pop()
    b = stack_pop()
    stack.append(b%a)

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

def change_direction(new_direction, IP, IP_delta, storage_offset):
    if new_direction in ['right', 'left', 'up', 'down']:
        if new_direction == 'right':
            IP_delta = (1, 0)
        elif new_direction == 'left':
            IP_delta = (-1, 0)
        elif new_direction == 'up':
            IP_delta = (0, 1)
        elif new_direction == 'down':
            IP_delta = (0, -1)
        return (IP, IP_delta, storage_offset)
    else:
        raise KeyError

def random_direction(IP, IP_delta, storage_offset):
    # '?' : Start moving in a random cardinal direction
    return change_direction(random.choice(['right', 'left', 'up', 'down']), IP, IP_delta, storage_offset)

def left_right_choice(IP, IP_delta, storage_offset):
    # '_' : Pop a value; move right if value=0, left otherwise
    if stack_pop():
        return change_direction('left', IP, IP_delta, storage_offset) 
    else:
        return change_direction('right', IP, IP_delta, storage_offset)

def up_down_choice(IP, IP_delta, storage_offset):
    # '|' : Pop a value; move down if value=0, up otherwise
    if stack_pop():
        return change_direction('up', IP, IP_delta, storage_offset)
    else:
        return change_direction('down', IP, IP_delta, storage_offset)

def switch_string_mode():
    # '"' : Start string mode: push each character's ASCII value all the way to the next "
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
    print(stack_pop(), end = ' ')

def print_ASCII():
    # ','   Pop value and output as an ASCII character
    print(chr(stack_pop()), end = '')

def trampoline(IP, IP_delta, storage_offset):
    # '#' : Trampoline: Skip next cell
    return move(IP, IP_delta, storage_offset)
    

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

def end_IP(IP, IP_delta, storage_offset):
    # end the current IP, if the last IP then call leave()
    pass

def leave():
    # quit the program, even if there are current IPs running 
    #funge_print(funge)
    quit()

def push_num(num):
    stack.append(int(num))

def push_char(char):
    stack.append(ord(char))

def reverse(IP, IP_delta, storage_offset):
    # 'r' : Multiply the IP_delta by -1
    IP_delta = tuple([-x for x in IP_delta])
    return (IP, IP_delta, storage_offset)

def absolute_delta(IP, IP_delta, storage_offset):
    # 'x' : Pop dy, pop dx, set IP_delta to (dx,dy)
    dy = stack_pop()
    dx = stack_pop()
    IP_delta = (dx, dy)
    return (IP, IP_delta, storage_offset)

def turn_right(IP, IP_delta, storage_offset):
    # ']' : change the IP_delta so that the direction is now rotated 90 degrees to the right
    # (1,0) -> (0,-1)  remember: (0,-1) is actually down, not up
    # (0,-1) -> (-1,0) 
    # (-1,0) -> (0,1) 
    # (0,1) -> (1,0)
    theta = math.pi/2 + math.pi # 270° in radians, 270° cause counterclockwise rotation matrix
    x,y = IP_delta
    nx = (x*math.cos(theta)) - (y*math.sin(theta)) 
    ny = (x*math.sin(theta)) + (y*math.cos(theta)) 
    IP_delta = (int(nx),int(ny))
    return (IP, IP_delta, storage_offset)


def turn_left(IP, IP_delta, storage_offset):
    # '[' : change the IP_delta so that the direction is now rotated 90 degrees to the left
    theta = math.pi/2 # 90° in radians, 90° cause counterclockwise rotation matrix
    x,y = IP_delta
    nx = (x*math.cos(theta)) - (y*math.sin(theta)) 
    ny = (x*math.sin(theta)) + (y*math.cos(theta)) 
    IP_delta = (int(nx),int(ny))
    return (IP, IP_delta, storage_offset)

def compare(IP, IP_delta, storage_offset):
    # 'w' : pop b, pop a, if a<b turn left, if a>b turn right, if a=b go straight
    b = stack_pop()
    a = stack_pop()
    if a<b:
        return turn_left(IP, IP_delta, storage_offset)
    elif a>b:
        return turn_right(IP, IP_delta, storage_offset)
    else:
        return (IP, IP_delta, storage_offset)

def jump_over():
    # ';' : Skip over all instructions till the next ; is reached, takes zero ticks to execute
    pass

def jump_forward(IP, IP_delta, storage_offset):
    # 'j' : pop n, the jump over n spaces in the IP_delta direction
    n = stack_pop()
    for i in range(n):
        IP, IP_delta, storage_offset = move(IP, IP_delta, storage_offset)
    return (IP, IP_delta, storage_offset)

def iterate(IP, IP_delta, storage_offset):
    # 'k' : pop n, find next instruction in IP_delta direction, do that n times, 
    #       takes only one tick
    #n = stack_pop()
    pass


def clear_stack():
    # 'n' : completely empty the stack
    while stack:
       stack_pop()

def fetch_character(IP, IP_delta, storage_offset):
    # "'" : push the value of the next character in IP_delta direction to the 
    #       stack,then skip over that character, takes only one tick, command 
    #       is an apostrophe
    IP, IP_delta, storage_offset = move(IP, IP_delta, storage_offset)
    push_char(funge[IP])
    return move(IP, IP_delta, storage_offset)

def store_character(IP, IP_delta, storage_offset):
    # 's' : pop a value off the stack, write it as a character into position+delta
    c = stack_pop()
    IP, IP_delta, storage_offset = move(IP, IP_delta, storage_offset)
    funge[IP] = chr(c)
    return reverse(*move(*reverse(IP, IP_delta, storage_offset)))

def tick(IP, IP_delta, storage_offset):
    # Execute the instruction at the current IP, then move. 
    # Try to give function extra info, if it doesn't need it, fall back
    # to giving nothing. 
    if _debug:
        print(funge.get(IP, ' '), end = ' ')
    try:
        # the case where the IP, Delta or storage offset don't get effected. 
        ruleset.get(funge.get(IP, ' '), reverse)()
    except TypeError:
        IP, IP_delta, storage_offset = ruleset.get(funge.get(IP, ' '), reverse)(IP, IP_delta, storage_offset)
    return move(IP, IP_delta, storage_offset)

def move(IP, IP_delta, storage_offset):
    # ideally one could use timeit to try different implementations of this
    # function and find which way is fastest, but this seems good enough 
    # for now at least
    if _debug: 
        print('({0}, {1}, {2}) '.format(IP, IP_delta, storage_offset), end = '\n')
    # left right movement first
    if 0 < IP[0] + IP_delta[0] < bounds[0]:
        # normal movement
        IP = (IP[0] + IP_delta[0], IP[1])
    elif IP[0] + IP_delta[0] < 0:
        # going off the left side
        IP = (bounds[0], IP[1])
    else:
        # going off the right side
        IP = (0, IP[1])
    # updown movement next
    if 0 < IP[1] - IP_delta[1] < bounds[1]:
        # normal movement
        IP = (IP[0], IP[1] - IP_delta[1])
    elif IP[1] - IP_delta[1] < 0:
        # going off the top
        IP = (IP[0], bounds[1])
    else:
        # going off the bottom
        IP = (IP[0], 0)
    return (IP, IP_delta, storage_offset)

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
           'r' : reverse,
           'x' : absolute_delta,
           'j' : jump_forward,
           ']' : turn_right,
           '[' : turn_left,
           'w' : compare,
           'n' : clear_stack,
           "'" : fetch_character,
           's' : store_character, 
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


try:
    with open(sys.argv[1], 'r') as f:
        initilize(f.read())
except IndexError:
    sys.exit("Error: expected a Befunge-93 file as a command argument.")
while tick_counter < max_ticks or not IP_list:
    # Run as long as there are IPs and the tick counter hasn't been exceeded.
    for i, IP_tuple in enumerate(IP_list):
        if not string_mode:
            IP_tuple = tick(*IP_tuple)
        else:
            if funge[IP_tuple[0]] == '"': 
                switch_string_mode()
                IP_tuple = move(*IP_tuple)
            else: 
                push_char(funge[IP_tuple[0]])
                IP_tuple = move(*IP_tuple)
        IP_list[i] = IP_tuple
    tick_counter += 1
    #time.sleep(.01)
