import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from src.uhigh import UHighCompiler

class TestUHighCompiler(unittest.TestCase):
    def test_compile_simple(self):
        compiler = UHighCompiler()
        code = 'func main() { var x = 1 }'
        output = compiler.compile(code)
        self.assertIn('main', output)

if __name__ == '__main__':
    unittest.main()
