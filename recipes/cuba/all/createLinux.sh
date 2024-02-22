#!/bin/bash
conan create . --name cuba --version 2.1.0 --channel conan-solar --user 1_1_0 -tf "" --build=missing
conan create . --name cuba --version 2.1.0 --channel conan-solar --user 1_1_0 -tf "" --build=missing -s build_type=Debug



