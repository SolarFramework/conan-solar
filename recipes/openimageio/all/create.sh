conan create . --version 2.4.7.1 --user conan-solar --channel 1_1_0 --build=missing -tf "" -o with_ffmpeg=False -o with_freetype=False -o with_giflib=False -o with_hdf5=False -o with_libheif=False -o with_libwebp=False -o with_opencolorio=False -o with_opencv=False -o with_ptex=False
conan create . --version 2.4.7.1 --user conan-solar --channel 1_1_0 --build=missing -tf "" -o with_ffmpeg=False -o with_freetype=False -o with_giflib=False -o with_hdf5=False -o with_libheif=False -o with_libwebp=False -o with_opencolorio=False -o with_opencv=False -o with_ptex=False -s build_type=Debug

