#!/bin/bash
conan create . --name colmap --version 3.11.0 --user conan-solar --channel stable -tf "" --build=missing -o freeimage/*:with_openexr=False -o freeimage/*:with_libpng=False -o with_openmp=False
conan create . --name colmap --version 3.10 --user conan-solar --channel stable -tf "" --build=missing -o freeimage/*:with_openexr=False -o freeimage/*:with_libpng=False -o with_openmp=False -s build_type=Debug
conan create . --name colmap --version 3.11.0 --user conan-solar --channel stable -tf "" --build=missing -o freeimage/*:with_openexr=False -o freeimage/*:with_libpng=False -o with_openmp=False -o with_cuda=True
conan create . --name colmap --version 3.10 --user conan-solar --channel stable -tf "" --build=missing -o freeimage/*:with_openexr=False -o freeimage/*:with_libpng=False -o with_openmp=False -o with_cuda=True -s build_type=Debug



