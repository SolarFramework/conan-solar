# conan libjpeg

Conan package for libjpeg library

9d version used in freeimage

	conan create . 9d@ -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True 