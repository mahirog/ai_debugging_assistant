import unittest
from src.suggestion_generator import SuggestionGenerator

class TestSuggestionGenerator(unittest.TestCase):
    def setUp(self):
        self.suggester = SuggestionGenerator()

    def test_name_error_suggestions(self):
        error = {'type': 'NameError', 'message': "Undefined variable 'x'", 'lineno': 1}
        suggestions = self.suggester.generate_suggestions(error, None)
        self.assertIsInstance(suggestions, list)
        self.assertTrue(any("variable" in s.lower() for s in suggestions))

    def test_syntax_error_suggestions(self):
        error = {'type': 'SyntaxError', 'message': "invalid syntax", 'lineno': 2}
        suggestions = self.suggester.generate_suggestions(error, None)
        self.assertIsInstance(suggestions, list)
        self.assertTrue(any("colon" in s.lower() or "parentheses" in s.lower() for s in suggestions))

    def test_type_error_suggestions(self):
        error = {'type': 'TypeError', 'message': "Cannot add str and int", 'lineno': 3}
        suggestions = self.suggester.generate_suggestions(error, None)
        self.assertIsInstance(suggestions, list)
        self.assertTrue(any("type" in s.lower() for s in suggestions))

    def test_internal_error_suggestions(self):
        error = {'type': 'InternalError', 'message': "Analysis error", 'lineno': 4}
        suggestions = self.suggester.generate_suggestions(error, None)
        self.assertIsInstance(suggestions, list)
        self.assertTrue(any("review" in s.lower() for s in suggestions))

    def test_unknown_error_type(self):
        error = {'type': 'UnknownError', 'message': "Something went wrong", 'lineno': 5}
        suggestions = self.suggester.generate_suggestions(error, None)
        self.assertIsInstance(suggestions, list)
        self.assertTrue(any("review" in s.lower() for s in suggestions))

if __name__ == '__main__':
    unittest.main()
