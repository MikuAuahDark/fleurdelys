# Additional annotations for normal CMake execution.
# Import with ## include(path/to/cmake.cmake); core.cmake is imported below.
# Covers cache, compatibility policies, configuration, properties, discovery,
# diagnostics, host queries and CMake runtime settings moved out of the DSL core.
# Includes project setup, target usage requirements, build rules, installation and testing.
# Descriptions and signatures adapted from the official CMake 4.4 documentation:
# https://cmake.org/cmake/help/v4.4/manual/cmake-commands.7.html
# https://cmake.org/cmake/help/v4.4/manual/cmake-variables.7.html
# Entries link to their sources. Runtime version requirements still apply.
# Variadic option tails accommodate syntax the annotation grammar cannot express.
# Variable declarations document names without assigning runtime values.

# Build targets. The t symbol namespace is defined by these annotations.

## Define an executable target from source files.
## function(add_executable <t&target> [WIN32] [MACOSX_BUNDLE] [EXCLUDE_FROM_ALL] [?source]...)
## Define an imported executable target.
## function(add_executable <t&target> IMPORTED [GLOBAL])
## Define an alias for an existing executable target.
## function(add_executable <t&target> ALIAS <t:target>)

## Define a library target from source files.
## function(add_library <t&target> [<STATIC|SHARED|MODULE|OBJECT|INTERFACE>] [EXCLUDE_FROM_ALL] [?source]...)
## Define an imported library target.
## function(add_library <t&target> <STATIC|SHARED|MODULE|UNKNOWN|OBJECT|INTERFACE> IMPORTED [GLOBAL])
## Define an alias for an existing library target.
## function(add_library <t&target> ALIAS <t:target>)

## Add compile definitions to a target with the specified visibility.
## function(target_compile_definitions <t:target> [<INTERFACE|PUBLIC|PRIVATE> [?definition]...]...)

# Project setup and build rules

## Set the project name and optionally enable languages (C and CXX by default).
## [Documentation](https://cmake.org/cmake/help/v4.4/command/project.html)
## function(project <?name> [?language]...)

## Set project metadata and languages. COMPAT_VERSION and SPDX_LICENSE require CMake 4.3; COMPAT_VERSION also requires VERSION.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/project.html)
## function(project <?name> [VERSION <?version>] [COMPAT_VERSION <?version>] [SPDX_LICENSE <?license>] [DESCRIPTION <?description>] [HOMEPAGE_URL <?url>] [LANGUAGES [?language]...])

## Enable additional compiler languages after project(). OPTIONAL is reserved and does not currently work.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/enable_language.html)
## function(enable_language <?language>... [OPTIONAL])

## Process a subdirectory immediately, optionally selecting its build directory. SYSTEM requires CMake 3.25.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/add_subdirectory.html)
## function(add_subdirectory <?source_dir> [?binary_dir] [EXCLUDE_FROM_ALL] [SYSTEM])

## Add build-order dependencies between top-level targets. Zero dependencies are allowed since CMake 4.1.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/add_dependencies.html)
## function(add_dependencies <t:target> [t:dependency]...)

## Create a target that is always out of date. Supports COMMAND, DEPENDS, BYPRODUCTS, SOURCES, VERBATIM and working-directory/job options.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/add_custom_target.html)
## function(add_custom_target <t&target> [ALL] [?command_or_option]...)

## Generate files at build time. Supports additional COMMAND clauses, DEPENDS, BYPRODUCTS, DEPFILE, VERBATIM, CODEGEN and job options.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/add_custom_command.html)
## function(add_custom_command OUTPUT <?output>... COMMAND <?command> [?argument_or_option]...)

## Attach a build event to a target in the current directory. PRE_BUILD has distinct behavior only with Visual Studio generators.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/add_custom_command.html)
## function(add_custom_command TARGET <t:target> <PRE_BUILD|PRE_LINK|POST_BUILD> COMMAND <?command> [?argument_or_option]...)


# Target usage requirements

