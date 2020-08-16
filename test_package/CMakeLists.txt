project(PackageTest CXX)
cmake_minimum_required(VERSION 2.8.12)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(ios-test test.cpp)
set_target_properties(ios-test PROPERTIES MACOSX_BUNDLE FALSE)
target_link_libraries(ios-test ${CONAN_LIBS})
message(STATUS "Libraries: ${CONAN_LIBS}")
