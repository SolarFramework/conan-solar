#!/bin/bash
conan create . --name g2o --version 20230223 --user conan-solar --channel 1_2_0 --build=missing -tf ""
conan create . --name g2o --version 20230223 --user conan-solar --channel 1_2_0 --build=missing -tf "" -s build_type=Debug