## Require compiler features or language standards, such as cxx_std_20, for a target and its consumers.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/target_compile_features.html)
## function(target_compile_features <t:target> [<INTERFACE|PUBLIC|PRIVATE> <?feature>...]...)

## Append or prepend target compiler options with the chosen visibility.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/target_compile_options.html)
## function(target_compile_options <t:target> [BEFORE] [<INTERFACE|PUBLIC|PRIVATE> [?option]...]...)

## Add target include paths. SYSTEM marks system headers; visibility controls propagation to consumers.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/target_include_directories.html)
## function(target_include_directories <t:target> [SYSTEM] [AFTER|BEFORE] [<INTERFACE|PUBLIC|PRIVATE> [?directory]...]...)

## Add target linker search paths. Prefer full library paths when possible. Requires CMake 3.13.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/target_link_directories.html)
## function(target_link_directories <t:target> [BEFORE] [<INTERFACE|PUBLIC|PRIVATE> [?directory]...]...)

## Add target linker options; static-library archiver options use STATIC_LIBRARY_OPTIONS instead. Requires CMake 3.13.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/target_link_options.html)
## function(target_link_options <t:target> [BEFORE] [<INTERFACE|PUBLIC|PRIVATE> [?option]...]...)

## Link libraries and propagate usage requirements according to visibility. Items may include targets, paths, flags, generator expressions and debug/optimized/general qualifiers.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/target_link_libraries.html)
## function(target_link_libraries <t:target> [<INTERFACE|PUBLIC|PRIVATE> [?library_or_flag]...]...)

## Link libraries with the plain signature. Do not mix plain and keyword signatures for the same target.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/target_link_libraries.html)
## function(target_link_libraries <t:target> [?library_or_flag]...)

## Specify headers to precompile and their visibility. Requires CMake 3.16.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/target_precompile_headers.html)
## function(target_precompile_headers <t:target> [<INTERFACE|PUBLIC|PRIVATE> [?header]...]...)

## Reuse another target's precompiled header artifact and add a dependency on that target. Compiler options and definitions must agree. Requires CMake 3.16.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/target_precompile_headers.html)
## function(target_precompile_headers <t:target> REUSE_FROM <t:other_target>)

## Add target sources with the chosen visibility. Relative paths use the current source directory.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/target_sources.html)
## function(target_sources <t:target> [<INTERFACE|PUBLIC|PRIVATE> [?source]...]...)

## Add named file sets. Requires CMake 3.23; CXX_MODULES requires 3.28 and SOURCES requires 4.4.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/target_sources.html)
## function(target_sources <t:target> [<INTERFACE|PUBLIC|PRIVATE> [FILE_SET <?set> [TYPE <HEADERS|CXX_MODULES|SOURCES>] [BASE_DIRS [?directory]...] [FILES [?file]...]]...]...)


# Directory compilation and linking defaults

## Add preprocessor definitions to the directory and its targets; function-style definitions are unsupported.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/add_compile_definitions.html)
## function(add_compile_definitions [?definition]...)

## Add compiler options to the directory for targets in this directory and below.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/add_compile_options.html)
## function(add_compile_options [?option]...)

## Add linker options to targets created after this call in this directory and below. Requires CMake 3.13.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/add_link_options.html)
## function(add_link_options [?option]...)

## Add include paths to the directory and targets in the current CMakeLists file. Prefer target_include_directories for per-target requirements.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/include_directories.html)
## function(include_directories [AFTER|BEFORE] [SYSTEM] [?directory]...)

## Set linker search paths for subsequently created targets. Prefer target_link_directories or full library paths.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/link_directories.html)
## function(link_directories [AFTER|BEFORE] [?directory]...)

## Set libraries for subsequently created targets in this directory and below. Prefer target_link_libraries.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/link_libraries.html)
## function(link_libraries [?library_or_flag]...)

## Add definitions or compiler flags to the current directory. Prefer add_compile_definitions and add_compile_options.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/add_definitions.html)
## function(add_definitions [?flag]...)

## Remove definitions previously added by add_definitions in the current directory.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/remove_definitions.html)
## function(remove_definitions [?flag]...)

