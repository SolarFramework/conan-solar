# conan flann

Conan package for flann library

fixed for cpp std17 build

1.9.1 version used in colmap

	conan create . 1.9.1@ -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True