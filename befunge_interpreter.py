import argparse
import copy
import functools as ft
import math
import time
import random
import sys

"""
Befunge-98 Interpreter
"""


stack = []
stack_of_stacks = [stack]
IP_list = []
bounds = (79,79)
funge = {}
string_mode = False
max_ticks = 50000
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


""" --------------------------- Instructions ------------------------------- """ 

def absolute_delta(IP):
    # 'x' : Pop dy, pop dx, set IP_delta to (dx,dy)
    dy = stack_pop()
    dx = stack_pop()
    IP.delta = (dx, dy)
    return IP

def add():
    # '+' : Addition: Pop a and b, then push a+b
    stack.append(stack_pop() + stack_pop())

def ask_char():
    # '~' : Ask user for a character and push its ASCII value
    #      doesn't handle bad input
    push_char(input())

def ask_num():
    # '&' : Ask user for a number and push it
    #     doesn't handle bad input
    push_num(input())

def begin_block(IP):
    # '{' : Begin bock, pop a cell, n, push a new stack to the stack of stacks
    #       then transfer n elements from the SOSS to the TOSS. Then push storage
    #       as a vector to the SOSS, and sets the new storage offset to the
    #       location to be executed next by the IP (position + delta), it copies
    #       these elements as a block so order is preserved
    #       If n is zero, no elements are transfrred
    #       If n  is negative, |n| zeros are pushed onto the SOSS. 
    pass

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

def clear_stack():
    # 'n' : completely empty the stack
    while stack:
       stack_pop()

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

def discard():
    # '$' : Pop value from the stack and discard it
    stack_pop()

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

def duplicate():
    # ':' : Duplicate value on top of the stack
        value = stack_pop()
        stack.append(value)
        stack.append(value)

def end_block(IP): 
    # '}' : End block, pop a cell, n, pops a vector off the SOSS which it assigns
    #       to the storage offset, then transfers n elements (as a block) from the
    #       TOSS to the SOSS, then pops the top stack of of the stack of stacks. 
    #       If n is zero, no elemets are transferred
    #       if N is negative, |n| cells are popped off the (original) SoSS
    pass


def end_IP(IP):
    # '@' : end the current IP, if the last IP then call leave()
    IP.active = False
    return IP


def fetch_character(IP):
    # "'" : push the value of the next character in IP_delta direction to the 
    #       stack,then skip over that character, takes only one tick, 
    #       instruction is an apostrophe.
    IP.move()
    push_char(funge.get(IP.location, ''))
    IP.move()
    return IP

def file_input(IP):
    # 'i' : pop a null-terminated (0"gnirts") string for the filename, followed
    #       by a flags cell, and a vector Va of where to operate. 
    #       If the file can be opened, it's inserted at Va then closed 
    #       immediately, else i acts like reverse (r).
    #       Two vectors—Vb and Va—are pushed onto the stack, Va being relative
    #       to storage offset, Vb being the size of the inputed file.
    #       Flags cell even: insert using end of line characters to start new 
    #                        lines, like you'd expect
    #       Flags cell odd:  insert input as binary, storing EOL and FF sequences
    #                        in Funge-space (FF = formfeed: U+000C)
    pass

def file_output(IP):
    # 'o' : pop a null terminated string for the filename, then a flags cell,
    #       then vector Va describing the least point, then Vb describing the
    #       size of the space to output. If file cannot be opened or written to
    #       act as reverse (r).
    #       Flags cell odd: linear text file, ignore spaces before each EOL, and
    #       any extra EOLs at the end. 
    pass

def get(IP):
    # 'g' : A "get" call (a way to retrieve data in storage). 
    #       Pop y and x, apply storage offset, then push ASCII value 
    #       of the character at that position in the program. 
    #       If (x,y) is out of bounds, push 0. 
    y = stack_pop() + IP.storage_offset[1]
    x = stack_pop() + IP.storage_offset[0]
    stack.append(ord(funge[(x,y)]))
    return IP

