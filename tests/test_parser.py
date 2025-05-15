import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from src.lexer import Lexer
from src.parser import Parser

class TestParser(unittest.TestCase):
    def test_parse_var_decl(self):
        lexer = Lexer('var x = 5')
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        self.assertIsNotNone(program)

if __name__ == '__main__':
    unittest.main()
