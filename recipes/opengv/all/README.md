# conan opengv

conan create all master@ -tf None -s compiler.cppstd=17 -s build_type=Debug --build=missing
conan create all master@ -tf None -s compiler.cppstd=17 -s build_type=Release --build=missing