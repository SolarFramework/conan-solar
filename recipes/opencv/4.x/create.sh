#!/bin/bash
conan create . opencv/4.5.5@ -tf None --build=missing -s compiler.cppstd=17 -o shared=True
conan create . opencv/4.5.5@ -tf None --build=missing -s compiler.cppstd=17 -s build_type=Debug -o shared=True
conan create . opencv/4.5.5@ -tf None --build=missing -s compiler.cppstd=17 -o shared=True -o contrib=True -o with_cuda=True -o with_cublas=True -o with_cudnn=True -o dnn=True -o dnn_cuda=True -o cuda_arch_bin="75 80 86"
conan create . opencv/4.5.5@ -tf None --build=missing -s compiler.cppstd=17 -s build_type=Debug  -o shared=True -o contrib=True -o with_cuda=True -o with_cublas=True -o with_cudnn=True -o dnn=True -o dnn_cuda=True -o cuda_arch_bin="75 80 86"


