import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from src import build

class TestBuild(unittest.TestCase):
    def test_build_project_exists(self):
        self.assertTrue(hasattr(build, 'build_project'))

if __name__ == '__main__':
    unittest.main()
