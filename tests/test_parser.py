import unittest
import ast
from src.parser import parse_code

class TestParser(unittest.TestCase):
    def test_valid_code(self):
        code = "x = 1 + 2"
        result = parse_code(code)
        # Should return an AST object, not a string
        self.assertIsInstance(result, ast.AST)

    def test_syntax_error(self):
        code = "x = "
        result = parse_code(code)
        # Should return a string containing 'SyntaxError'
        self.assertIsInstance(result, str)
        self.assertIn("SyntaxError", result)

    def test_multiline_valid_code(self):
        code = """
def foo():
    return 42
"""
        result = parse_code(code)
        self.assertIsInstance(result, ast.AST)

    def test_multiline_syntax_error(self):
        code = """
def foo()
    return 42
"""
        result = parse_code(code)
        self.assertIsInstance(result, str)
        self.assertIn("SyntaxError", result)

if __name__ == '__main__':
    unittest.main()
