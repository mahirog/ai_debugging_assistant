import unittest
import ast
from src.error_detector import ErrorDetector

class TestErrorDetector(unittest.TestCase):
    def setUp(self):
        self.detector = ErrorDetector()

    def test_undefined_variable(self):
        code = "print(x)"
        tree = ast.parse(code)
        errors = self.detector.detect_errors(tree)
        self.assertTrue(any(e['type'] == 'NameError' for e in errors))
        self.assertTrue(any("Undefined variable" in e['message'] for e in errors))

    def test_no_error(self):
        code = "x = 5\nprint(x)"
        tree = ast.parse(code)
        errors = self.detector.detect_errors(tree)
        self.assertEqual(errors, [])

    def test_type_error(self):
        code = 'a = "hello" + 5'
        tree = ast.parse(code)
        errors = self.detector.detect_errors(tree)
        self.assertTrue(any(e['type'] == 'TypeError' for e in errors))
        self.assertTrue(any("Cannot add" in e['message'] for e in errors))

    def test_multiple_errors(self):
        code = 'print(y)\nz = "foo" + 3'
        tree = ast.parse(code)
        errors = self.detector.detect_errors(tree)
        error_types = [e['type'] for e in errors]
        self.assertIn('NameError', error_types)
        self.assertIn('TypeError', error_types)

if __name__ == '__main__':
    unittest.main()
