# Additional annotations for normal CMake execution.
# Import with ## include(path/to/cmake.cmake); core.cmake is imported below.
# Covers cache, compatibility policies, configuration, properties, discovery,
# diagnostics, host queries and CMake runtime settings moved out of the DSL core.
# This is not yet a complete catalogue of CMake project/build-system commands.
# Descriptions and signatures adapted from the official CMake 4.4 documentation:
# https://cmake.org/cmake/help/v4.4/manual/cmake-commands.7.html
# https://cmake.org/cmake/help/v4.4/manual/cmake-variables.7.html
# Entries link to their sources. Runtime version requirements still apply.
# Variadic option tails accommodate syntax the annotation grammar cannot express.
# Variable declarations document names without assigning runtime values.

# Control flow and scopes

## Create a scoped block. SCOPE_FOR selects policy and/or variable scopes; PROPAGATE forwards variables when the block ends. Requires CMake 3.25.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/block.html)
## function(block [SCOPE_FOR <POLICIES|VARIABLES>...] [PROPAGATE <?variable>...])

# Variables, configuration and inclusion

## Create or update a cache entry. FORCE permits replacing an existing value.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/set.html)
## function(set <?variable> [?value]... CACHE <BOOL|FILEPATH|PATH|STRING|INTERNAL> <?docstring> [FORCE])

## Set a cache entry using the CMake 4.2 cache-binding syntax. The first argument is CACHE{variable}.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/set.html)
## function(set <?cache_binding> [TYPE <BOOL|FILEPATH|PATH|STRING|INTERNAL>] [HELP [?help]...] [FORCE] VALUE [?value]...)

## Remove a cache entry.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/unset.html)
## function(unset <?variable> CACHE)

## Define a boolean cache option. Its default is OFF when no initial value is supplied.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/option.html)
## function(option <&variable> <?help_text> [?initial_value])

## Specify the minimum supported CMake version and establish the corresponding policy version.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_minimum_required.html)
## function(cmake_minimum_required VERSION <?version_or_range> [FATAL_ERROR])

## Select compatibility behavior for a policy.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_policy.html)
## function(cmake_policy SET <?policy> <OLD|NEW>)

## Read the current setting of a policy.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_policy.html)
## function(cmake_policy GET <?policy> <&output>)

## Select policy settings corresponding to a CMake version or version range.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_policy.html)
## function(cmake_policy VERSION <?version_or_range>)

## Save or restore the policy stack. Every PUSH needs a matching POP.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_policy.html)
## function(cmake_policy <PUSH|POP>)

## Load a file or module. OPTIONAL tolerates a missing file; RESULT_VARIABLE receives the resolved filename or NOTFOUND.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/include.html)
## function(include <?file_or_module> [OPTIONAL] [RESULT_VARIABLE <&result>] [NO_POLICY_SCOPE])

## Copy a file, optionally substituting variables and #cmakedefine directives. Options control escaping, permissions and newline style.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/configure_file.html)
## function(configure_file <?input> <?output> [?option]...)

## Mark cache entries as advanced, optionally clearing or forcing the flag.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/mark_as_advanced.html)
## function(mark_as_advanced [CLEAR|FORCE] [?variable]...)

## Read selected entries from another cache into prefixed normal variables.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/load_cache.html)
## function(load_cache <?directory> READ_WITH_PREFIX <?prefix> [?entry]...)

# Messages, execution and introspection

## Emit a CMake author or deprecation diagnostic.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/message.html)
## function(message <AUTHOR_WARNING|DEPRECATION> [?text]...)

## Start or finish a check. CHECK_PASS and CHECK_FAIL pair with the most recent CHECK_START.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/message.html)
## function(message <CHECK_START|CHECK_PASS|CHECK_FAIL> [?text]...)

## Read the current message log level.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_language.html)
## function(cmake_language GET_MESSAGE_LOG_LEVEL <&output>)