## Collect source filenames from a directory into a variable. New files do not automatically trigger CMake regeneration.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/aux_source_directory.html)
## function(aux_source_directory <?directory> <&output>)


# Build object properties and IDE organization

## Read a target property into a variable, or output-NOTFOUND if absent.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_target_property.html)
## function(get_target_property <&output> <t:target> <?property>)

## Set target properties using name/value pairs. Alias targets cannot be modified.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/set_target_properties.html)
## function(set_target_properties <t:target>... PROPERTIES <?property> <?value> [?property ?value]...)

## Read a source-file property in the selected directory scope, or NOTFOUND if absent.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_source_file_property.html)
## function(get_source_file_property <&output> <?source> [DIRECTORY <?directory>] [TARGET_DIRECTORY <t:target>] <?property>)

## Set source-file properties using name/value pairs, optionally in other directory scopes (CMake 3.18).
## [Documentation](https://cmake.org/cmake/help/v4.4/command/set_source_files_properties.html)
## function(set_source_files_properties <?source>... [DIRECTORY <?directory>...] [TARGET_DIRECTORY <t:target>...] PROPERTIES <?property> <?value> [?property ?value]...)

## Read a test property, or NOTFOUND if absent. DIRECTORY requires CMake 3.28.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_test_property.html)
## function(get_test_property <?test> <?property> [DIRECTORY <?directory>] <&output>)

## Set test properties using name/value pairs. DIRECTORY requires CMake 3.28.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/set_tests_properties.html)
## function(set_tests_properties <?test>... [DIRECTORY <?directory>] PROPERTIES <?property> <?value> [?property ?value]...)

## Read a target property, its presence, or its documentation.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_property.html)
## function(get_property <&output> TARGET <t:target> PROPERTY <?property> [SET|DEFINED|BRIEF_DOCS|FULL_DOCS])

## Query a source-file property in the selected directory scope.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_property.html)
## function(get_property <&output> SOURCE <?source> [DIRECTORY <?directory>] [TARGET_DIRECTORY <t:target>] PROPERTY <?property> [SET|DEFINED|BRIEF_DOCS|FULL_DOCS])

## Query a test property in the selected directory scope.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_property.html)
## function(get_property <&output> TEST <?test> [DIRECTORY <?directory>] PROPERTY <?property> [SET|DEFINED|BRIEF_DOCS|FULL_DOCS])

## Query properties of an installed file.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_property.html)
## function(get_property <&output> INSTALL <?file> PROPERTY <?property> [SET|DEFINED|BRIEF_DOCS|FULL_DOCS])

## Query a target file-set property. Requires CMake 4.3.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/get_property.html)
## function(get_property <&output> FILE_SET <?set> TARGET <t:target> PROPERTY <?property> [SET|DEFINED|BRIEF_DOCS|FULL_DOCS])

## Set or append properties on targets.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/set_property.html)
## function(set_property TARGET [t:target]... [APPEND] [APPEND_STRING] PROPERTY <?property> [?value]...)

## Set or append source-file properties in the selected directory scopes.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/set_property.html)
## function(set_property SOURCE [?source]... [DIRECTORY <?directory>...] [TARGET_DIRECTORY <t:target>...] [APPEND] [APPEND_STRING] PROPERTY <?property> [?value]...)

## Set or append test properties.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/set_property.html)
## function(set_property TEST [?test]... [DIRECTORY <?directory>] [APPEND] [APPEND_STRING] PROPERTY <?property> [?value]...)

## Set or append installed-file properties, which may contain CPack generator expressions.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/set_property.html)
## function(set_property INSTALL [?file]... [APPEND] [APPEND_STRING] PROPERTY <?property> [?value]...)

## Set or append properties on target file sets. Requires CMake 4.3.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/set_property.html)
## function(set_property FILE_SET <?set>... TARGET <t:target> [APPEND] [APPEND_STRING] PROPERTY <?property> [?value]...)

