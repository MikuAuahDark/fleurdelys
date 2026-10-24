# Annotations

Annotations use contiguous full-line `##` comments. One optional space after
`##` is removed; indentation and empty `##` lines are preserved as Markdown.
`###` lines are ignored. A blank source line, ordinary comment, or intervening
command separates documentation from its declaration. Bracket comments and
strings cannot contain annotations.

```cmake
## Perform mathematical computation using double-precision floating-point.
##
## **Warning**: This is a Cartethyia extension!
##
## function(math FEXPR <?expression> [PRECISION <DEFAULT|FULL>])
```

Function names are case-insensitive, with their declared spelling retained.
All unprefixed signature tokens are case-sensitive literals. `?name` accepts
any argument; `&name` also marks a possible variable definition. Angle brackets
require their contents; square brackets make their contents optional as a unit.
Groups can nest. `|` separates literal alternatives, with optional surrounding
whitespace. `<FOO>` is equivalent to `FOO`.

`<?item>...` consumes one or more arguments; `[?item]...` consumes zero or more.
Repetition applies to the immediately preceding group, which must consume at
least one argument on each repetition. Alternatives currently contain literals
only. Malformed declarations produce LSP warnings.

```cmake
## Set a variable in the current scope.
## function(set <&var> [?value])
## Set a variable in the parent scope.
## function(set <?var> <?value> PARENT_SCOPE)
```

Multiple declarations of the same function add overloads, each with its own
documentation. Explicit annotations replace signatures inferred from executable
`function()` or `macro()` declarations and built-in signatures. Implementation
parameters and implicit arguments remain visible inside their bodies.

Literal matches take precedence over generic placeholders. Dynamic arguments
such as `${mode}` are uncertain matches. Variable effects require agreement
among equally specific matching overloads; completions combine the possibilities
from all viable overloads, including partially entered groups.

`&name` suggests existing visible variables. It defines a variable after a
successful call only for an unquoted literal variable name matching
`[A-Za-z_][A-Za-z0-9_.-]*`. Quoted strings, bracket arguments, and names containing
expansions do not create inferred variables. An existing definition in the
destination scope is retained; a local definition can shadow an outer variable.
Executable `set()` and `unset()` retain their built-in scope handling.

Variables can be documented without executing a command:

```cmake
## If set to 1, the script is running under the Cartethyia interpreter.
## set(CARTETHYIA 1)
```

Documentation immediately preceding an executable `set()` also documents its
variable. Annotations are local to the file and enclosing scope unless imported:

```cmake
## include(path/to/annotation.cmake)
include("path/to/helpers.cmake")
```

Both forms resolve paths relative to the containing file and load transitive
includes. Cycles and repeated imports in a scope are guarded. Function-local
symbols stay local. Open editor buffers take precedence over saved files.
Include paths can use known variable values and `${CMAKE_CURRENT_LIST_DIR}`;
unresolved dynamic paths do not produce definite missing-file warnings.
There is no preload mechanism yet.

The former `##cmake-ls:` directives are no longer supported.