## Enable or disable tracing. Requires CMake 4.2.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_language.html)
## function(cmake_language TRACE ON [EXPAND])

## Disable the innermost tracing scope. Requires CMake 4.2.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_language.html)
## function(cmake_language TRACE OFF)

## Query host information. QUERY accepts keys such as NUMBER_OF_LOGICAL_CORES, HOSTNAME and OS_NAME.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_host_system_information.html)
## function(cmake_host_system_information RESULT <&output> QUERY <?key>...)

## Query the Windows registry, with options for views, values and error reporting.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_host_system_information.html)
## function(cmake_host_system_information RESULT <&output> QUERY WINDOWS_REGISTRY <?key> [?option]...)

## Set diagnostic-category behavior. Requires CMake 4.4.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_diagnostic.html)
## function(cmake_diagnostic SET <?category> <IGNORE|WARN|SEND_ERROR|FATAL_ERROR> [RECURSE])

## Raise or lower diagnostic severity. Requires CMake 4.4.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_diagnostic.html)
## function(cmake_diagnostic <PROMOTE|DEMOTE> <?category> <IGNORE|WARN|SEND_ERROR|FATAL_ERROR> [NO_RECURSE])

## Read a diagnostic action. Requires CMake 4.4.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_diagnostic.html)
## function(cmake_diagnostic GET <?diagnostic> <&output>)

## Save or restore diagnostic settings. Requires CMake 4.4.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_diagnostic.html)
## function(cmake_diagnostic <PUSH|POP>)

## Retrieve a global CMake property or VARIABLES, MACROS, COMPONENTS or COMMANDS.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_cmake_property.html)
## function(get_cmake_property <&output> <?property>)

## Read a directory property or a directory-scoped variable.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_directory_property.html)
## function(get_directory_property <&output> [DIRECTORY <?directory>] <?property>)

## Read a variable in the chosen directory scope.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_directory_property.html)
## function(get_directory_property <&output> [DIRECTORY <?directory>] DEFINITION <?variable>)

## Query a global property, its presence, or its documentation.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_property.html)
## function(get_property <&output> GLOBAL PROPERTY <?property> [SET|DEFINED|BRIEF_DOCS|FULL_DOCS])

## Query a directory property.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_property.html)
## function(get_property <&output> DIRECTORY [?directory] PROPERTY <?property> [SET|DEFINED|BRIEF_DOCS|FULL_DOCS])

## Query a cache-entry property.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_property.html)
## function(get_property <&output> CACHE <?entry> PROPERTY <?property> [SET|DEFINED|BRIEF_DOCS|FULL_DOCS])

## Query a variable property.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_property.html)
## function(get_property <&output> VARIABLE PROPERTY <?property> [SET|DEFINED|BRIEF_DOCS|FULL_DOCS])

## Set or append a global property.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/set_property.html)
## function(set_property GLOBAL [APPEND|APPEND_STRING] PROPERTY <?property> [?value]...)

## Set or append a directory property.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/set_property.html)
## function(set_property DIRECTORY [?directory] [APPEND|APPEND_STRING] PROPERTY <?property> [?value]...)

## Set or append properties on cache entries.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/set_property.html)
## function(set_property CACHE <?entry>... [APPEND|APPEND_STRING] PROPERTY <?property> [?value]...)

## Set directory properties using name/value pairs.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/set_directory_properties.html)
## function(set_directory_properties PROPERTIES <?property> <?value> [?property ?value]...)

## Store the host computer's name in a variable.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/site_name.html)
## function(site_name <&output>)

# Strings

## Remove generator expressions from a string.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#manipulation)
## function(string GENEX_STRIP <?string> <&output>)

## Substitute variables in a string.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/string.html#generation)
## function(string CONFIGURE <?string> <&output> [@ONLY] [ESCAPE_QUOTES])

# Lists

## Remove generator expressions from list elements.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#modification)
## function(list TRANSFORM <?list> GENEX_STRIP [?option]...)

