#!/bin/bash
conan create . cuba/2.0.0@conan-solar/1_1_0 -tf None --build=missing
conan create . cuba/2.0.0@conan-solar/1_1_0 -tf None --build=missing -s build_type=Debug



