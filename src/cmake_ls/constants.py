from typing import TypedDict

# Control flow commands
CONTROL_FLOW = [
    "if",
    "elseif",
    "else",
    "endif",
    "while",
    "endwhile",
    "foreach",
    "endforeach",
    "function",
    "endfunction",
    "macro",
    "endmacro",
    "return",
    "break",
    "continue",
    "block",
    "endblock",
]

# Core utilities (not exhaustive, but covering user request and common ones)
CORE_UTILS = [
    "set",
    "unset",
    "math",
    "list",
    "string",
    "message",
    "option",
    "cmake_minimum_required",
    "project",
    "include",
    "add_executable",
    "add_library",
    "target_link_libraries",
    "target_include_directories",
    "install",
    "file",
    "find_package",
    "configure_file",
]

# Built-in Variables with descriptions
BUILTIN_VARIABLES = {
    "CARTETHYIA": "Undefined if running under normal CMake, true otherwise.",
    "CMAKE_SOURCE_DIR": "The path to the top level of the source tree.",
    "CMAKE_BINARY_DIR": "The path to the top level of the build tree.",
    "PROJECT_NAME": "The name of the project specified in the most recent project() command.",
    "PROJECT_SOURCE_DIR": "The path to the source directory of the current project.",
    "PROJECT_BINARY_DIR": "The path to the build directory of the current project.",
    "CMAKE_VERSION": "The full version of cmake in format major.minor.patch.",
    "CMAKE_COMMAND": "The full path to the cmake executable.",
    "WIN32": "True if the target system is Windows.",
    "UNIX": "True if the target system is Unix-like (including Linux and macOS).",
    "APPLE": "True if the target system is Apple (macOS, iOS, etc.).",
    "MSVC": "True if the compiler is Microsoft Visual C++.",
    "CMAKE_CXX_COMPILER": "The full path to the C++ compiler.",
    "CMAKE_C_COMPILER": "The full path to the C compiler.",
    "BUILD_SHARED_LIBS": "Global flag to cause add_library() to create shared libraries if on.",
    "CMAKE_BUILD_TYPE": "Specifies the build type on single-configuration generators.",
}

# Common Environment Variables
ENV_VARIABLES = {
    "PATH": "System search path for executables.",
    "LD_LIBRARY_PATH": "Search path for shared libraries at runtime (on Unix).",
    "CMAKE_PREFIX_PATH": "Semicolon-separated list of directories specifying installation prefixes of software to be found.",
    "CXX": "Default C++ compiler.",
    "CC": "Default C compiler.",
    "FLAGS": "Default compiler flags.",
    "LDFLAGS": "Default linker flags.",
}

# Common Cache Variables
CACHE_VARIABLES = {
    "CMAKE_INSTALL_PREFIX": "Install directory used by install().",
    "BUILD_SHARED_LIBS": "Global flag to cause add_library() to create shared libraries if on.",
    "CMAKE_EXPORT_COMPILE_COMMANDS": "Enable/Disable output of compile_commands.json for use with clang-based tools.",
}

# Generic Variable Namespace Registry
VARIABLE_NAMESPACES = {
    "": BUILTIN_VARIABLES,
    "ENV": ENV_VARIABLES,
    "CACHE": CACHE_VARIABLES,
}


class _CommandSpecInfo(TypedDict):
    sig: str
    desc: str


