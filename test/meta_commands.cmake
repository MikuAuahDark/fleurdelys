# Test annotation declarations

## This is a description for MY_VAR
## set(MY_VAR 1)

## This is a description for MY_FUNC
## function(my_func <?ARG1> <?ARG2>)
function(my_func)
endfunction()

# Testing signature mismatch
my_func(A) # Error: Invalid arguments (expected two arguments)
my_func(A B) # OK

# Testing default signature
function(default_func arg1 arg2)
endfunction()
default_func(X) # Error: Invalid arguments (expected two arguments)

# An annotation need not have an implementation.
## function(external FOO)
external(FOO)

# Testing malformed annotation
## function(broken [FOO)
