# conan colmap

describes colmap build with a conan recipe

colmap can be build with msvc2017 (compiler.version=15, with a patch applied to sources) or msvc 2019 (compiler.version=16)

## Dependencies : 

- official Flann recipe doesn't build with cppstd 17 then use Flann recipe conan-solar git repository 
- Ceres in Debug mode use glog in Release mode then build Colmap with Ceres in Release mode to avoid issue : ceres-solver:build_type=Release


## Build dependencies

## Build Colmap

Conan package for Gprc 1.71.0 with protobuf 6.32

- Debug version :

		conan create . --name grpc --version 1.71.0 -tf "" -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True

- Release version :

		conan create . --name grpc --version 1.71.0 -tf "" -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Release --build=missing -o shared=True

		