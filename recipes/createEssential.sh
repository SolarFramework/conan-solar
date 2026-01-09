#!/bin/bash

pushd ./opencv/4.x/
./createLinux.sh
popd

pushd ./colmap/all
./createLinux.sh
popd

pushd ./g2o/all
./create.sh
popd

pushd ./ceres-sover/all
./create.sh
popd