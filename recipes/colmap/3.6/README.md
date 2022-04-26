# conan colmap

colmap only build with msvc 2019 (compiler.version=16)

## Dependencies : 

- official Flann recipe doesn't build with cppstd 17 then use Flann recipe conan-solar git repository 
- Ceres in Debug mode use glog in Release mode then build Colmap with Ceres in Release mode to avoid issue : ceres-solver:build_type=Release


## Build dependencies

### Flann

use conan-solar recipe 

- Debug version :
 
	conan create . 1.9.1@ -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True -s compiler.version=16

- Release version : change with build_type=Release

### Other dependencies

All others dependencies are retrieved directly when building Colmap directly from conan-center. (no need to use old recipes in conan-solar git repository)

Boost have been update in 1.75.0 for use zlib 1.2.12. Boost 1.74.0 uses zlib 1.2.11, and there are conflicts with other recipe already updated with zlib 1.2.12 (FreeImage and others)

list of all recursive dependencies retrieved : 

	boost/1.75.0
	brotli/1.0.9
	bzip2/1.0.8
	ceres-solver/2.0.0
	double-conversion/3.2.0
	eigen/3.4.0
	flann/1.9.1
	freeimage/3.18.0
	freetype/2.11.1
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
	libpq/14.2
	libraw/0.20.2
	libtiff/4.3.0
	libwebp/1.2.2
	lz4/1.9.3
	openexr/2.5.7
	opengl/system
	openjpeg/2.4.0
	openssl/1.1.1n
	pcre2/10.39
	qt/5.15.2
	sqlite3/3.38.1
	xz_utils/5.2.5
	zlib/1.2.12
	zstd/1.5.2

## Build Colmap

Conan package for colmap library 3.6 or 3.7

- Debug version :

		conan create . 3.6@ -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True -s compiler.version=16 -s ceres-solver:build_type=Release

- Release version :

		conan create . 3.6@ -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Release --build=missing -o shared=True -s compiler.version=16


# TODO Investigations

- QT : use for GUI in colmap. If GUI is disabled then build issue => GUI is enabled !
- Opengl : colmap cmakelist remove opengl if colmap GUI is disabled, but there are opengl source dependencies in Colmap sources => keep Opengl
  