## Define a custom property's documentation, inheritance and optional target-property initialization.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/define_property.html)
## function(define_property <GLOBAL|DIRECTORY|TARGET|SOURCE|TEST|VARIABLE|CACHED_VARIABLE> PROPERTY <?name> [INHERITED] [BRIEF_DOCS <?text>...] [FULL_DOCS <?text>...] [INITIALIZE_FROM_VARIABLE <?variable>])

## Group source files in generated IDE projects.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/source_group.html)
## function(source_group <?name> [FILES [?source]...] [REGULAR_EXPRESSION <?regex>])

## Group sources by their directory structure under a root. Requires CMake 3.8.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/source_group.html)
## function(source_group TREE <?root> [PREFIX <?prefix>] [FILES [?source]...])


# Installation and build-tree exports

## Install target artifacts and file sets. Options select EXPORT, destinations, artifact kinds, components, configurations and runtime dependencies.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/install.html)
## function(install TARGETS [t:target]... [?option]...)

## Install files or executable scripts. Options include TYPE or DESTINATION, PERMISSIONS, CONFIGURATIONS, COMPONENT, RENAME and OPTIONAL.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/install.html)
## function(install <FILES|PROGRAMS> [?file]... [?option]...)

## Install directory contents with destination, permissions, component and PATTERN/REGEX filtering options. A trailing slash omits the directory name.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/install.html)
## function(install DIRECTORY [?directory]... [?option]...)

## Execute a CMake script or inline code during installation, optionally for a component or ALL_COMPONENTS.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/install.html)
## function(install <SCRIPT|CODE> <?script_or_code> [?option]...)

## Install a target export set. Supports NAMESPACE, FILE, CONFIGURATIONS, COMPONENT and CXX_MODULES_DIRECTORY.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/install.html)
## function(install EXPORT <?export_name> DESTINATION <?directory> [?option]...)

## Install runtime artifacts of imported executable, shared-library or module targets. Requires CMake 3.21.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/install.html)
## function(install IMPORTED_RUNTIME_ARTIFACTS <t:target>... [?option]...)

## Install runtime dependencies collected into a named set, with directory and regex filters. Requires CMake 3.21.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/install.html)
## function(install RUNTIME_DEPENDENCY_SET <?set> [?option]...)

## Export explicitly listed build-tree targets using FILE or ANDROID_MK, with optional NAMESPACE and APPEND.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/export.html)
## function(export TARGETS [t:target]... [?option]...)

## Export build-tree targets associated with an install export set, optionally selecting FILE and NAMESPACE.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/export.html)
## function(export EXPORT <?export_name> [?option]...)

## Register the current build directory in the user package registry, subject to CMAKE_EXPORT_PACKAGE_REGISTRY and policy CMP0090.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/export.html)
## function(export PACKAGE <?package>)


# Testing and compiler probes

## Enable generation of CTest tests for the current directory and below. Normally called at the top level.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/enable_testing.html)
## function(enable_testing)

## Register a CTest test. Supports CONFIGURATIONS, WORKING_DIRECTORY, COMMAND_EXPAND_LISTS and BUILD_DEPENDS; executable targets are resolved at test time.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/add_test.html)
## function(add_test NAME <?name> COMMAND <?command> [?argument_or_option]...)

## Register a test using the legacy signature, without target-name substitution or generator-expression support.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/add_test.html)
## function(add_test <?name> <?command> [?argument]...)

## Configure test-time discovery using DISCOVERY_ARGS, DISCOVERY_MATCH, TEST_NAME and TEST_ARGS, with optional discovery/test properties. Requires CMake 4.4.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/discover_tests.html)
## function(discover_tests COMMAND <?command> [?argument_or_option]...)

## Try building a whole project and return success. This signature requires CMake 3.25; NO_LOG requires 3.26.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/try_compile.html)
## function(try_compile <&compile_result> PROJECT <?project> SOURCE_DIR <?source_dir> [BINARY_DIR <?binary_dir>] [TARGET <?target>] [LOG_DESCRIPTION <?text>] [NO_CACHE] [NO_LOG] [CMAKE_FLAGS [?flag]...] [OUTPUT_VARIABLE <&output>])