#def get_system_info(IP):
#    pass

def greater_than():
    # '`' : Greater than: Pop a and b, then push 1 if b>a, otherwise zero.
    a = stack_pop()
    b = stack_pop()
    if b>a:
        stack.append(1)
    else:
        stack.append(0)

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

def jump_forward(IP):
    # 'j' : pop n, the jump over n spaces in the IP_delta direction
    n = stack_pop()
    for i in range(n):
        IP.move()
    return IP

def jump_over(IP):
    # ';' : Skip over all instructions till the next ; is reached, takes zero ticks to execute
    IP.move()
    while funge.get(IP.location, '') != ';':
        IP.move()
    return IP

def left_right_choice(IP):
    # '_' : Pop a value; move right if value=0, left otherwise
    if stack_pop():
        return change_direction('left', IP) 
    else:
        return change_direction('right', IP)

def logical_not():
    # '!'' : Logical NOT: Pop a value. If the value is zero, push 1; otherwise, push zero.
    if not stack_pop(): 
        stack.append(1)
    else:
        stack.append(0)

def modulo():
    # '%' : Modulo: Pop a and b, then push the remainder of the integer division of b/a.
    a = stack_pop()
    b = stack_pop()
    stack.append(b%a)

def multiply():
    # '*' : Multiplication: Pop a and b, then push a*b
    stack.append(stack_pop() * stack_pop())

def nop():
    # 'z' : do nothing (useful for concurrent timing)
    pass

def print_ASCII():
    # ','   Pop value and output as an ASCII character
    print(chr(stack_pop()), end = '', flush = True)
    
def print_int():
    # '.' : Pop value and output as an integer
    print(stack_pop(), end = ' ', flush = True)

def push_char(char):
    stack.append(ord(char))

def push_num(num):
    stack.append(int(num))

def put(IP):
    global funge
    # 'p' : A "put" call (a way to store a value for later use). 
    #       Pop y, x, and v, apply the storage offset, then change
    #       the character at the specified location in the funge space 
    #       to the character with ASCII value v. 
    y = stack_pop() + IP.storage_offset[1]
    x = stack_pop() + IP.storage_offset[0]
    v = stack_pop()
    funge[(x,y)] = chr(v)
    return IP

def random_direction(IP):
    # '?' : Start moving in a random cardinal direction
    return change_direction(random.choice(['right', 'left', 'up', 'down']), IP)

def reverse(IP):
    # 'r' : Multiply the IP_delta by -1
    IP.reverse()
    return IP

def split(IP):
    # 't' : duplicates current IP, executes child before parent, reversed delta
    #       though. 
    global IP_list
    child_IP = reverse(copy.deepcopy(IP))
    child_IP.move()
    #child_IP = tick(child_IP, should_move = True)
    IP_list.append(child_IP)
    return IP

def stack_pop():
    try:
        return stack.pop()
    except IndexError:
        return 0


def stack_under_stack(IP):
    # 'u' : Pops n, transfers n cells from SOSS to TOSS, one at a time, so order
    #       is reversed.
    #       If there is no SOSS, instruction sould reverse (r)
    #       If n is negative, |n| cells are transferred from TOSS to SOSS
    #       If count is zero, pass. 
    pass

def store_character(IP):
    # 's' : pop a value off the stack, write it as a character into position+delta
    c = stack_pop()
    IP.move()
    funge[IP.location] = chr(c)
    IP.reverse()
    IP.move()
    IP.reverse()
    return IP

def subtract():
    # '-' : Subtraction: Pop a and b, then push b-a
    a = stack_pop()
    b = stack_pop()
    stack.append(b-a)

def swap():
    # '\' : Swap two values on top of the stack
    # listed in the instruction dictionary as '\\'
    a = stack_pop()
    b = stack_pop()
    stack.append(a)
    stack.append(b)

def switch_string_mode(IP):
    # '"' : Start string mode: push each character's ASCII value all the way to the next "
    #       yes, '"' does indeed work as intended, even though it looks fugly as hell
    IP.string_mode = not IP.string_mode
    return IP

