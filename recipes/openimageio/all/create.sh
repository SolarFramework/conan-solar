conan v1
----------
conan create . openimageio/2.4.7.1@conan-solar/1_1_0 --build=missing -tf None -o with_ffmpeg=False -o with_freetype=False -o with_giflib=False -o with_hdf5=False -o with_libheif=False -o with_libwebp=False -o with_opencolorio=False -o with_opencv=False -o with_ptex=False -o with_openjpeg=False
conan create . openimageio/2.4.7.1@conan-solar/1_1_0 --build=missing -tf None -o with_ffmpeg=False -o with_freetype=False -o with_giflib=False -o with_hdf5=False -o with_libheif=False -o with_libwebp=False -o with_opencolorio=False -o with_opencv=False -o with_ptex=False -o with_openjpeg=False -s build_type=Debug

conan v2
----------
conan create . --version 2.4.7.1 --user conan-solar --channel 1_1_0 --build=missing -tf "" -o boost/*:shared=True -o boost/*:zlib=False -o boost/*:bzip2=False -o with_ffmpeg=False -o with_freetype=False -o with_giflib=False -o with_hdf5=False -o with_libheif=False -o with_libwebp=False -o with_opencolorio=False -o with_opencv=False -o with_ptex=False -o with_tools=False
conan create . --version 2.4.7.1 --user conan-solar --channel 1_1_0 --build=missing -tf "" -o boost/*:shared=True -o boost/*:zlib=False -o boost/*:bzip2=False -o with_ffmpeg=False -o with_freetype=False -o with_giflib=False -o with_hdf5=False -o with_libheif=False -o with_libwebp=False -o with_opencolorio=False -o with_opencv=False -o with_ptex=False -o with_tools=False -s build_type=Debug