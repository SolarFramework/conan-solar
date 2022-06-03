# conan colmap

describes colmap build with a conan recipe

colmap can be build with msvc2017 (compiler.version=15, with a patch applied to sources) or msvc 2019 (compiler.version=16)

## Dependencies : 

- official Flann recipe doesn't build with cppstd 17 then use Flann recipe conan-solar git repository 
- Ceres in Debug mode use glog in Release mode then build Colmap with Ceres in Release mode to avoid issue : ceres-solver:build_type=Release


## Build dependencies

### Flann

use conan-solar recipe 

- or build it (for instance in debug version) :
 
	conan create . 1.9.1@conan-solar/stable -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True

### Other dependencies

All others dependencies are retrieved directly when building Colmap directly from conan-center. (no need to use old recipes in conan-solar git repository)

Boost have been update in 1.76.0 for use zlib 1.2.12, and because OpenImageIO recipe uses Boost 1.76.0. 
Boost 1.74.0 uses zlib 1.2.11, and there are conflicts with other recipe already updated with zlib 1.2.12 (FreeImage and others)

list of all recursive dependencies retrieved : 

	boost/1.76.0
    ceres-solver/2.0.0
    colmap/3.7
    eigen/3.4.0
    flann/1.9.1@conan-solar/stable
    freeimage/3.18.0
    gflags/2.2.2
    glew/2.2.0
    glog/0.5.0
    glu/system
    jasper/2.0.33
    jbig/20160605
    jxrlib/cci.20170615
    lcms/2.12
    libdeflate/1.10
    libjpeg/9d
    libpng/1.6.37
    libraw/0.20.2
    libtiff/4.3.0
    libwebp/1.2.2
    lz4/1.9.3
    openexr/2.5.7
    opengl/system
    openjpeg/2.4.0
    xz_utils/5.2.5
    zlib/1.2.12
    zstd/1.5.2

## Build Colmap

Conan package for colmap library 3.7

- Debug version :

		conan create . 3.7@ -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True -s ceres-solver:build_type=Release -o boost:zlib=False -o boost:bzip2=False -o boost:shared=True

- Release version :

		conan create . 3.7@ -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Release --build=missing -o shared=True -o boost:zlib=False -o boost:bzip2=False -o boost:without_stacktrace=True -o boost:shared=True

# TODO Investigations

- QT : use for GUI in colmap. 
colmap cmakelist remove opengl if colmap GUI is disabled.
If GUI is disabled, Qt is not used, and Opengl is not used. OpenGl is needed by Colmap. So there is 'GUI_ENABLED_param_patch.patch' for keep Opengl and fix build.