## Remove generator expressions from list elements.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/list.html#modification)
## function(list TRANSFORM <?list> GENEX_STRIP [?selector]... OUTPUT_VARIABLE <&output>)

# Files and filesystem paths

## Write configured content with optional variable escaping and newline conversion.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/file.html#writing)
## function(file CONFIGURE OUTPUT <?filename> CONTENT <?content> [?option]...)

## Extract a path component. Prefer cmake_path for modern lexical operations or file(REAL_PATH) for symlink resolution.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_filename_component.html)
## function(get_filename_component <&output> <?filename> <DIRECTORY|NAME|EXT|NAME_WE|LAST_EXT|NAME_WLE|PATH> [CACHE])

## Resolve an absolute path, optionally resolving symlinks.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_filename_component.html)
## function(get_filename_component <&output> <?filename> <ABSOLUTE|REALPATH> [BASE_DIR <?directory>] [CACHE])

## Split a program and its arguments.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_filename_component.html)
## function(get_filename_component <&output> <?command_line> PROGRAM [PROGRAM_ARGS <&arguments>] [CACHE])

# Discovery (modules and package configurations may themselves require a project)

## Locate a file and store its full path or a NOTFOUND result. Options include NAMES, HINTS, PATHS, PATH_SUFFIXES, NO_CACHE and REQUIRED.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/find_file.html)
## function(find_file <&variable> <?name_or_option>...)

## Locate a directory containing a requested file.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/find_path.html)
## function(find_path <&variable> <?name_or_option>...)

## Locate an executable program.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/find_program.html)
## function(find_program <&variable> <?name_or_option>...)

## Locate a library file without creating a build target.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/find_library.html)
## function(find_library <&variable> <?name_or_option>...)

## Locate a package through a find module or package configuration. Version, components and search behavior are optional; loaded files may require project mode.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/find_package.html)
## function(find_package <?package> [?version_or_option]...)

## Read a pkg-config file into CMAKE_PKG_CONFIG_* variables without importing targets. Requires CMake 3.31; options control lookup, strictness and variable overrides.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_pkg_config.html#extract)
## function(cmake_pkg_config EXTRACT <?package> [?version_or_option]...)

# CMake invocation, version and directory context

## Number of command-line arguments passed to CMake in script mode.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_ARGC.html)
## set(CMAKE_ARGC)

## First command-line argument in script mode. Subsequent arguments are CMAKE_ARGV1, CMAKE_ARGV2, and so on.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_ARGV0.html)
## set(CMAKE_ARGV0)

## Absolute path of the file passed to cmake -P; unset outside script mode.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_SCRIPT_MODE_FILE.html)
## set(CMAKE_SCRIPT_MODE_FILE)

## Full path of the CMake executable.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_COMMAND.html)
## set(CMAKE_COMMAND)

## Directory containing CMake's installed modules and other support files.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_ROOT.html)
## set(CMAKE_ROOT)

## Complete CMake version string.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_VERSION.html)
## set(CMAKE_VERSION)

## Major component of CMake's version.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MAJOR_VERSION.html)
## set(CMAKE_MAJOR_VERSION)

## Minor component of CMake's version.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MINOR_VERSION.html)
## set(CMAKE_MINOR_VERSION)

## Patch component of CMake's version.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_PATCH_VERSION.html)
## set(CMAKE_PATCH_VERSION)

## Compatibility variable fixed at 0; older CMake releases used it as a fourth version component.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_TWEAK_VERSION.html)
## set(CMAKE_TWEAK_VERSION)

## Version requested by the most recent cmake_minimum_required call.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MINIMUM_REQUIRED_VERSION.html)
## set(CMAKE_MINIMUM_REQUIRED_VERSION)

## Top-level source directory; in script mode this is the working directory.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_SOURCE_DIR.html)
## set(CMAKE_SOURCE_DIR)

