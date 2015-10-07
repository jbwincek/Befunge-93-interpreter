import functools as ft
import math
import time
import random
import sys

"""
Befunge-98 Interpreter
"""


stack = []
IP_list = []
bounds = (79,79)
funge = {}
string_mode = False
max_ticks = 400000
tick_counter = 0
_debug = False

class IP_state:
    def __init__(self,
                location = (0,0),
                delta = (1,0),
                storage_offset = (0,0),
                active = True,
                string_mode = False,):
        self.location = location
        self.delta = delta
        self.storage_offset = storage_offset
        self.active = active
        self.string_mode = string_mode
    
    def move(self):
        if _debug: 
            print(' IP:{0}, IP_delta:{1}, S.O.:{2} Stack: {3}'
                   .format(self.location, self.delta, self.storage_offset, stack), end = '\n')
        # left right movement first
        if 0 < self.location[0] + self.delta[0] < bounds[0]:
            # normal movement
            self.location = (self.location[0] + self.delta[0], self.location[1])
        elif self.location[0] + self.delta[0] < 0:
            # going off the left side
            self.location = (bounds[0], self.location[1])
        else:
            # going off the right side
            self.location = (0, self.location[1])
        # updown movement next
        if 0 < self.location[1] - self.delta[1] < bounds[1]:
            # normal movement
            self.location = (self.location[0], self.location[1] - self.delta[1])
        elif self.location[1] - self.delta[1] < 0:
            # going off the top
            self.location = (self.location[0], bounds[1])
        else:
            # going off the bottom
            self.location = (self.location[0], 0)

    def reverse(self):
        self.delta = tuple([-d for d in self.delta])

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
    a = stack_pop()
    b = stack_pop()
    if not a: 
        ask_num()
    else: 
        c = int(b) // int(a)
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

def change_direction(new_direction, IP):
    if new_direction in ['right', 'left', 'up', 'down']:
        if new_direction == 'right':
            IP.delta = (1, 0)
        elif new_direction == 'left':
            IP.delta = (-1, 0)
        elif new_direction == 'up':
            IP.delta = (0, 1)
        elif new_direction == 'down':
            IP.delta = (0, -1)
        return IP
    else:
        raise KeyError

def random_direction(IP):
    # '?' : Start moving in a random cardinal direction
    return change_direction(random.choice(['right', 'left', 'up', 'down']), IP)

def left_right_choice(IP):
    # '_' : Pop a value; move right if value=0, left otherwise
    if stack_pop():
        return change_direction('left', IP) 
    else:
        return change_direction('right', IP)

def up_down_choice(IP):
    # '|' : Pop a value; move down if value=0, up otherwise
    if stack_pop():
        return change_direction('up', IP)
    else:
        return change_direction('down', IP)

def switch_string_mode(IP):
    # '"' : Start string mode: push each character's ASCII value all the way to the next "
    #       yes, '"' does indeed work as intended, even though it looks fugly as hell
    IP.string_mode = not IP.string_mode
    return IP

def duplicate():
    # ':' : Duplicate value on top of the stack
        value = stack_pop()
        stack.append(value)
        stack.append(value)

def swap():
    # '\' : Swap two values on top of the stack
    # listed in the instruction dictionary as '\\'
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

def trampoline(IP):
    # '#' : Trampoline: Skip next cell
    IP.move()
    return IP
    

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

def end_IP(IP):
    # end the current IP, if the last IP then call leave()
    IP.active = False
    return IP

def push_num(num):
    stack.append(int(num))

def push_char(char):
    stack.append(ord(char))

def reverse(IP):
    # 'r' : Multiply the IP_delta by -1
    IP.reverse()
    return IP

def absolute_delta(IP):
    # 'x' : Pop dy, pop dx, set IP_delta to (dx,dy)
    dy = stack_pop()
    dx = stack_pop()
    IP.delta = (dx, dy)
    return IP

