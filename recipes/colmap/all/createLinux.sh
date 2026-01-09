#!/bin/bash
conan create . --name colmap --version 3.13 --user conan-solar --channel stable -tf "" --build=missing -o freeimage/*:with_openexr=False -o freeimage/*:with_tiff=False -o *:with_cuda=True -o libglvnd/*:gles1=False -o libglvnd/*:gles2=False
conan create . --name colmap --version 3.13 --user conan-solar --channel stable -tf "" --build=missing -o freeimage/*:with_openexr=False -o freeimage/*:with_tiff=False -o *:with_cuda=True -o libglvnd/*:gles1=False -o libglvnd/*:gles2=False -s build_type=Debug



