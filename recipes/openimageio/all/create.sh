conan create . openimageio/2.3.13.0@conan-solar/boost_1_76 --build=missing -tf None -o boost:shared=True -o boost:zlib=False -o boost:bzip2=False -o with_ffmpeg=False -o with_freetype=False -o with_giflib=False -o with_hdf5=False -o with_libheif=False -o with_libwebp=False -o with_opencolorio=False -o with_opencv=False -o with_ptex=False -o with_tools=False
conan create . openimageio/2.3.13.0@conan-solar/boost_1_76 --build=missing -tf None -o boost:shared=True -o boost:zlib=False -o boost:bzip2=False -o with_ffmpeg=False -o with_freetype=False -o with_giflib=False -o with_hdf5=False -o with_libheif=False -o with_libwebp=False -o with_opencolorio=False -o with_opencv=False -o with_ptex=False  -o with_tools=False -s build_type=Debug 