conan create . --version master --user conan-solar --channel stable --build=missing -tf "" -o use_CUDA=True -o use_glog=True
conan create . --version master --user conan-solar --channel stable --build=missing -tf "" -o use_CUDA=True -o use_glog=True -s build_type=Debug
conan create . --version master --user conan-solar --channel stable --build=missing -tf "" -o use_glog=True
conan create . --version master --user conan-solar --channel stable --build=missing -tf "" -o use_glog=True -s build_type=Debug

