import argparse
import os
from parser import parse_code
from error_detector import ErrorDetector
from suggestion_generator import SuggestionGenerator
from explainer import ErrorExplainer

def main():
    parser = argparse.ArgumentParser(description='AI-Powered Python Debugging Assistant')
    parser.add_argument('file', help='Python file to analyze')
    parser.add_argument('--fix', action='store_true', help='Output auto-fixed code')
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found")
        return

    with open(args.file, 'r') as f:
        code = f.read()

    ast_result = parse_code(code)
    if isinstance(ast_result, str):
        print(f"\nError in {args.file}:\n{ast_result}")
        return

    detector = ErrorDetector()
    explainer = ErrorExplainer()
    suggester = SuggestionGenerator()

    errors = detector.detect_errors(ast_result)

    print(f"\nAnalysis Report for {args.file}")
    print("=" * 50)
    fixed_code = code
    for error in errors:
        print(f"\nLine {error.get('lineno', '?')} - {error['type']}")
        print(f"Error: {error['message']}")
        print(f"Explanation: {explainer.explain_error(error)}")
        print("Suggested Fixes:")
        for i, suggestion in enumerate(suggester.generate_suggestions(error, ast_result), 1):
            print(f"  {i}. {suggestion}")
        if args.fix:
            fixed_code = suggester.apply_fix(fixed_code, error)
    print("\n" + "=" * 50)

    if args.fix:
        print("\n--- Fixed Code ---\n")
        print(fixed_code)
        # Optionally, write to a new file:
        # with open(args.file.replace('.py', '_fixed.py'), 'w') as f:
        #     f.write(fixed_code)

if __name__ == '__main__':
    main()
