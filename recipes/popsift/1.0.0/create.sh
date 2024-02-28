#!/bin/bash
conan create . popsift/1.0.0-rc3@conan-solar/1_1_0 --build=missing -tf None
conan create . popsift/1.0.0-rc3@conan-solar/1_1_0 --build=missing -tf None -s build_type=Debug




