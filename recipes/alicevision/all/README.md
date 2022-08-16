# Pre requeries
- Install git

# Linux environment
- emulation with wsl2
- OS: ubuntu 20.04

# command lines validate on Window and Linux
conan create all v2.4.0@ -tf None -s compiler.cppstd=14 -s build_type=Debug --build=missing -o shared=True -o with_cuda=False -o boost:shared=True -o flann:shared=False -o ceres-solver:shared=True -o geogram:shared=True -o openimageio:shared=True -o with_popsift=True -o popsift:shared=True -o with_opengv=True
conan create all v2.4.0@ -tf None -s compiler.cppstd=14 -s build_type=Debug --build=missing -o shared=True -o with_cuda=True -o boost:shared=True -o flann:shared=False -o ceres-solver:shared=True -o geogram:shared=True -o openimageio:shared=True -o with_popsift=True -o popsift:shared=True -o with_opengv=True

# command lines validate on Window
conan create all v2.4.0@ -tf None -s compiler.cppstd=14 -s build_type=Debug --build=missing -o shared=True -o with_cuda=True -o boost:shared=True -o flann:shared=False -o ceres-solver:shared=True -o geogram:shared=True -o openimageio:shared=True -o with_popsift=False -o popsift:shared=True -o with_opengv=True
conan create all v2.4.0@ -tf None -s compiler.cppstd=14 -s build_type=Debug --build=missing -o shared=True -o with_cuda=True -o boost:shared=True -o flann:shared=False -o ceres-solver:shared=True -o geogram:shared=True -o openimageio:shared=True -o with_popsift=True -o popsift:shared=True -o with_opengv=False
conan create all v2.4.0@ -tf None -s compiler.cppstd=14 -s build_type=Debug --build=missing -o shared=True -o with_cuda=True -o boost:shared=True -o flann:shared=False -o ceres-solver:shared=True -o geogram:shared=True -o openimageio:shared=True -o with_popsift=False -o popsift:shared=True -o with_opengv=False
conan create all v2.4.0@ -tf None -s compiler.cppstd=14 -s build_type=Debug --build=missing -o shared=True -o with_cuda=True -o boost:shared=True -o flann:shared=False -o ceres-solver:shared=True -o geogram:shared=True -o openimageio:shared=True -o with_popsift=True -o popsift:shared=True -o with_opengv=True


# Test Cpp-std 17
conan create all v2.4.0@ -tf None -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True -o with_cuda=False -o boost:shared=True -o flann:shared=False -o ceres-solver:shared=True -o geogram:shared=True -o openimageio:shared=True -o with_popsift=False -o popsift:shared=True -o with_opengv=False -o openimageio:with_tbb=False

# changes and fix history :

- conanfile.py :

	- ```self.options['openimageio'].with_tbb = False``` :	 otherwise issue on build	
	- ```cmake.definitions["ALICEVISION_BUILD_DOC"] = "OFF"``` : not mandatory (issue on build?)
        
	- add conan dependencies (then remove internal dependencies in CMakeLists) :
	
		```self.requires("coin-utils/2.11.4")```

        ```self.requires("coin-osi/0.108.6")```

        ```self.requires("coin-clp/1.17.6")``` 

- patches :
	- alicevision-cmake-helpers.patch : part of old alicevision-cmake-search-ceres-flann-opengv-openimageio-popsift.patch for isolate Helpers.cmake changes
	- alicevision-cmake-search-ceres-flann-opengv-openimageio-popsift-coin-utils-clp-osi.patch : old alicevision-cmake-search-ceres-flann-opengv-openimageio-popsift.patch and new changes for take coin-utils, coin-osi, and coin-clp as externals dependencies
	- alicevision-code-cppstd17.patch : fix alicevision code for cpp-std17
	- MeshSDFilter-OpenMesh-code-cppstd17.patch : fix MeshSDFilter submodule for cpp-std17	

## TODO

only tested on windows, TODO Linux