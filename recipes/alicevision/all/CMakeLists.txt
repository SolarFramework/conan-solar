cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

conan_basic_setup()

add_subdirectory("source_subfolder")