def turn_right(IP):
    # ']' : change the IP_delta so that the direction is now rotated 90 degrees to the right
    # (1,0) -> (0,-1)  remember: (0,-1) is actually down, not up
    # (0,-1) -> (-1,0) 
    # (-1,0) -> (0,1) 
    # (0,1) -> (1,0)
    theta = math.pi/2 + math.pi # 270° in radians, 270° cause counterclockwise rotation matrix
    x,y = IP.delta
    nx = (x*math.cos(theta)) - (y*math.sin(theta)) 
    ny = (x*math.sin(theta)) + (y*math.cos(theta)) 
    IP.delta = (int(nx),int(ny))
    return IP


def turn_left(IP):
    # '[' : change the IP_delta so that the direction is now rotated 90 degrees to the left
    theta = math.pi/2 # 90° in radians, 90° cause counterclockwise rotation matrix
    x,y = IP.delta
    nx = (x*math.cos(theta)) - (y*math.sin(theta)) 
    ny = (x*math.sin(theta)) + (y*math.cos(theta)) 
    IP.delta = (int(nx),int(ny))
    return IP

def compare(IP):
    # 'w' : pop b, pop a, if a<b turn left, if a>b turn right, if a=b go straight
    b = stack_pop()
    a = stack_pop()
    if a<b:
        return turn_left(IP)
    elif a>b:
        return turn_right(IP)
    else:
        return IP

def jump_over(IP):
    # ';' : Skip over all instructions till the next ; is reached, takes zero ticks to execute
    IP.move()
    while funge.get(IP.location, '') != ';':
        IP.move()
    return IP
 
def jump_forward(IP):
    # 'j' : pop n, the jump over n spaces in the IP_delta direction
    n = stack_pop()
    for i in range(n):
        IP.move()
    return IP

def iterate(IP):
    # 'k' : pop n, find next instruction in IP_delta direction, do that n times, 
    #       takes only one tick
    n = stack_pop()
    IP.move()
    while funge.get(IP.location, ' ') == ' ':
        IP.move()
    for i in range(n):
        IP = op(IP)
    return IP

def clear_stack():
    # 'n' : completely empty the stack
    while stack:
       stack_pop()

def fetch_character(IP):
    # "'" : push the value of the next character in IP_delta direction to the 
    #       stack,then skip over that character, takes only one tick, 
    #       instruction is an apostrophe.
    IP.move()
    push_char(funge.get(IP.location, ''))
    IP.move()
    return IP

def store_character(IP):
    # 's' : pop a value off the stack, write it as a character into position+delta
    c = stack_pop()
    IP.move()
    funge[IP.location] = chr(c)
    IP.reverse()
    IP.move()
    IP.reverse()
    return IP

def op(IP, funge = funge):
    try:
        # the case where the IP, Delta or storage offset don't get effected.
        # It is significantly quicker to do this with a try/except clause instead 
        # of using len(inspect.signature(callable).parameters) - I checked. 
        ruleset.get(funge.get(IP.location, ' '), reverse)()
    except TypeError:
        IP = ruleset.get(funge.get(IP.location, ' '), reverse)(IP)
    return IP

def tick(IP):
    # 
    if _debug:
        print(funge.get(IP.location, ' '), end = ' ')
    IP = op(IP)
    IP.move()
    return IP

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
           '@' : end_IP,
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
           ';' : jump_over, 
           'q' : quit,
           'k' : iterate,
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
           'a' : ft.partial(push_num, 10),
           'b' : ft.partial(push_num, 11),
           'c' : ft.partial(push_num, 12),
           'd' : ft.partial(push_num, 13),
           'e' : ft.partial(push_num, 14),
           'f' : ft.partial(push_num, 15),
           }

starter_IP = IP_state()
IP_list.append(starter_IP)
try:
    with open(sys.argv[1], 'r') as f:
        initilize(f.read())
except IndexError:
    sys.exit("Error: expected a Befunge-98 file as a command argument.")
while IP_list and tick_counter < max_ticks:
    # Run as long as there are IPs and the tick counter hasn't been exceeded.
    for i, IP in enumerate(IP_list):
        if IP.active:
            if not IP.string_mode:
                IP = tick(IP)
            else:
                if funge[IP.location] == '"': 
                    switch_string_mode(IP)
                    IP.move()
                else: 
                    push_char(funge[IP.location])
                    IP.move()
            IP_list[i] = IP
    tick_counter += 1
    #time.sleep(.01)
