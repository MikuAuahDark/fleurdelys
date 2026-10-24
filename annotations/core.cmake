# General-purpose CMake language annotations for DSL usage.
# Automatically loaded by fleurdelys for every file unit.
# Includes control flow, normal variables, text/list processing, files, paths,
# processes and metaprogramming. CMake-specific runtime interfaces are in cmake.cmake.
# Descriptions and signatures adapted from the official CMake 4.4 documentation:
# https://cmake.org/cmake/help/v4.4/manual/cmake-commands.7.html
# https://cmake.org/cmake/help/v4.4/manual/cmake-variables.7.html
# Entries link to their sources. Runtime version requirements still apply.
# Variadic option tails accommodate syntax the annotation grammar cannot express.
# Variable declarations document names without assigning runtime values.

# Control flow and scopes

## Execute commands conditionally. Conditions support predicates, comparisons and boolean operators.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/if.html)
## function(if [?condition]...)

## Test another condition in an if block.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/elseif.html)
## function(elseif [?condition]...)

## Execute the fallback branch of an if block. The optional condition repeats the opening condition.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/else.html)
## function(else [?condition]...)

## Close an if block.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/endif.html)
## function(endif [?condition]...)

## Repeat commands while the condition is true.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/while.html)
## function(while [?condition]...)

## Close a while loop.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/endwhile.html)
## function(endwhile [?condition]...)

## Iterate over the supplied items.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/foreach.html)
## function(foreach <?loop_var> [?item]...)

## Iterate from zero through stop, inclusive.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/foreach.html)
## function(foreach <?loop_var> RANGE <?stop>)

## Iterate through an inclusive numeric range with an optional step.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/foreach.html)
## function(foreach <?loop_var> RANGE <?start> <?stop> [?step])

## Iterate over named lists and explicit items.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/foreach.html)
## function(foreach <?loop_var> IN [LISTS [?list]...] [ITEMS [?item]...])

## Iterate over lists in parallel. One loop variable produces suffixed variables; multiple variables receive corresponding elements.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/foreach.html)
## function(foreach <?loop_var>... IN ZIP_LISTS <?list>...)

## Close a foreach loop.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/endforeach.html)
## function(endforeach [?loop_var])

## Leave the innermost loop.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/break.html)
## function(break)

## Skip to the next iteration of the innermost loop.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/continue.html)
## function(continue)

## Define a callable command with its own variable scope.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/function.html)
## function(function <?name> [?parameter]...)

## End a function definition.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/endfunction.html)
## function(endfunction [?name])

## Define a macro whose commands execute in the caller's scope.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/macro.html)
## function(macro <?name> [?parameter]...)

## End a macro definition.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/endmacro.html)
## function(endmacro [?name])

## Create a variable-scoped block, optionally forwarding variables when it ends. Requires CMake 3.25.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/block.html)
## function(block [SCOPE_FOR VARIABLES] [PROPAGATE <?variable>...])

## Close a scoped block.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/endblock.html)
## function(endblock)

## Return from a file, directory or function. PROPAGATE forwards variables through enclosing blocks and requires CMake 3.25.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/return.html)
## function(return [PROPAGATE <?variable>...])

# Variables and inclusion

## Bind a normal variable; multiple values form a semicolon-separated list. PARENT_SCOPE changes the enclosing scope.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/set.html)
## function(set <&variable> [?value]... [PARENT_SCOPE])

## Remove a normal variable or a binding in the enclosing scope. ENV{variable} bindings are also accepted.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/unset.html)
## function(unset <?variable> [PARENT_SCOPE])

## Load a file or module. OPTIONAL tolerates a missing file; RESULT_VARIABLE receives the resolved filename or NOTFOUND.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/include.html)
## function(include <?file_or_module> [OPTIONAL] [RESULT_VARIABLE <&result>])

## Prevent repeated inclusion in the current, directory, or global scope.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/include_guard.html)
## function(include_guard [DIRECTORY|GLOBAL])

## Parse keyword arguments into variables prefixed by the chosen prefix. Options, one-value keywords and multi-value keywords are lists.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_parse_arguments.html)
## function(cmake_parse_arguments <?prefix> <?options> <?one_value_keywords> <?multi_value_keywords> [?argument]...)

