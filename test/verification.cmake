# message() overloads
message(STATUS "Hello")        # OK
message(FATAL_ERROR "Error")   # OK
message("Plain")               # OK
message(INVALID "oops")        # ERROR: Invalid arguments

# target_include_directories()
target_include_directories(mytgt PUBLIC inc1 inc2)      # OK
target_include_directories(mytgt SYSTEM PRIVATE inc)    # OK
target_include_directories(mytgt BEFORE PUBLIC inc)    # OK
target_include_directories(mytgt PRIVATE)               # ERROR: missing items
target_include_directories()                            # ERROR: missing target

# list()
list(APPEND mylist "item")     # OK
list(INVALID_SUB mylist)        # ERROR: Invalid arguments
list(SORT mylist COMPARE STRING ORDER DESCENDING) # OK

# string()
string(APPEND myvar "hello")   # OK
string(REGEX MATCH ".*" out "in") # OK
string(INVALID_SUB out "in")    # ERROR: Invalid arguments

# Built-in variables (hover test)
message(STATUS "${CMAKE_VERSION}")     # OK
message(STATUS "${PROJECT_NAME}")      # OK
message(STATUS "${UNDEFINED_VAR}")     # WARNING: may be undefined

# Namespace tests
message(STATUS "$ENV{PATH}")           # OK
message(STATUS "$CACHE{CMAKE_INSTALL_PREFIX}") # OK
message(STATUS "$INVALID_NS{MYVAR}")   # ERROR: Unknown variable namespace '$INVALID_NS{'

# Cache set/unset
set(CACHE{MY_CACHE_VAR} "value")       # OK
message(STATUS "${MY_CACHE_VAR}")      # WARNING: may be undefined (CACHE{VAR} != VAR)
message(STATUS "$CACHE{MY_CACHE_VAR}") # OK
unset(CACHE{MY_CACHE_VAR})             # OK
