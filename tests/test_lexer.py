import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from src.lexer import Lexer

class TestLexer(unittest.TestCase):
    def test_tokenize_var_decl(self):
        lexer = Lexer('var x = 5')
        tokens = lexer.tokenize()
        self.assertTrue(any(t[0] == 'IDENT' and t[1] == 'var' for t in tokens))
        self.assertTrue(any(t[0] == 'IDENT' and t[1] == 'x' for t in tokens))
        self.assertTrue(any(t[0] == 'NUMBER' and t[1] == '5' for t in tokens))

    def test_tokenize_with_whitespace(self):
        code = '   var   y   =   10   '
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertTrue(any(t[0] == 'IDENT' and t[1] == 'y' for t in tokens))
        self.assertTrue(any(t[0] == 'NUMBER' and t[1] == '10' for t in tokens))

    def test_tokenize_with_comment(self):
        code = 'var z = 3 // this is a comment'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertTrue(any(t[0] == 'IDENT' and t[1] == 'z' for t in tokens))
        self.assertTrue(any(t[0] == 'NUMBER' and t[1] == '3' for t in tokens))
        # Ensure comment is ignored
        self.assertFalse(any('comment' in str(t[1]) for t in tokens))

    def test_tokenize_invalid_token(self):
        code = 'var $illegal = 1'
        lexer = Lexer(code)
        with self.assertRaises(Exception):
            lexer.tokenize()

    def test_tokenize_empty_input(self):
        lexer = Lexer('')
        tokens = lexer.tokenize()
        self.assertEqual(tokens, [])

if __name__ == '__main__':
    unittest.main()