## Parse function arguments directly from ARGV starting at the specified index, preserving embedded semicolons.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_parse_arguments.html)
## function(cmake_parse_arguments PARSE_ARGV <?start> <?prefix> <?options> <?one_value_keywords> <?multi_value_keywords>)

## Watch reads and modifications of a normal variable, optionally invoking a callback.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/variable_watch.html)
## function(variable_watch <?variable> [?command])

# Messages, execution and introspection

## Emit a message. The default level is NOTICE; severity and log-level keywords control reporting.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/message.html)
## function(message [?text]...)

## Emit a diagnostic or log message at the specified level.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/message.html)
## function(message <FATAL_ERROR|SEND_ERROR|WARNING|NOTICE|STATUS|VERBOSE|DEBUG|TRACE> [?text]...)

## Evaluate an integer expression with signed 64-bit arithmetic, optionally formatting the result as hexadecimal.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/math.html)
## function(math EXPR <&output> <?expression> [OUTPUT_FORMAT <DECIMAL|HEXADECIMAL>])

## Run one or more child processes during script evaluation. Options select working directory, timeout, streams and result variables.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/execute_process.html)
## function(execute_process COMMAND <?argument>... [?option]...)

## Run a process pipeline with explicit stream and result variables. Keyword ordering follows the documented synopsis; the general overload accepts other orderings.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/execute_process.html)
## function(execute_process COMMAND <?command> [?argument]... [COMMAND <?command> [?argument]...]... [WORKING_DIRECTORY <?directory>] [TIMEOUT <?seconds>] [RESULT_VARIABLE <&result>] [RESULTS_VARIABLE <&results>] [OUTPUT_VARIABLE <&output>] [ERROR_VARIABLE <&error>] [INPUT_FILE <?file>] [OUTPUT_FILE <?file>] [ERROR_FILE <?file>] [OUTPUT_QUIET] [ERROR_QUIET] [COMMAND_ECHO <STDOUT|STDERR|NONE>] [OUTPUT_STRIP_TRAILING_WHITESPACE] [ERROR_STRIP_TRAILING_WHITESPACE] [ENCODING <?encoding>] [ECHO_OUTPUT_VARIABLE] [ECHO_ERROR_VARIABLE] [COMMAND_ERROR_IS_FATAL <ANY|LAST|NONE>])

## Invoke a command by name.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_language.html)
## function(cmake_language CALL <?command> [?argument]...)

## Evaluate strings as CMake code.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_language.html)
## function(cmake_language EVAL CODE <?code>...)

## Exit script mode with the specified status. Requires CMake 3.29.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_language.html)
## function(cmake_language EXIT <?exit_code>)

# Strings

## Find a substring's byte offset; REVERSE selects its last occurrence. Missing substrings yield -1.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#search-and-replace)
## function(string FIND <?string> <?substring> <&output> [REVERSE])

## Replace literal matches in the concatenated inputs.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#search-and-replace)
## function(string REPLACE <?match> <?replacement> <&output> [?input]...)

## Extract the first or all regular-expression matches.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#search-and-replace)
## function(string REGEX <MATCH|MATCHALL> <?regex> <&output> [?input]...)

## Replace regular-expression matches using a replacement expression.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#search-and-replace)
## function(string REGEX REPLACE <?regex> <?replacement> <&output> [?input]...)

## Escape regular-expression metacharacters. Requires CMake 4.2.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#manipulation)
## function(string REGEX QUOTE <&output> <?input>...)

## Append or prepend inputs to a variable.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#manipulation)
## function(string <APPEND|PREPEND> <&variable> [?input]...)

## Concatenate inputs.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#manipulation)
## function(string CONCAT <&output> [?input]...)

## Join inputs with a separator.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#manipulation)
## function(string JOIN <?glue> <&output> [?input]...)

## Change case, measure byte length or trim whitespace.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#manipulation)
## function(string <TOLOWER|TOUPPER|LENGTH|STRIP> <?string> <&output>)

## Extract bytes beginning at an offset; length -1 selects the remainder.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#manipulation)
## function(string SUBSTRING <?string> <?begin> <?length> <&output>)

