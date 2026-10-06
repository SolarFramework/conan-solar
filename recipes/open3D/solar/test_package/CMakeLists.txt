cmake_minimum_required(VERSION 3.16)
project(test_open3d CXX)

find_package(Open3D REQUIRED CONFIG)

add_executable(test_open3d src/example.cpp)
target_link_libraries(test_open3d PRIVATE Open3D::Open3D)
target_compile_features(test_open3d PRIVATE cxx_std_17)
