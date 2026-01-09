#!/bin/bash
conan create . --name cuba --version 2.1.0 --user conan-solar --channel 1_2_0 -tf "" --build=missing -o cuda_arch_bin=7.5 -o eigen/*:MPL2_only=True
conan create . --name cuba --version 2.1.0 --user conan-solar --channel 1_2_0 -tf "" --build=missing -o cuda_arch_bin=7.5 -o eigen/*:MPL2_only=True -s build_type=Debug