## Top-level binary directory; in script mode this is the working directory.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_BINARY_DIR.html)
## set(CMAKE_BINARY_DIR)

## Current source directory; in script mode this is the working directory.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_CURRENT_SOURCE_DIR.html)
## set(CMAKE_CURRENT_SOURCE_DIR)

## Current binary directory; in script mode this is the working directory.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_CURRENT_BINARY_DIR.html)
## set(CMAKE_CURRENT_BINARY_DIR)

# Host platform (compiler and target-system variables require project setup)

## True when CMake runs on Windows, including 64-bit Windows.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_HOST_WIN32.html)
## set(CMAKE_HOST_WIN32)

## True when CMake runs on a Unix-like operating system, including Apple platforms and Cygwin.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_HOST_UNIX.html)
## set(CMAKE_HOST_UNIX)

## True when CMake runs on an Apple operating system.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_HOST_APPLE.html)
## set(CMAKE_HOST_APPLE)

## True when CMake runs on Solaris.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_HOST_SOLARIS.html)
## set(CMAKE_HOST_SOLARIS)

## True when CMake runs on Linux. Requires CMake 3.25.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_HOST_LINUX.html)
## set(CMAKE_HOST_LINUX)

## BSD host variant, such as FreeBSD or OpenBSD, when applicable. Requires CMake 3.25.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_HOST_BSD.html)
## set(CMAKE_HOST_BSD)

## True when CMake runs on AIX.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_HOST_AIX.html)
## set(CMAKE_HOST_AIX)

## Executable filename suffix on the host platform, such as .exe on Windows.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_HOST_EXECUTABLE_SUFFIX.html)
## set(CMAKE_HOST_EXECUTABLE_SUFFIX)

## Host operating-system name and version combined.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_HOST_SYSTEM.html)
## set(CMAKE_HOST_SYSTEM)

## Name of the operating system running CMake.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_HOST_SYSTEM_NAME.html)
## set(CMAKE_HOST_SYSTEM_NAME)

## Version of the operating system running CMake.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_HOST_SYSTEM_VERSION.html)
## set(CMAKE_HOST_SYSTEM_VERSION)

## Processor reported by the host operating system.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_HOST_SYSTEM_PROCESSOR.html)
## set(CMAKE_HOST_SYSTEM_PROCESSOR)

# CMake runtime behavior and search settings

## Additional directories searched for include modules and find modules before CMake's own module directory.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MODULE_PATH.html)
## set(CMAKE_MODULE_PATH)

## Minimum severity emitted by message for ordinary log messages.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MESSAGE_LOG_LEVEL.html)
## set(CMAKE_MESSAGE_LOG_LEVEL)

## List of indentation fragments prefixed to eligible message output.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MESSAGE_INDENT.html)
## set(CMAKE_MESSAGE_INDENT)

## List of message-context components joined with dots when context display is enabled.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MESSAGE_CONTEXT.html)
## set(CMAKE_MESSAGE_CONTEXT)

## Enable display of message context.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MESSAGE_CONTEXT_SHOW.html)
## set(CMAKE_MESSAGE_CONTEXT_SHOW)

## Control warnings for deprecated functionality. Deprecated in CMake 4.4 and ignored with CMP0218 NEW; use cmake_diagnostic instead.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_WARN_DEPRECATED.html)
## set(CMAKE_WARN_DEPRECATED)

## Treat deprecated functionality as an error. Deprecated in CMake 4.4 and ignored with CMP0218 NEW; use cmake_diagnostic instead.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_ERROR_DEPRECATED.html)
## set(CMAKE_ERROR_DEPRECATED)

## Default command echo behavior for execute_process.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_EXECUTE_PROCESS_COMMAND_ECHO.html)
## set(CMAKE_EXECUTE_PROCESS_COMMAND_ECHO)

## Default fatal-error handling for execute_process child failures. Requires CMake 4.0.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_EXECUTE_PROCESS_COMMAND_ERROR_IS_FATAL.html)
## set(CMAKE_EXECUTE_PROCESS_COMMAND_ERROR_IS_FATAL)

