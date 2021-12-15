# conan-ceres

Conan package for ceres library

2.0.0 version used in colmap

conan create . 2.0.0@ -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True -o use_glog=True -o use_gflags=True -o use_cxsparse=False