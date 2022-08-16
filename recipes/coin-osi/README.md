# Pre requeries
- Install git

#Info:
recipe based on Conan-center recipe - commit 0eaf089b1d75989ad4048bc53798569030e39bdd - 07/08/2022
build changed from autotools to CMake with https://github.com/coin-or/Osi/pull/128
then conan recipe updated 

recipe has been patched for disable bind2nd (removed in cpp-std 17)

# use
conan create all 0.108.6@ -tf None -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=False

# TODO

only tested on windows, TODO Linux