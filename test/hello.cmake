if(CARTETHYIA)
	message(STATUS "Running under Cartethyia")
else()
	message(STATUS "Running under CMake")
endif()
target_include_directories(foo PRIVATE bar)
string(FIND "Hello" "world" outputvar REVERSE)
message(STATUS "${outputvar}")
message(STATUS "$ENV{HOME}")

##cmake-ls: signature <v&:bar>
function(foo bar)
	message(STATUS "${ARGV}")
endfunction()

# Stuff
##cmake-ls: define BAR

message(STATUS "${BAR}")