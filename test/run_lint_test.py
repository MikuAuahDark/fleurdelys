import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from fleurdelys.linting import lint_cmake


def test():
    test_file = os.path.join(os.path.dirname(__file__), "verification.cmake")
    with open(test_file, "r") as f:
        source = f.read()

    diagnostics = lint_cmake(source)

    print(f"Linting {test_file}:")
    for d in diagnostics:
        severity = "ERROR" if d.severity == 1 else "WARNING"
        print(f"Line {d.range.start.line + 1}: [{severity}] {d.message}")


if __name__ == "__main__":
    test()
