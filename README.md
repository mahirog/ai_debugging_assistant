# AI-Powered Python Debugging Assistant

A command-line tool that analyzes Python code, detects common errors, explains them in plain language, and suggests actionable fixes.  
Now with an auto-fix feature for simple errors!

## Features

- **Code Parsing:** Parses Python code into an AST for analysis.
- **Error Detection:** Identifies syntax errors, undefined variables, and basic type errors.
- **Error Explanation:** Provides clear, concise explanations for each detected error.
- **Suggestion Generation:** Offers practical suggestions and code fixes for common errors.
- **Auto-Fix:** Optionally outputs a fixed version of your code for simple errors.
- **Command-Line Interface:** Analyze any Python file directly from your terminal.

## Installation

pip install -r requirements.txt

## Usage

Analyze a Python file and get a detailed error report:

python src/cli.py path/to/your_script.py

To also output the auto-fixed code:

python src/cli.py path/to/your_script.py --fix

## Running Tests

python -m unittest discover tests

## Example

Given this 
`example.py`:

x = 10
print(y)
z = "hello" + 5

def foo()
print("Missing colon")

Run:

python src/cli.py example.py --fix


You will see error reports and a fixed version of your code.


**Happy debugging!**