## Repeat a string a specified number of times.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#manipulation)
## function(string REPEAT <?string> <?count> <&output>)

## Compare two strings lexicographically.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#comparison)
## function(string COMPARE <LESS|GREATER|EQUAL|NOTEQUAL|LESS_EQUAL|GREATER_EQUAL> <?left> <?right> <&output>)

## Compute a hexadecimal digest.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#hashing)
## function(string <MD5|SHA1|SHA224|SHA256|SHA384|SHA512|SHA3_224|SHA3_256|SHA3_384|SHA3_512> <&output> <?input>)

## Convert numeric character codes to a string.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#generation)
## function(string ASCII <?number>... <&output>)

## Encode bytes as hexadecimal.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#generation)
## function(string HEX <?string> <&output>)

## Convert text to a valid C identifier.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#generation)
## function(string MAKE_C_IDENTIFIER <?string> <&output>)

## Generate pseudorandom text with optional length, alphabet and seed.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#generation)
## function(string RANDOM [LENGTH <?length>] [ALPHABET <?alphabet>] [RANDOM_SEED <?seed>] <&output>)

## Format the current time, optionally in UTC.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#generation)
## function(string TIMESTAMP <&output> [?format] [UTC])

## Generate a namespace-based UUID.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#generation)
## function(string UUID <&output> NAMESPACE <?namespace> NAME <?name> TYPE <MD5|SHA1> [UPPER])

## Read, inspect or remove JSON elements.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#json)
## function(string JSON <&output> [ERROR_VARIABLE <&error>] <GET|TYPE|LENGTH|REMOVE> <?json> [?member_or_index]...)

## Retrieve a JSON object's member name by index.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#json)
## function(string JSON <&output> [ERROR_VARIABLE <&error>] MEMBER <?json> [?member_or_index]... <?index>)

## Assign a JSON element.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#json)
## function(string JSON <&output> [ERROR_VARIABLE <&error>] SET <?json> <?member_or_index>... <?value>)

## Compare JSON values structurally.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#json)
## function(string JSON <&output> [ERROR_VARIABLE <&error>] EQUAL <?left_json> <?right_json>)

# Lists

## Count list elements.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#reading)
## function(list LENGTH <?list> <&output>)

## Retrieve elements by index; negative indices count from the end.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#reading)
## function(list GET <?list> <?index>... <&output>)

## Join list elements with a separator.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#reading)
## function(list JOIN <?list> <?glue> <&output>)

## Extract a list segment; length -1 selects the remainder.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#reading)
## function(list SUBLIST <?list> <?begin> <?length> <&output>)

## Find an element's first index, or -1 when absent.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#search)
## function(list FIND <?list> <?value> <&output>)

## Add elements to either end of a list.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#modification)
## function(list <APPEND|PREPEND> <&list> [?element]...)

## Keep or discard elements matching a regular expression.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#modification)
## function(list FILTER <&list> <INCLUDE|EXCLUDE> REGEX <?regex>)

## Insert elements at an index.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#modification)
## function(list INSERT <&list> <?index> [?element]...)

## Remove elements from either end, optionally storing each removed element.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#modification)
## function(list <POP_BACK|POP_FRONT> <&list> [&output]...)

## Remove matching values or indexed elements.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#modification)
## function(list <REMOVE_ITEM|REMOVE_AT> <&list> <?value_or_index>...)

## Remove duplicate elements or reverse their order.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#modification)
## function(list <REMOVE_DUPLICATES|REVERSE> <&list>)

## Transform elements in place, optionally selecting indices or writing another variable. Options include AT, FOR, REGEX and OUTPUT_VARIABLE.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#modification)
## function(list TRANSFORM <?list> <APPEND|PREPEND> <?value> [?option]...)

## Apply a case or whitespace transformation to list elements.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#modification)
## function(list TRANSFORM <?list> <TOLOWER|TOUPPER|STRIP> [?option]...)

## Replace regular-expression matches in selected elements.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#modification)
## function(list TRANSFORM <?list> REPLACE <?regex> <?replacement> [?option]...)

