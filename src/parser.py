import ast

def parse_code(code_string):
    """
    Parse Python code into an Abstract Syntax Tree (AST)
    
    Args:
        code_string (str): Python source code
        
    Returns:
        ast.AST | str: AST node or error message
    """
    try:
        return ast.parse(code_string)
    except SyntaxError as e:
        return (
            f"SyntaxError: {e.msg}\n"
            f"Line {e.lineno}, Column {e.offset}\n"
            f"Problematic line: {e.text.strip() if e.text else 'Unknown'}"
        )
    except Exception as e:
        return f"Unexpected parsing error: {str(e)}"
