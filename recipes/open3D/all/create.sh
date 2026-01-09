#!/bin/bash
conan create . --name open3d --version v0.19.0 --user conan-solar --channel 1_5_0 --build=missing -tf ""
conan create . --name open3d --version v0.19.0 --user conan-solar --channel 1_5_0 --build=missing -tf "" -s build_type=Debug