## Transform selected elements into a separate output list.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#modification)
## function(list TRANSFORM <?list> <APPEND|PREPEND> <?value> [?selector]... OUTPUT_VARIABLE <&output>)

## Apply a case or whitespace transformation to list elements.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#modification)
## function(list TRANSFORM <?list> <TOLOWER|TOUPPER|STRIP> [?selector]... OUTPUT_VARIABLE <&output>)

## Write regular-expression replacements to another list.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#modification)
## function(list TRANSFORM <?list> REPLACE <?regex> <?replacement> [?selector]... OUTPUT_VARIABLE <&output>)

## Sort elements using the selected comparison, case and order.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#ordering)
## function(list SORT <&list> [COMPARE <STRING|FILE_BASENAME|NATURAL>] [CASE <SENSITIVE|INSENSITIVE>] [ORDER <ASCENDING|DESCENDING>])

# Files and filesystem paths

## Read file contents, optionally limiting the byte range or encoding the bytes as hexadecimal.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#reading)
## function(file READ <?filename> <&output> [OFFSET <?offset>] [LIMIT <?limit>] [HEX])

## Extract text strings from a file. Options control length, count, encoding and filtering.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#reading)
## function(file STRINGS <?filename> <&output> [?option]...)

## Compute a file's hexadecimal digest.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#reading)
## function(file <MD5|SHA1|SHA224|SHA256|SHA384|SHA512|SHA3_224|SHA3_256|SHA3_384|SHA3_512> <?filename> <&output>)

## Format a file's modification time.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#reading)
## function(file TIMESTAMP <?filename> <&output> [?format] [UTC])

## Write or append content, creating missing parent directories.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#writing)
## function(file <WRITE|APPEND> <?filename> [?content]...)

## Update timestamps; TOUCH creates missing files while TOUCH_NOCREATE skips them.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#writing)
## function(file <TOUCH|TOUCH_NOCREATE> [?file]...)

## Collect matching paths. GLOB_RECURSE descends into subdirectories; options control directory entries, relative paths and symlinks.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#filesystem)
## function(file <GLOB|GLOB_RECURSE> <&output> [?option_or_pattern]...)

## Create directories and their missing parents.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#filesystem)
## function(file MAKE_DIRECTORY [?directory]... [RESULT <&result>])

## Remove files or recursively remove directories.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#filesystem)
## function(file <REMOVE|REMOVE_RECURSE> [?path]...)

## Move a filesystem entry, optionally reporting errors or preventing replacement.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#filesystem)
## function(file RENAME <?oldname> <?newname> [RESULT <&result>] [NO_REPLACE])

## Copy one file, with options for unchanged content and recent-file access retries.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#filesystem)
## function(file COPY_FILE <?source> <?destination> [RESULT <&result>] [ONLY_IF_DIFFERENT] [INPUT_MAY_BE_RECENT])

## Copy filesystem entries while controlling permissions, matching and symlink traversal.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#filesystem)
## function(file COPY <?file>... DESTINATION <?directory> [?option]...)

## Read a file's size in bytes or a symbolic link's stored target.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#filesystem)
## function(file <SIZE|READ_SYMLINK> <?filename> <&output>)

## Create a hard or symbolic link, optionally falling back to copying.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#filesystem)
## function(file CREATE_LINK <?original> <?linkname> [RESULT <&result>] [COPY_ON_ERROR] [SYMBOLIC])

## Change file and directory permissions, optionally recursively.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#filesystem)
## function(file <CHMOD|CHMOD_RECURSE> <?path>... [?option]...)

## Resolve symlinks and make a path absolute.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#path-conversion)
## function(file REAL_PATH <?path> <&output> [BASE_DIRECTORY <?directory>] [EXPAND_TILDE])

## Compute a relative filesystem path.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#path-conversion)
## function(file RELATIVE_PATH <&output> <?directory> <?file>)

## Convert between CMake and native path notation. Prefer cmake_path for new code.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#path-conversion)
## function(file <TO_CMAKE_PATH|TO_NATIVE_PATH> <?path> <&output>)

## Download a URL, optionally into a file. Options control TLS, authentication, timeouts, hashes and status reporting.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#transfer)
## function(file DOWNLOAD <?url> [?file] [?option]...)

