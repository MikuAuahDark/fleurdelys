# Test Meta Commands

# This is a description for MY_VAR
##cmake-ls: define MY_VAR

# This is a description for MY_FUNC
##cmake-ls: signature <ARG1> <ARG2>
function(my_func)
endfunction()

# Testing signature mismatch
my_func(A) # Error: Invalid arguments (expected <ARG1> <ARG2>)
my_func(A B) # OK

# Testing default signature
function(default_func arg1 arg2)
endfunction()
default_func(X) # Error: Invalid arguments (expected <arg1> <arg2>)

# Testing misplaced signature
##cmake-ls: signature <FOO>
set(X 1) # Warning: Signature override must be followed by function or macro.

# Testing unknown meta command
##cmake-ls: unknown_cmd
