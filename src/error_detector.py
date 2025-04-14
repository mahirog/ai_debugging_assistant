import ast
import builtins

class ErrorDetector:
    def __init__(self):
        self.defined_vars = set()
        # Use the builtins module for robust detection
        self.builtins = set(dir(builtins))

    def detect_errors(self, ast_node):
        errors = []
        self.defined_vars.clear()
        
        try:
            # First pass: Collect variable assignments
            for node in ast.walk(ast_node):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.defined_vars.add(target.id)

            # Second pass: Detect errors
            for node in ast.walk(ast_node):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    # Use builtins module for correct detection
                    if node.id not in self.defined_vars and node.id not in self.builtins:
                        errors.append({
                            'type': 'NameError',
                            'message': f"Undefined variable '{node.id}'",
                            'lineno': getattr(node, 'lineno', None)
                        })
                
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                    left_type = self._infer_type(node.left)
                    right_type = self._infer_type(node.right)
                    if {left_type, right_type} == {'str', 'int'}:
                        errors.append({
                            'type': 'TypeError',
                            'message': f"Cannot add {left_type} and {right_type}",
                            'lineno': getattr(node, 'lineno', None)
                        })

        except Exception as e:
            errors.append({
                'type': 'InternalError',
                'message': f"Analysis error: {str(e)}",
                'lineno': None
            })

        return errors

    def _infer_type(self, node):
        if isinstance(node, ast.Constant):
            return type(node.value).__name__
        return 'unknown'