## Upload a file to a URL with optional transfer settings.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#transfer)
## function(file UPLOAD <?file> <?url> [?option]...)

## Lock a file or directory, optionally choosing the lifetime, timeout or explicit release.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#locking)
## function(file LOCK <?path> [?option]...)

## Create an archive from paths, with optional format, compression and timestamp settings.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#archiving)
## function(file ARCHIVE_CREATE OUTPUT <?archive> PATHS <?path>... [?option]...)

## Extract or list an archive's contents, optionally filtering paths and choosing a destination.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#archiving)
## function(file ARCHIVE_EXTRACT INPUT <?archive> [?option]...)

## Extract a path component without accessing the filesystem.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_path.html#decomposition)
## function(cmake_path GET <?path_var> <ROOT_NAME|ROOT_DIRECTORY|ROOT_PATH|FILENAME|RELATIVE_PART|PARENT_PATH> <&output>)

## Extract an extension or stem, optionally considering only the last extension.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_path.html#decomposition)
## function(cmake_path GET <?path_var> <EXTENSION|STEM> [LAST_ONLY] <&output>)

## Test path components or whether a path is absolute or relative.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_path.html#query)
## function(cmake_path <HAS_ROOT_NAME|HAS_ROOT_DIRECTORY|HAS_ROOT_PATH|HAS_FILENAME|HAS_EXTENSION|HAS_STEM|HAS_RELATIVE_PART|HAS_PARENT_PATH|IS_ABSOLUTE|IS_RELATIVE> <?path_var> <&output>)

## Test whether a path is a prefix of another path, optionally after normalization.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_path.html#query)
## function(cmake_path IS_PREFIX <?path_var> <?input> [NORMALIZE] <&output>)

## Compare literal paths for equality or inequality.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_path.html#comparison)
## function(cmake_path COMPARE <?left> <EQUAL|NOT_EQUAL> <?right> <&output>)

## Assign a native path converted to CMake notation, optionally normalizing it.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_path.html#modification)
## function(cmake_path SET <&path_var> [NORMALIZE] <?input>)

## Append path components or raw text, optionally writing a separate output variable.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_path.html#modification)
## function(cmake_path <APPEND|APPEND_STRING> <?path_var> [?input]... [OUTPUT_VARIABLE <&output>])

## Remove a filename or normalize a path, optionally writing a separate result.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_path.html#modification)
## function(cmake_path <REMOVE_FILENAME|NORMAL_PATH> <?path_var> [OUTPUT_VARIABLE <&output>])

## Replace a filename.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_path.html#modification)
## function(cmake_path REPLACE_FILENAME <?path_var> <?input> [OUTPUT_VARIABLE <&output>])

## Remove an extension.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_path.html#modification)
## function(cmake_path REMOVE_EXTENSION <?path_var> [LAST_ONLY] [OUTPUT_VARIABLE <&output>])

## Replace an extension.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_path.html#modification)
## function(cmake_path REPLACE_EXTENSION <?path_var> [LAST_ONLY] <?input> [OUTPUT_VARIABLE <&output>])

## Form a relative path against a base directory.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_path.html#generation)
## function(cmake_path RELATIVE_PATH <?path_var> [BASE_DIRECTORY <?base>] [OUTPUT_VARIABLE <&output>])

## Form an absolute path, optionally normalizing it.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_path.html#generation)
## function(cmake_path ABSOLUTE_PATH <?path_var> [BASE_DIRECTORY <?base>] [NORMALIZE] [OUTPUT_VARIABLE <&output>])

## Convert a path variable to native notation.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_path.html#native-conversion)
## function(cmake_path NATIVE_PATH <?path_var> [NORMALIZE] <&output>)

## Convert a literal path list between native and CMake separators.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_path.html#native-conversion)
## function(cmake_path CONVERT <?input> <TO_CMAKE_PATH_LIST|TO_NATIVE_PATH_LIST> <&output> [NORMALIZE])

## Hash a normalized path.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_path.html#hashing)
## function(cmake_path HASH <?path_var> <&output>)

