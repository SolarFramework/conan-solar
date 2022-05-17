# Pre requeries
- Install git

# conan aliceVision

cd c:\Users\aschadle\Documents\dev\recipe\alicevision
conan create all v2.4.0@ -tf None -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True -o with_cuda=False -o boost:shared=True

# ligne de commande
conan create all v2.4.0@ -tf None -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True -o with_cuda=False -o boost:shared=True -o flann:shared=False -o ceres-solver:shared=True -o geogram:shared=True -o openimageio:shared=True -o popsift:shared=True
