import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from fleurdelys.linting import lint_cmake
from fleurdelys.utils import extract_definitions


def test_meta_commands():
    test_file = os.path.join(os.path.dirname(__file__), "meta_commands.cmake")
    with open(test_file, "r") as f:
        source = f.read()

    print("--- LINTING RESULTS ---")
    diagnostics = lint_cmake(source)
    for d in diagnostics:
        severity = "ERROR" if d.severity == 1 else "WARNING"
        print(f"Line {d.range.start.line + 1}: [{severity}] {d.message}")

    print("\n--- DEFINITIONS RESULTS ---")
    defs = extract_definitions(source)

    # Check MY_VAR
    if "MY_VAR" in defs:
        d = defs["MY_VAR"]
        print(f"Variable MY_VAR found at line {d.line + 1}")
        print(f"  Description: {d.description}")
    else:
        print("Variable MY_VAR NOT FOUND!")

    # Check my_func
    if "my_func" in defs:
        d = defs["my_func"]
        print(f"Function my_func found at line {d.line + 1}")
        print(f"  Description: {d.description}")
        print(f"  Signatures: {d.signatures}")
    else:
        print("Function my_func NOT FOUND!")

    # Check default_func
    if "default_func" in defs:
        d = defs["default_func"]
        print(f"Function default_func found at line {d.line + 1}")
        print(f"  Args: {d.args}")
    else:
        print("Function default_func NOT FOUND!")


if __name__ == "__main__":
    test_meta_commands()
