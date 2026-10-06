#!/bin/bash
conan create . --name open3d --version 0.19.0 --user conan-solar --channel stable -tf "" --build=missing -s compiler.cppstd=17 -o "open3d/*:with_cuda=True"
conan create . --name open3d --version 0.19.0 --user conan-solar --channel stable -tf "" --build=missing -s compiler.cppstd=17 -o "open3d/*:with_cuda=True" -s build_type=Debug
conan create . --name open3d --version 0.19.0 --user conan-solar --channel stable -tf "" --build=missing -s compiler.cppstd=17
