if(CARTETHYIA)
	message(STATUS "Running under Cartethyia")
else()
	message(STATUS "Running under CMake")
endif()
target_include_directories(foo PRIVATE bar)
string(FIND "Hello" "world" outputvar REVERSE)
message(STATUS "${outputvar}")
message(STATUS "$ENV{HOME}")

## function(foo <&bar>)
function(foo bar)
	message(STATUS "${ARGV}")
endfunction()

## Stuff
## set(BAR 1)

message(STATUS "${BAR}")
foo(BAZ)

message(STATUS ${BAZ})
