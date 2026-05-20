import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from cmake_ls.linting import lint_cmake


def verify_implicit_args():
    source = """
function(my_func arg1)
    message(STATUS "ARGC: ${ARGC}")
    message(STATUS "ARGV: ${ARGV}")
    message(STATUS "ARGN: ${ARGN}")
    message(STATUS "ARG1: ${arg1}")
endfunction()

macro(my_macro arg1)
    message(STATUS "ARGC: ${ARGC}")
    message(STATUS "ARGV: ${ARGV}")
    message(STATUS "ARGN: ${ARGN}")
    message(STATUS "ARG1: ${arg1}")
endmacro()

# Outside scope - should warn
message(STATUS "OUTSIDE ARGC: ${ARGC}")
"""
    diagnostics = lint_cmake(source)

    print("Linting results:")
    for d in diagnostics:
        severity = "ERROR" if d.severity == 1 else "WARNING"
        print(f"Line {d.range.start.line + 1}: [{severity}] {d.message}")

    # Expectation:
    # Lines 3, 4, 5 (my_func) - NO warnings
    # Lines 10, 11, 12 (my_macro) - NO warnings
    # Line 17 (outside) - SHOULD warning "Variable 'ARGC' may be undefined."

    warnings = [
        d for d in diagnostics if "ARGC" in d.message and "undefined" in d.message
    ]
    if any(d.range.start.line == 16 for d in warnings):
        print("SUCCESS: ARGC correctly warned outside scope.")
    else:
        print("FAILURE: ARGC did not warn outside scope.")

    internal_warnings = [
        d for d in diagnostics if d.range.start.line in [2, 3, 4, 9, 10, 11]
    ]
    if not internal_warnings:
        print("SUCCESS: No warnings inside function/macro for implicit args.")
    else:
        print("FAILURE: Found warnings inside function/macro:")
        for d in internal_warnings:
            print(f"Line {d.range.start.line + 1}: {d.message}")


if __name__ == "__main__":
    verify_implicit_args()