## Extract a path component. Prefer cmake_path for modern lexical operations or file(REAL_PATH) for symlink resolution.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_filename_component.html)
## function(get_filename_component <&output> <?filename> <DIRECTORY|NAME|EXT|NAME_WE|LAST_EXT|NAME_WLE|PATH>)

## Resolve an absolute path, optionally resolving symlinks.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_filename_component.html)
## function(get_filename_component <&output> <?filename> <ABSOLUTE|REALPATH> [BASE_DIR <?directory>])

## Split a program and its arguments.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_filename_component.html)
## function(get_filename_component <&output> <?command_line> PROGRAM [PROGRAM_ARGS <&arguments>])

## Parse a command line using the selected platform's quoting rules. PROGRAM optionally resolves its executable; SEPARATE_ARGS splits the remaining arguments.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/separate_arguments.html)
## function(separate_arguments <&output> <UNIX_COMMAND|WINDOWS_COMMAND|NATIVE_COMMAND> [PROGRAM [SEPARATE_ARGS]] <?command_line>)

## Replace spaces in the named variable with list separators (legacy form).
## [Documentation](https://cmake.org/cmake/help/v4.4/command/separate_arguments.html)
## function(separate_arguments <&variable>)

# List, function and regular-expression context

## Absolute path of the list file currently being processed.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_CURRENT_LIST_FILE.html)
## set(CMAKE_CURRENT_LIST_FILE)

## Directory of the list file currently being processed; its value follows the dynamic call context.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_CURRENT_LIST_DIR.html)
## set(CMAKE_CURRENT_LIST_DIR)

## Line number currently being processed in the current list file.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_CURRENT_LIST_LINE.html)
## set(CMAKE_CURRENT_LIST_LINE)

## File that included the current file. Unset in the outermost script and, with CMP0198 NEW, while processing CMakeLists.txt.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_PARENT_LIST_FILE.html)
## set(CMAKE_PARENT_LIST_FILE)

## Name of the function currently executing; unset outside a function.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_CURRENT_FUNCTION.html)
## set(CMAKE_CURRENT_FUNCTION)

## File in which the executing function was defined.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_CURRENT_FUNCTION_LIST_FILE.html)
## set(CMAKE_CURRENT_FUNCTION_LIST_FILE)

## Directory in which the executing function was defined; useful for locating resources alongside the definition.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_CURRENT_FUNCTION_LIST_DIR.html)
## set(CMAKE_CURRENT_FUNCTION_LIST_DIR)

## Line where the executing function was defined.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_CURRENT_FUNCTION_LIST_LINE.html)
## set(CMAKE_CURRENT_FUNCTION_LIST_LINE)

## Number of arguments passed to a function or macro. Macro arguments are substitutions rather than ordinary variables.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/function.html#arguments)
## set(ARGC)

## All arguments passed to a function or macro as a list.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/function.html#arguments)
## set(ARGV)

## Arguments beyond the named parameters of a function or macro.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/function.html#arguments)
## set(ARGN)

## Number of capture groups from the latest successful regular-expression match.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MATCH_COUNT.html)
## set(CMAKE_MATCH_COUNT)

## Complete text matched by the latest successful regular expression.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MATCH_n.html)
## set(CMAKE_MATCH_0)

## Text captured by regular-expression group 1.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MATCH_n.html)
## set(CMAKE_MATCH_1)

## Text captured by regular-expression group 2.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MATCH_n.html)
## set(CMAKE_MATCH_2)

## Text captured by regular-expression group 3.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MATCH_n.html)
## set(CMAKE_MATCH_3)

## Text captured by regular-expression group 4.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MATCH_n.html)
## set(CMAKE_MATCH_4)

## Text captured by regular-expression group 5.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MATCH_n.html)
## set(CMAKE_MATCH_5)

## Text captured by regular-expression group 6.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MATCH_n.html)
## set(CMAKE_MATCH_6)

## Text captured by regular-expression group 7.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MATCH_n.html)
## set(CMAKE_MATCH_7)

## Text captured by regular-expression group 8.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MATCH_n.html)
## set(CMAKE_MATCH_8)

## Text captured by regular-expression group 9.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MATCH_n.html)
## set(CMAKE_MATCH_9)
