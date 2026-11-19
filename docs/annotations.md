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
any argument; `&name` marks a possible variable definition, and `:name` suggests
visible variable names without defining one. Angle brackets
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

`&name` suggests visible variable names and defines a variable after a
successful call only for an unquoted literal variable name matching
`[A-Za-z_][A-Za-z0-9_.-]*`. Quoted strings, bracket arguments, and names containing
expansions do not create inferred variables. An existing definition in the
destination scope is retained; a local definition can shadow an outer variable.
Executable `set()` and `unset()` retain their built-in scope handling.

Named symbol namespaces are created implicitly by annotations. They are separate
from language variables; no namespace name (including `v` or `t`) is reserved.
`namespace&name` defines a symbol, while `namespace:name` suggests known symbols
without requiring the argument to name an existing symbol. Definition placeholders
also suggest existing names from their namespace; `:` only suggests names.

```cmake
## function(add_executable <t&target> [WIN32] [?src]...)
## function(target_compile_definitions <t:target> <?visibility> [?definition]...)
```

Namespace names are case-sensitive identifiers (`[A-Za-z_][A-Za-z0-9_]*`).
Symbols are global once analyzed, including definitions inside functions and
imports. LSP suggestions combine symbols from documents seen during the session,
independently of cursor position. Closed documents retain their last seen source;
edits to open documents remove stale names. Symbol definitions accept nonempty
unquoted literal arguments, including names such as `package::target`, but not
expansions, bracket arguments, or escaped names. Variable definitions retain
their stricter name grammar and scope rules. Equally specific matching overloads
must agree on both namespace and argument before defining a symbol.

Symbols can also be declared directly, with preceding Markdown documentation:

```cmake
## Main application target.
## symbol(t app)
## Imported dependency.
## symbol(t package::library)
```

`symbol(namespace name)` requires exactly two unquoted literal arguments. It
creates the namespace implicitly and makes the symbol globally available to
both `namespace:` and `namespace&` suggestions. A direct declaration supplies
the symbol's documentation and definition location, replacing an earlier entry
with the same namespace and name. Use `## set(...)` for language variables.

Variables can be documented without executing a command:

```cmake
## If set to 1, the script is running under the Cartethyia interpreter.
## set(CARTETHYIA 1)
```

Namespaced variables use `set(NAMESPACE{NAME} [value])`:

```cmake
## Installation directory.
## set(CACHE{CMAKE_INSTALL_PREFIX})
## System search path.
## set(ENV{PATH})
## Custom variable namespace.
## set(FOO{BAR} example)
```

Each declaration implicitly creates its variable namespace, including `CACHE`.
Namespace names are case-sensitive identifiers (`[A-Za-z_][A-Za-z0-9_]*`);
variable names use `[A-Za-z_][A-Za-z0-9_.-]*`. These declarations provide
completion, hover documentation, and definition navigation for `$FOO{BAR}`.
They follow ordinary variable annotation scope and import rules, remain separate
from named symbol namespaces, and do not define an ordinary `${BAR}` variable.
Later declarations in the same scope replace earlier ones. Namespaced values
are recorded as annotation metadata; they are not expanded in include paths.
Declaring `ENV{PATH}` does not read or modify the process environment.

Variable catalogues come entirely from loaded annotations. Core supplies list-file
context and general process environment names (`ENV{PATH}` and
`ENV{LD_LIBRARY_PATH}`). The optional CMake pack supplies project, build, platform
and compiler variables, CMake environment inputs, and documented `CACHE` entries.
Disabling that pack removes its entries from completion, hover, navigation and
undefined-variable exemptions. The ordinary `${...}` namespace is always valid;
other variable namespaces are recognized when a visible declaration defines them.

Documentation immediately preceding an executable `set()` also documents its
variable. Function and variable annotations are local to the file and enclosing
scope unless imported; named symbols remain global:

```cmake
## include(path/to/annotation.cmake)
include("path/to/helpers.cmake")
```

Both forms resolve paths relative to the containing file and load transitive
includes. Cycles and repeated imports in a scope are guarded. Function-local
variables and commands stay local. Open editor buffers take precedence over saved files.
Include paths can use known variable values and `${CMAKE_CURRENT_LIST_DIR}`;
unresolved dynamic paths do not produce definite missing-file warnings.
`annotations/core.cmake` is loaded automatically before each file unit, including
when analysis stops at the cursor. Its declarations are available without an
explicit include.

The repository provides two annotation files, with descriptions adapted from
the official CMake 4.4 manual and links to each entry's documentation:

The migrated platform, compiler, environment and cache descriptions were checked
against the installed CMake 4.4.4 reference manual. Environment compiler flags
use the documented `CFLAGS` and `CXXFLAGS` names, rather than a generic `FLAGS`.
`PATH` and `LD_LIBRARY_PATH` retain general process-environment descriptions;
the CMake manual has no dedicated entries for them.

- `annotations/core.cmake` contains general-purpose language utilities for DSL
  usage: control flow, normal variables, strings, lists, files, paths, processes,
  metaprogramming, and list-file, function and regular-expression context.
- `annotations/cmake.cmake` adds interfaces for normal
  CMake execution: cache entries, policies, configuration, properties, discovery,
  generator-expression stripping, diagnostics, host queries and runtime settings.
  It is not yet a complete catalogue of project/build-system commands.

Import the additional CMake interfaces with
`## include(relative/path/to/annotations/cmake.cmake)`, relative to your file.
Core is preloaded independently by the analyzer. Loaded find modules or package
configurations may require a project. Runtime version requirements still apply;
the annotations do not implement commands.

The former `##cmake-ls:` directives are no longer supported.

For automatic CMake/external pack loading, CLI and editor settings, precedence,
and standalone packaging, see [annotation loading](annotation-loading.md).
