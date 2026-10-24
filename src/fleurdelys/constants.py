from pathlib import Path

# Built-in Variables with descriptions
BUILTIN_VARIABLES = {
    "CARTETHYIA": "Undefined if running under normal CMake, true otherwise.",
    "CMAKE_SOURCE_DIR": "The path to the top level of the source tree.",
    "CMAKE_CURRENT_LIST_DIR": "The directory containing the CMake list file currently being processed.",
    "CMAKE_CURRENT_LIST_FILE": "The full path to the CMake list file currently being processed.",
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


# Wheels bundle the annotations inside the package; source checkouts keep them
# at the repository root.
CORE_ANNOTATIONS = Path(__file__).resolve().parent / "annotations" / "core.cmake"
if not CORE_ANNOTATIONS.is_file():
    CORE_ANNOTATIONS = Path(__file__).resolve().parents[2] / "annotations" / "core.cmake"