## Try compiling source files; accepts SOURCES or SOURCE_FROM_CONTENT/VAR/FILE, compiler/link options and output variables. Legacy forms start with a binary directory.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/try_compile.html)
## function(try_compile <&compile_result> <?source_or_option>...)

## Compile and run source files, storing compile success and the process exit code or FAILED_TO_RUN. Supports source, compiler/link, output and execution options.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/try_run.html)
## function(try_run <&run_result> <&compile_result> <?source_or_option>...)

## Construct a cmake --build command line. PROJECT_NAME is legacy and causes a warning.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/build_command.html)
## function(build_command <&output> [CONFIGURATION <?configuration>] [PARALLEL_LEVEL <?parallel>] [TARGET <?target>] [PROJECT_NAME <?project>])

## Request file API replies for this generation step. API_VERSION must be 1. Requires CMake 3.27.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_file_api.html)
## function(cmake_file_api QUERY API_VERSION <?version> [CODEMODEL <?version>...] [CACHE <?version>...] [CMAKEFILES <?version>...] [TOOLCHAINS <?version>...])

## Configure project instrumentation with HOOKS, OPTIONS, repeated CALLBACK and CUSTOM_CONTENT entries. Requires CMake 4.3.
## [Documentation](https://cmake.org/cmake/help/v4.4/command/cmake_instrumentation.html)
## function(cmake_instrumentation API_VERSION <?api_version> DATA_VERSION <?data_version> [?option]...)

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

# Build-system variables

## Default add_library to SHARED instead of STATIC when no explicit library type is given.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/BUILD_SHARED_LIBS.html)
## set(BUILD_SHARED_LIBS)

## Build configuration for single-configuration generators, such as Debug, Release, RelWithDebInfo or MinSizeRel.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_BUILD_TYPE.html)
## set(CMAKE_BUILD_TYPE)

## Available build configurations for multi-configuration generators such as Visual Studio, Xcode and Ninja Multi-Config.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_CONFIGURATION_TYPES.html)
## set(CMAKE_CONFIGURATION_TYPES)

## Toolchain file read early to configure compilers, utilities and target-platform settings.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_TOOLCHAIN_FILE.html)
## set(CMAKE_TOOLCHAIN_FILE)

## Whether CMake considers this a cross build, usually because CMAKE_SYSTEM_NAME was set manually; platform-specific limitations apply.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_CROSSCOMPILING.html)
## set(CMAKE_CROSSCOMPILING)

## Operating-system name of the target platform.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_SYSTEM_NAME.html)
## set(CMAKE_SYSTEM_NAME)

## Processor value for the target system; native builds generally inherit the host value, which need not match the compiler architecture.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_SYSTEM_PROCESSOR.html)
## set(CMAKE_SYSTEM_PROCESSOR)

## Compiler sysroot and prefix for find-command searches. May only be set in a toolchain file.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_SYSROOT.html)
## set(CMAKE_SYSROOT)

## Native build tool selected by the generator, as an executable path or command name.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_MAKE_PROGRAM.html)
## set(CMAKE_MAKE_PROGRAM)

## Generate compile_commands.json with exact compiler invocations. Supported by Makefile and Ninja generators.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_EXPORT_COMPILE_COMMANDS.html)
## set(CMAKE_EXPORT_COMPILE_COMMANDS)

## Initial C_STANDARD property for targets created after this variable is set.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_C_STANDARD.html)
## set(CMAKE_C_STANDARD)

## Initial C_STANDARD_REQUIRED property, controlling whether targets may fall back to an older C standard.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_C_STANDARD_REQUIRED.html)
## set(CMAKE_C_STANDARD_REQUIRED)

## Initial C_EXTENSIONS property, controlling compiler-specific C language extensions.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_C_EXTENSIONS.html)
## set(CMAKE_C_EXTENSIONS)

## Initial CXX_STANDARD property for subsequently created targets.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_CXX_STANDARD.html)
## set(CMAKE_CXX_STANDARD)

