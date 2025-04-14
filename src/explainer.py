class ErrorExplainer:
    """
    Provides human-readable explanations for detected Python errors.
    """

    _error_explanations = {
        # Syntax errors
        'SyntaxError': {
            'generic': (
                "Invalid Python syntax. Common causes include:\n"
                "- Missing colons at the end of compound statements (if/for/while/def)\n"
                "- Mismatched parentheses, brackets, or braces\n"
                "- Incorrect indentation levels"
            ),
            'EOL': "Unclosed string literal or mismatched quotes",
            'invalid syntax': "Unexpected token or malformed expression",
        },
        
        # Name resolution errors
        'NameError': {
            'generic': (
                "Undefined variable or function name. Possible causes:\n"
                "- Typo in the variable/function name\n"
                "- Using a variable before assignment\n"
                "- Forgetting to import required modules"
            ),
        },

        # Type errors
        'TypeError': {
            'generic': (
                "Operation on incompatible data types. Common issues:\n"
                "- Mixing different types (e.g., str + int)\n"
                "- Incorrect function arguments\n"
                "- Invalid method calls for an object type"
            ),
            'unsupported operand': "Invalid operation between these data types",
        },

        # Internal analyzer errors
        'InternalError': (
            "An internal analysis error occurred. This might indicate:\n"
            "- Edge case not handled by the analyzer\n"
            "- Complex code structure beyond current capabilities"
        ),

        # Default fallback
        'default': (
            "An error occurred that needs manual review. Check:\n"
            "- Code logic around the reported line\n"
            "- External dependencies and imports\n"
            "- Python version compatibility"
        ),
    }

    def explain_error(self, error: dict) -> str:
        """
        Generate a natural language explanation for a detected error.
        
        Args:
            error (dict): Error dictionary containing:
                - 'type': str (error category)
                - 'message': str (specific error message)
                - 'lineno': int (line number)

        Returns:
            str: Formatted explanation with troubleshooting tips
        """
        error_type = error.get('type', 'UnknownError')
        error_msg = error.get('message', '').lower()
        explanation = []

        # Get base explanation
        base = self._error_explanations.get(error_type, self._error_explanations['default'])
        if isinstance(base, dict):
            base_explanation = base.get('generic', base.get(error_msg, base[next(iter(base))]))
        else:
            base_explanation = base

        explanation.append(f"**{error_type} Explanation**")
        explanation.append(base_explanation)

        # Add context-specific troubleshooting
        explanation.append("\n**Troubleshooting Steps:**")
        explanation.append(self._get_troubleshooting_steps(error_type, error_msg))

        return '\n'.join(explanation)

    def _get_troubleshooting_steps(self, error_type: str, error_msg: str) -> str:
        """Generate context-aware troubleshooting steps"""
        steps = []
        
        if error_type == 'NameError':
            steps.append("- Check spelling and capitalization of variable names")
            steps.append("- Verify the variable is defined before use")
            steps.append("- Check import statements for missing modules")

        elif error_type == 'SyntaxError':
            steps.append("- Review the line for missing punctuation (:, () [] {})")
            steps.append("- Check for incomplete multi-line statements")
            steps.append("- Validate indentation levels (4 spaces per level)")

        elif error_type == 'TypeError':
            steps.append("- Print variable types before the operation")
            steps.append("- Use type conversion functions (int(), str(), etc.)")
            steps.append("- Check function/method parameter requirements")

        else:
            steps.append("- Review the code around the reported line")
            steps.append("- Search for similar errors in Python documentation")
            steps.append("- Simplify complex expressions into smaller parts")

        return '\n'.join(f"• {step}" for step in steps)