# Command Specifications for Validation and Documentation
COMMAND_SPECS: dict[str, list[_CommandSpecInfo]] = {
    "target_include_directories": [
        {
            "sig": "<target> [SYSTEM] [BEFORE|AFTER] <INTERFACE|PUBLIC|PRIVATE> <item> ... [INTERFACE|PUBLIC|PRIVATE <item> ...] ...",
            "desc": "Add include directories to a target.",
        }
    ],
    "string": [
        {
            "sig": "APPEND <var> <input...>",
            "desc": "Append all the `<input>` arguments to the string.",
        },
        {
            "sig": "PREPEND <var> <input...>",
            "desc": "Prepend all the `<input>` arguments to the string.",
        },
        {
            "sig": "CONCAT <var> <input...>",
            "desc": "Concatenate all the `<input>` arguments together and store the result in the named `<output_variable>`.",
        },
        {
            "sig": "FIND <string> <substring> <output_variable> [REVERSE]",
            "desc": "Return the position where the given `<substring>` was found in the supplied `<string>`. If the "
            "`REVERSE` flag was used, the command will search for the position of the last occurrence of the "
            "specified `<substring>`. If the `<substring>` is not found, a position of -1 is returned.\n\nThe "
            "`string(FIND)` subcommand treats all strings as ASCII-only characters. The index stored in "
            "`<output_variable>` will also be counted in bytes, so strings containing multi-byte characters "
            "may lead to unexpected results.",
        },
        {
            "sig": "JOIN <glue> <var> <input> ...",
            "desc": "Join all the `<input>` arguments together using the `<glue>` string and store the result in the "
            "named `<output_variable>`.\n\n"
            "To join a list's elements, prefer to use the `JOIN` operator from the `list()` command. This allows for "
            "the elements to have special characters like `;` in them.",
        },
        {
            "sig": "REGEX <MATCH|MATCHALL|REPLACE> <regex> <outvar> <input...>",
            "desc": "Regular expression operations.",
        },
        {"sig": "LENGTH <string> <outvar>", "desc": "Get the length of a string."},
        {
            "sig": "SUBSTRING <string> <begin> <length> <outvar>",
            "desc": "Get a substring.",
        },
    ],
    "list": [
        {
            "sig": "LENGTH <list> <outvar>",
            "desc": "Get the number of elements in a list.",
        },
        {
            "sig": "GET <list> <index> ... <outvar>",
            "desc": "Get elements at specific indices.",
        },
        {"sig": "APPEND <list> <element> ...", "desc": "Append elements to a list."},
        {"sig": "FIND <list> <value> <outvar>", "desc": "Find the index of a value."},
        {"sig": "REMOVE_ITEM <list> <value> ...", "desc": "Remove items from a list."},
        {"sig": "REMOVE_AT <list> <index> ...", "desc": "Remove items at indices."},
        {
            "sig": "SORT <list> [COMPARE <BINARY|STRING|FILE_STR|VERSION>] [CASE <SENSITIVE|INSENSITIVE>] [ORDER <ASCENDING|DESCENDING>]",
            "desc": "Sort a list.",
        },
    ],
    "message": [
        {"sig": "<message>", "desc": "General message output."},
        {"sig": "STATUS <message>", "desc": "Status message for user feedback."},
        {
            "sig": "FATAL_ERROR <message>",
            "desc": "Stop processing and report an error.",
        },
        {"sig": "WARNING <message>", "desc": "CMake warning."},
        {"sig": "AUTHOR_WARNING <message>", "desc": "Author warning."},
        {"sig": "SEND_ERROR <message>", "desc": "Error, but continue processing."},
        {"sig": "VERBOSE <message>", "desc": "Verbose logs."},
        {"sig": "DEBUG <message>", "desc": "Debug logs."},
        {"sig": "TRACE <message>", "desc": "Trace logs."},
    ],
}

ALL_COMMANDS = sorted(list(set(CONTROL_FLOW + CORE_UTILS)))

COMMAND_SIGNATURES = {}

# Populate signatures from specs
for cmd, overloads in COMMAND_SPECS.items():
    COMMAND_SIGNATURES[cmd] = [f"{cmd}({ov['sig']})" for ov in overloads]

# Add fallback signatures for common commands not in specs
FALLBACK_SIGNATURES = {
    "set": [
        "set(<variable> <value>... [PARENT_SCOPE])",
        "set(CACHE{<variable>} <value>...)",
    ],
    "unset": [
        "unset(<variable> [CACHE | PARENT_SCOPE])",
        "unset(CACHE{<variable>})",
    ],
    "if": ["if(<condition>)"],
    "while": ["while(<condition>)"],
    "foreach": ["foreach(<loop_var> <items>)"],
    "function": ["function(<name> [arg1 [arg2 [arg3 ...]]])"],
    "macro": ["macro(<name> [arg1 [arg2 [arg3 ...]]])"],
    "project": [
        "project(<projectname> [VERSION <major>[.<minor>[.<patch>[.<tweak>]]]] [LANGUAGES <language>...])"
    ],
    "add_executable": [
        "add_executable(<name> [WIN32] [MACOSX_BUNDLE] [EXCLUDE_FROM_ALL] [source1] [source2 ...])"
    ],
    "target_link_libraries": [
        "target_link_libraries(<target> <PRIVATE|PUBLIC|INTERFACE> <item>...)"
    ],
}
for cmd, sigs in FALLBACK_SIGNATURES.items():
    if cmd not in COMMAND_SIGNATURES:
        COMMAND_SIGNATURES[cmd] = sigs
