from functools import wraps
from os import path
import re
import subprocess
import unittest
import sys


class BefungeInterpreterTests(unittest.TestCase):
    def setUp(self):
        if path.isfile('../befunge_interpreter.py'):
            self.bi_loc = '../befunge_interpreter.py'
            self.cwd = ''
        elif path.isfile('befunge_interpreter.py'):
            self.bi_loc = 'befunge_interpreter.py'
            self.cwd = 'tests/'
        else:
            sys.exit("Could not find befunge_interpreter.py")

    def assert_correct_output(self, test_file = None):
        # moves all boilerplate code to here 
        self.test_file = self.cwd + test_file
        c = subprocess.run(args=["python3", self.bi_loc, self.test_file], stdout=subprocess.PIPE, universal_newlines = True)
        self.assertEqual(c.stdout, self.correct_output(self.test_file))

    def correct_output(self, file):
        """requires "The correct output is: " magic string  in the source code on it's own line"""
        with open(file, 'r') as f:
            source = f.read()
            offset = source.find('The correct output is:')
            return source[offset:].splitlines()[0].split(sep = ': ')[1].strip()


    def test_get(self):
        self.assert_correct_output("get_test.bf")

    def test_up_down_choice(self):
        self.assert_correct_output("up_down_choice_test.bf")

    def test_swap(self):
        self.assert_correct_output("swap_test.bf")

    def test_put(self):
        self.assert_correct_output("put_test.bf")

    def test_basic(self):
        #tests trampoline, duplicate, left right choice, and ascii output
        self.assert_correct_output("test.bf")

    def test_left_right_choice(self):
        self.assert_correct_output("left_right_choice_test.bf")

    def test_greater_than(self):
        self.assert_correct_output("greater_than_test.bf")

    def test_reverse_push_char(self):
        self.assert_correct_output("reverse_push_char_test.bf")

    def test_appropriately_handle_big_numbers(self):
        self.assert_correct_output("int_overflow_test.bf")

    def test_the_reverse_instruction(self):
        self.assert_correct_output("reverse_test.bf")

    def test_unknown_character_handling(self):
        self.assert_correct_output("handle_unknown_chars_well_test.bf")




if __name__ == '__main__':
    unittest.main()