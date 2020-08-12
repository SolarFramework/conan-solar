@echo on
conan create . conan-solar/stable -tf None 
conan create . conan-solar/stable -tf None -s build_type=Debug
conan create . conan-solar/stable -tf None -o contrib=True -o nonfree=True -o harfbuzz=False
conan create . conan-solar/stable -tf None -s build_type=Debug -o contrib=True -o nonfree=True -o harfbuzz=False


