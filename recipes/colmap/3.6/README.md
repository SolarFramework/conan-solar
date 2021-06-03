# conan colmap

Conan package for colmap library 3.6

	conan create . 3.6@@conan-solar/stable -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True

depends :

- libjpeg: 

		conan create . 9d@@conan-solar/stable -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True

- jxrlib :

		conan create . v2019.10.9@conan-solar/stable -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Debug --build=missing

- freeimage (depends of libjpeg and jrxlib)

		conan create . 3.18.0@@conan-solar/stable -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True

- flann

		conan create . 1.9.1@@conan-solar/stable -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True

- Ceres

		conan create . 2.0.0@@conan-solar/stable -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True -o use_glog=True -o use_gflags=True -o use_cxsparse=False