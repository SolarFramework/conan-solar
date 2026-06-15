cmake_minimum_required(VERSION 3.15)
project(test_ifcplusplus CXX)

find_package(ifcplusplus REQUIRED CONFIG)

add_executable(test_ifcplusplus test_package.cpp)
target_link_libraries(test_ifcplusplus PRIVATE IFCPP::IfcPlusPlus)