## Initial CXX_STANDARD_REQUIRED property, controlling whether targets may fall back to an older C++ standard.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_CXX_STANDARD_REQUIRED.html)
## set(CMAKE_CXX_STANDARD_REQUIRED)

## Initial CXX_EXTENSIONS property, controlling compiler-specific C++ language extensions.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_CXX_EXTENSIONS.html)
## set(CMAKE_CXX_EXTENSIONS)

## Initial POSITION_INDEPENDENT_CODE property for non-SHARED/non-MODULE targets; also used by try_compile.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_POSITION_INDEPENDENT_CODE.html)
## set(CMAKE_POSITION_INDEPENDENT_CODE)

## Initial INTERPROCEDURAL_OPTIMIZATION property for subsequently created targets.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_INTERPROCEDURAL_OPTIMIZATION.html)
## set(CMAKE_INTERPROCEDURAL_OPTIMIZATION)

## Initial output directory for runtime artifacts of subsequently created targets.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_RUNTIME_OUTPUT_DIRECTORY.html)
## set(CMAKE_RUNTIME_OUTPUT_DIRECTORY)

## Initial output directory for library artifacts of subsequently created targets.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_LIBRARY_OUTPUT_DIRECTORY.html)
## set(CMAKE_LIBRARY_OUTPUT_DIRECTORY)

## Initial output directory for archive artifacts of subsequently created targets.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_ARCHIVE_OUTPUT_DIRECTORY.html)
## set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY)

## Installation prefix used for relative install destinations; cmake --install --prefix can override it at install time.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_INSTALL_PREFIX.html)
## set(CMAKE_INSTALL_PREFIX)

## Initial runtime search path for installed targets, expressed as a semicolon-separated list.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_INSTALL_RPATH.html)
## set(CMAKE_INSTALL_RPATH)

## Additional build-tree runtime search paths used to initialize newly created targets.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_BUILD_RPATH.html)
## set(CMAKE_BUILD_RPATH)

## Omit runtime search path information from built and installed binaries.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_SKIP_RPATH.html)
## set(CMAKE_SKIP_RPATH)

## Show full command lines during Makefile builds.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_VERBOSE_MAKEFILE.html)
## set(CMAKE_VERBOSE_MAKEFILE)

## Initial COMPILE_WARNING_AS_ERROR property for targets. Requires CMake 3.24.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_COMPILE_WARNING_AS_ERROR.html)
## set(CMAKE_COMPILE_WARNING_AS_ERROR)

## Name of the most recent project() in the current directory scope or a parent scope.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/PROJECT_NAME.html)
## set(PROJECT_NAME)

## Source directory of the most recent project() in the current directory scope or a parent scope.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/PROJECT_SOURCE_DIR.html)
## set(PROJECT_SOURCE_DIR)

## Build directory of the most recent project() in the current scope.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/PROJECT_BINARY_DIR.html)
## set(PROJECT_BINARY_DIR)

## Whether the most recent project() in the current scope or above came from the top-level CMakeLists file. Requires CMake 3.21.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/PROJECT_IS_TOP_LEVEL.html)
## set(PROJECT_IS_TOP_LEVEL)

## Version supplied to the most recent project() call, or an empty string when omitted.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/PROJECT_VERSION.html)
## set(PROJECT_VERSION)

## Name set by project() in the top-level CMakeLists file.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_PROJECT_NAME.html)
## set(CMAKE_PROJECT_NAME)

## Target type for try_compile source probes: EXECUTABLE (default) or STATIC_LIBRARY to avoid linking an executable.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_TRY_COMPILE_TARGET_TYPE.html)
## set(CMAKE_TRY_COMPILE_TARGET_TYPE)

## Host command and optional arguments used to run target executables during cross compilation and initialize target emulator properties.
## [Documentation](https://cmake.org/cmake/help/v4.4/variable/CMAKE_CROSSCOMPILING_EMULATOR.html)
## set(CMAKE_CROSSCOMPILING_EMULATOR)
