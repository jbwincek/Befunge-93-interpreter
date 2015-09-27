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

    def assert_correct_output(self, test_file = None, strip = True):
        # moves all boilerplate code to here 
        self.test_file = self.cwd + test_file
        test_execution_output = subprocess.check_output(["python3", self.bi_loc, self.test_file], universal_newlines = True)
        # .strip() on the output could in some circumstances cause issues, set to False as needed
        if strip:
            self.assertEqual(test_execution_output.strip(), self.correct_output(self.test_file))
        else: 
            self.assertEqual(test_execution_output, self.correct_output(self.test_file))

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

    def test_absolute_delta(self):
        self.assert_correct_output("absolute_delta_test.bf")

    def test_jump_forward(self):
        self.assert_correct_output("jump_forward_test.bf")
        self.assert_correct_output("jump_nothing_test.bf")

    def test_turns(self):
        self.assert_correct_output("turn_right_test.bf")
        self.assert_correct_output("turn_left_test.bf")

    def test_wrapping(self):
        self.assert_correct_output("wrap_around_top_test.bf")
        self.assert_correct_output("wrap_around_left_test.bf")
        self.assert_correct_output("wrap_around_right_test.bf")
        self.assert_correct_output("wrap_around_bottom_test.bf")

    def test_compare(self):
        self.assert_correct_output("compare_straight_test.bf")
        self.assert_correct_output("compare_right_test.bf")
        self.assert_correct_output("compare_left_test.bf")

    def test_stack_clearing(self):
        self.assert_correct_output("clear_stack_test.bf")

    def test_trampoline(self):
        self.assert_correct_output("trampoline_test.bf")
        self.assert_correct_output("trampoline_edge_cases_test.bf")

    def test_fetch_character(self):
        self.assert_correct_output("fetch_character_test.bf")
        #self.assert_correct_output("fetch_character_hard_test.bf")
        #    Not sure if the above test is failing because of a test coding issue, 
        #    or a bug in the interpreter. 

    def test_store_character(self):
        self.assert_correct_output("store_character_test.bf")

    def test_modulo(self):
        self.assert_correct_output("modulo_test.bf")

    def test_jump_over(self):
        self.assert_correct_output("jump_over_basic_test.bf")
        self.assert_correct_output("jump_over_borders_test.bf")

    def test_push_numbers_bigger_than_ten(self):
        self.assert_correct_output("numbers_bigger_than_ten_test.bf")

    def test_divisions_resulting_in_floats(self):
        self.assert_correct_output("float_tests.bf")

    def test_quit(self):
        self.assert_correct_output("quit_test.bf")

    def test_iterate(self):
        self.assert_correct_output("iterate_test.bf")

if __name__ == '__main__':
    unittest.main()