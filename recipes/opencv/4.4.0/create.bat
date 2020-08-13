@echo on
conan create . conan-solar/stable -tf None --build=missing -s compiler.cppstd=17 -o shared=True
conan create . conan-solar/stable -tf None --build=missing -s compiler.cppstd=17 -s build_type=Debug -o shared=True
conan create . conan-solar/stable -tf None --build=missing -s compiler.cppstd=17 -o shared=True -o contrib=True -o nonfree=True -o harfbuzz=False -o gflags=False -o glog=False
conan create . conan-solar/stable -tf None --build=missing -s compiler.cppstd=17 -s build_type=Debug  -o shared=True -o contrib=True -o nonfree=True -o harfbuzz=False -o gflags=False -o glog=False