## Semicolon-separated installation prefixes searched by find commands.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_PREFIX_PATH.html)
## set(CMAKE_PREFIX_PATH)

## Additional directories searched by find_program.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_PROGRAM_PATH.html)
## set(CMAKE_PROGRAM_PATH)

## Additional directories searched by find_file and find_path.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_INCLUDE_PATH.html)
## set(CMAKE_INCLUDE_PATH)

## Additional directories searched by find_library.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_LIBRARY_PATH.html)
## set(CMAKE_LIBRARY_PATH)

## Framework locations searched by find commands on Apple platforms.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_FRAMEWORK_PATH.html)
## set(CMAKE_FRAMEWORK_PATH)

## Application-bundle locations searched by find commands on Apple platforms.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_APPBUNDLE_PATH.html)
## set(CMAKE_APPBUNDLE_PATH)

## Directories excluded from find-command search results.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_IGNORE_PATH.html)
## set(CMAKE_IGNORE_PATH)

## Installation prefixes excluded from find-command searches.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_IGNORE_PREFIX_PATH.html)
## set(CMAKE_IGNORE_PREFIX_PATH)

## Emit additional find-command search diagnostics.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_FIND_DEBUG_MODE.html)
## set(CMAKE_FIND_DEBUG_MODE)

## Enable search locations supplied by CMake search-path variables.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_FIND_USE_CMAKE_PATH.html)
## set(CMAKE_FIND_USE_CMAKE_PATH)

## Enable search locations supplied by CMake-specific environment variables.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_FIND_USE_CMAKE_ENVIRONMENT_PATH.html)
## set(CMAKE_FIND_USE_CMAKE_ENVIRONMENT_PATH)

## Enable search locations supplied by standard system environment variables.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_FIND_USE_SYSTEM_ENVIRONMENT_PATH.html)
## set(CMAKE_FIND_USE_SYSTEM_ENVIRONMENT_PATH)

## Enable package-root search locations supplied by PackageName_ROOT variables.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_FIND_USE_PACKAGE_ROOT_PATH.html)
## set(CMAKE_FIND_USE_PACKAGE_ROOT_PATH)

## Treat find calls, including find_package, as REQUIRED unless OPTIONAL is specified. Requires CMake 4.1.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_FIND_REQUIRED.html)
## set(CMAKE_FIND_REQUIRED)

## Name of the package currently being located by find_package.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_FIND_PACKAGE_NAME.html)
## set(CMAKE_FIND_PACKAGE_NAME)

## Prefer package configuration files over find modules in find_package's basic signature.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_FIND_PACKAGE_PREFER_CONFIG.html)
## set(CMAKE_FIND_PACKAGE_PREFER_CONFIG)

## Package-directory sorting method: NONE, NAME or NATURAL.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_FIND_PACKAGE_SORT_ORDER.html)
## set(CMAKE_FIND_PACKAGE_SORT_ORDER)

## Package-directory sorting direction: ASC or DEC.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_FIND_PACKAGE_SORT_DIRECTION.html)
## set(CMAKE_FIND_PACKAGE_SORT_DIRECTION)

## Verify peer certificates for file transfers when not overridden by a command option.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_TLS_VERIFY.html)
## set(CMAKE_TLS_VERIFY)

## Certificate-authority bundle used by file transfers unless overridden.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_TLS_CAINFO.html)
## set(CMAKE_TLS_CAINFO)

## Minimum TLS version used by file transfers unless overridden.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_TLS_VERSION.html)
## set(CMAKE_TLS_VERSION)

## Default .netrc usage level for file transfers: IGNORED, OPTIONAL or REQUIRED.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_NETRC.html)
## set(CMAKE_NETRC)

## Alternative .netrc file used for transfer credentials.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_NETRC_FILE.html)
## set(CMAKE_NETRC_FILE)
