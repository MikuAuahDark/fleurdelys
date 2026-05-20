from pygls.workspace import TextDocument
import lsprotocol.types as lsp


def reproduce():
    doc = TextDocument(
        uri="file:///test.cmake", source="project(foo)\nadd_executable(bar main.c)\n"
    )
    print(f"Lines count: {len(doc.lines)}")

    # Try to access line out of range
    try:
        line = doc.lines[2]
        print(f"Line 2: {line}")
    except IndexError as e:
        print(f"Caught expected IndexError: {e}")
    except Exception as e:
        print(f"Caught unexpected {type(e).__name__}: {e}")

    # The error in traceback was: IndexError: tuple index out of range
    # This specifically means doc.lines is a tuple.
    print(f"doc.lines type: {type(doc.lines)}")


if __name__ == "__main__":
    reproduce()
