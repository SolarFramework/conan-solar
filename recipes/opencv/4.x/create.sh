#!/bin/bash
conan create . opencv/4.7.0@conan-solar/1_1_0 -tf None --build=missing -s compiler.cppstd=17
conan create . opencv/4.7.0@conan-solar/1_1_0 -tf None --build=missing -s compiler.cppstd=17 -s build_type=Debug
conan create . opencv/4.7.0@conan-solar/1_1_0 -tf None --build=missing -s compiler.cppstd=17 -o contrib=True -o with_cuda=True -o with_cublas=True -o with_cudnn=True -o dnn=True -o dnn_cuda=True
conan create . opencv/4.7.0@conan-solar/1_1_0 -tf None --build=missing -s compiler.cppstd=17 -s build_type=Debug -o contrib=True -o with_cuda=True -o with_cublas=True -o with_cudnn=True -o dnn=True -o dnn_cuda=True