def trampoline(IP):
    # '#' : Trampoline: Skip next cell
    IP.move()
    return IP

def turn_left(IP):
    # '[' : change the IP_delta so that the direction is now rotated 90 degrees to the left
    theta = math.pi/2 # 90° in radians, 90° cause counterclockwise rotation matrix
    x,y = IP.delta
    nx = (x*math.cos(theta)) - (y*math.sin(theta)) 
    ny = (x*math.sin(theta)) + (y*math.cos(theta)) 
    IP.delta = (int(nx),int(ny))
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

def up_down_choice(IP):
    # '|' : Pop a value; move down if value=0, up otherwise
    if stack_pop():
        return change_direction('up', IP)
    else:
        return change_direction('down', IP)



""" ---------------------- interpreter functions --------------------------- """

def op(IP, funge = funge):
    try:
        # the case where the IP, Delta or storage offset don't get effected.
        # It is significantly quicker to do this with a try/except clause instead 
        # of using len(inspect.signature(callable).parameters) - I checked. 
        ruleset.get(funge.get(IP.location, ' '), reverse)()
    except TypeError:
        IP = ruleset.get(funge.get(IP.location, ' '), reverse)(IP)
    return IP

def tick(IP, should_move = True):
    # 
    if _debug:
        print(funge.get(IP.location, ' '), end = ' ')
    IP = op(IP)
    if should_move:
        IP.move()
    return IP

def initilize(input_string):
    global funge
    global stack
    global bounds
    stack = []
    input_lines = input_string.splitlines()
    file_height = len(input_lines)
    if file_height > bounds[1]:
        bounds = (bounds[0], file_height)
    for y, line in enumerate(input_lines):
        line_length = len(line)
        if line_length > bounds[0]:
            bounds = (line_length, bounds[1])
        for x, letter in enumerate(line):
            funge[(x,y)] = letter

def funge_print(fungespace):
    output_string = '\n'
    for y in range(bounds[1]):
        for x in range(bounds[0]):
            output_string+=str(fungespace.get((x,y),' '))
        output_string+='\n'
    print(output_string.rstrip())

def gnirts():
    # pop a null terminated string off the stack and return it
    output = ''
    popping = True
    while popping:
        character = stack_pop()
        if character == 0:
            break
        else:
            output += chr(character)
    return output


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
           't' : split,
           'z' : nop,
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

def run():
    global tick_counter
    starter_IP = IP_state()
    IP_list.append(starter_IP)
    # try:
    #     with open(sys.argv[1], 'r') as f:
    #         initilize(f.read())
    # except IndexError:
    #     sys.exit("Error: expected a  as a command argument.")

    parser = argparse.ArgumentParser()
    parser.add_argument('source_file', help = 'Befunge-98 source code file')
    parser.add_argument('-d', '--debug', help = 'run in debug mode', action = 'store_true')
    args = parser.parse_args()
    _debug = args.debug

    try:
        with open(args.source_file, 'r', errors = 'ignore') as f:
            initilize(f.read())
    except FileNotFoundError:
        exit("Error: problem loading {}".format(args.source_file))
    except UnicodeDecodeError:
        exit("Error: problem decoding the unicode")

    while IP_list and tick_counter < max_ticks:
        # Run as long as there are IPs and the tick counter hasn't been exceeded.
        if _debug:
            print("Tick: {}".format(tick_counter))
        for i, IP in enumerate(IP_list):
            if IP.active:
                if not IP.string_mode:
                    IP = tick(IP)
                else:
                    if funge.get(IP.location, ' ') == '"': 
                        switch_string_mode(IP)
                        IP.move()
                    else: 
                        push_char(funge.get(IP.location, ' '))
                        IP.move()
            else:
                IP_list.pop(i)
        tick_counter += 1
        #time.sleep(.01)


if __name__ == '__main__':
    run()