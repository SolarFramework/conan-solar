cmake_minimum_required(VERSION 2.8)
project(conanWrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory("source_subfolder")