import os
import sys
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from cmake_ls.server import completions
from lsprotocol.types import CompletionParams, TextDocumentIdentifier, Position


class MockDocument:
    def __init__(self, source):
        self.source = source
        self.lines = source.splitlines(keepends=True)


def test_completions():
    source = """function(my_func arg1)
    message(STATUS "${A")
endfunction()
"""
    # Position is on line 1, at the end of "${A"
    # "    message(STATUS \"${A"
    # 01234567890123456789012
    # So index 23 is after "A"

    ls = MagicMock()
    doc = MockDocument(source)
    ls.workspace.get_text_document.return_value = doc

    params = CompletionParams(
        text_document=TextDocumentIdentifier(uri="file:///test.cmake"),
        position=Position(line=1, character=23),
    )

    result = completions(ls, params)

    items = [item.label for item in result.items]
    print(f"Completions found: {items}")

    expected = ["ARGC", "ARGV", "ARGN", "arg1"]
    missing = [e for e in expected if e not in items]

    if not missing:
        print(
            "SUCCESS: All expected implicit arguments and regular arguments found in completions."
        )
    else:
        print(f"FAILURE: Missing completions: {missing}")


if __name__ == "__main__":
    test_completions()
