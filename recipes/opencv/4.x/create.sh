#!/bin/bash
conan create . --name=opencv --version=4.7.0 --user=conan-solar --channel=1_1_0 -tf "" --build=missing -s compiler.cppstd=17 -o ffmpeg/*:with_pulse=False -o ffmpeg/*:with_libfdk_aac=False -o ffmpeg/*:with_libmp3lame=False -o ffmpeg/*:with_libalsa=False -o ffmpeg/*:with_libx264=False -o ffmpeg/*:with_libx265=False -o ffmpeg/*:with_openjpeg=False
conan create . --name=opencv --version=4.7.0 --user=conan-solar --channel=1_1_0 -tf "" --build=missing -s compiler.cppstd=17 -s build_type=Debug -o ffmpeg/*:with_pulse=False -o ffmpeg/*:with_libfdk_aac=False -o ffmpeg/*:with_libmp3lame=False -o ffmpeg/*:with_libalsa=False -o ffmpeg/*:with_libx264=False -o ffmpeg/*:with_libx265=False -o ffmpeg/*:with_openjpeg=False
conan create . --name=opencv --version=4.7.0 --user=conan-solar --channel=1_1_0 -tf "" --build=missing -s compiler.cppstd=17 -o ffmpeg/*:with_pulse=False -o ffmpeg/*:with_libfdk_aac=False -o ffmpeg/*:with_libmp3lame=False -o ffmpeg/*:with_libalsa=False -o ffmpeg/*:with_libx264=False -o ffmpeg/*:with_libx265=False -o ffmpeg/*:with_openjpeg=False -o opencv/*:contrib=True -o opencv/*:with_cuda=True -o opencv/*:with_cublas=True -o opencv/*:with_cudnn=True -o opencv/*:dnn=True -o opencv/*:dnn_cuda=True
conan create . --name=opencv --version=4.7.0 --user=conan-solar --channel=1_1_0 -tf "" --build=missing -s compiler.cppstd=17 -s build_type=Debug -o ffmpeg/*:with_pulse=False -o ffmpeg/*:with_libfdk_aac=False -o ffmpeg/*:with_libmp3lame=False -o ffmpeg/*:with_libalsa=False -o ffmpeg/*:with_libx264=False -o ffmpeg/*:with_libx265=False -o ffmpeg/*:with_openjpeg=False -o opencv/*:contrib=True -o opencv/*:with_cuda=True -o opencv/*:with_cublas=True -o opencv/*:with_cudnn=True -o opencv/*:dnn=True -o opencv/*:dnn_cuda=True




