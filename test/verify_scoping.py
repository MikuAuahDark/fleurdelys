from cmake_ls.linting import lint_cmake
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

source = """
set(GLOBAL_VAR 1)

function(myfunc ARG1)
  set(LOCAL_VAR 2)
  set(GLOBAL_VAR 3 PARENT_SCOPE)
  message(${ARG1})
  message(${LOCAL_VAR})
endfunction()

myfunc(test)
message(${LOCAL_VAR}) # Should warn
message(${GLOBAL_VAR}) # Should be fine

macro(mymacro MARG1)
  set(MACRO_VAR 4)
  message(${MARG1})
endmacro()

mymacro(mtest)
message(${MACRO_VAR}) # Should be fine (leaks)
message(${MARG1}) # Should warn (doesn't leak)

block()
  set(BLOCK_VAR 5)
endblock()
message(${BLOCK_VAR}) # Should warn
"""

diagnostics = lint_cmake(source)
for d in diagnostics:
    print(f"Line {d.range.start.line + 1}: {d.message}")
