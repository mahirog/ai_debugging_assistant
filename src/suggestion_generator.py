import re

class SuggestionGenerator:
    def generate_suggestions(self, error, ast_node):
        suggestions = []
        error_type = error.get('type', '')
        
        if error_type == 'NameError':
            suggestions.extend([
                "Check variable spelling",
                "Add missing variable assignment",
                "Verify imports for external names"
            ])
        elif error_type == 'SyntaxError':
            suggestions.extend([
                "Check missing colons/parentheses",
                "Verify indentation levels",
                "Look for incomplete statements"
            ])
        elif error_type == 'TypeError':
            suggestions.extend([
                "Use explicit type conversion",
                "Check variable types before operation",
                "Consider alternative data structures"
            ])
        else:
            suggestions.append("Review code logic around reported line")
            
        return suggestions

    def apply_fix(self, code, error):
        """
        Returns a version of the code with the suggested fix applied for the given error.
        Only handles simple cases for demonstration.
        """
        lines = code.splitlines()
        lineno = error.get('lineno')
        if error['type'] == 'NameError':
            # Insert a variable assignment before the line
            var_name = re.findall(r"'(.+)'", error['message'])
            if var_name and lineno:
                lines.insert(lineno - 1, f"{var_name[0]} = 0  # Auto-fix: added missing variable")
        elif error['type'] == 'TypeError':
            # Try to convert int to str in string concatenation
            if lineno:
                line = lines[lineno - 1]
                # Replace + with + str() if possible
                fixed_line = re.sub(r'(".*?") \+ (\w+)', r'\1 + str(\2)', line)
                lines[lineno - 1] = fixed_line + "  # Auto-fix: type conversion"
        elif error['type'] == 'SyntaxError':
            # Try to add a colon at the end if missing
            if lineno:
                line = lines[lineno - 1]
                if not line.strip().endswith(':'):
                    lines[lineno - 1] = line.rstrip() + ':' + "  # Auto-fix: added missing colon"
        # Add more rules as needed
        return '\n'.join(lines)
