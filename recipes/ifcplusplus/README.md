# Recette Conan — IfcPlusPlus 2.5

## Structure

```
ifcplusplus-conan/
├── conanfile.py               # Recette principale
└── test_package/
    ├── conanfile.py           # Test du package
    ├── CMakeLists.txt
    └── test_package.cpp
```

## Prerequis

- Conan 2.x (`pip install conan`)
- CMake >= 3.15
- Compilateur C++17 (GCC 9+, Clang 10+, MSVC 2019+)

## Build & install dans le cache Conan

```bash
# Build Release (defaut)
conan create . --build=missing

# Build Debug
conan create . --build=missing -s build_type=Debug

# Build en shared lib
conan create . --build=missing -o ifcplusplus/*:shared=True
```

## Utiliser dans un projet consumer

### conanfile.txt

```ini
[requires]
ifcplusplus/2.5

[generators]
CMakeDeps
CMakeToolchain
```

```bash
mkdir build && cd build
conan install .. --build=missing
cmake .. -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake
cmake --build .
```

### CMakeLists.txt du projet

```cmake
find_package(ifcplusplus REQUIRED CONFIG)
target_link_libraries(mon_exe PRIVATE IfcPlusPlus::IfcPlusPlus)
```

## Dependances

| Composant       | Dependance         | Note                          |
|-----------------|--------------------|-------------------------------|
| Lib core        | Aucune             | Header-only + sources internes|
| Lecteur parallel| pthreads (Linux)   | Gere via system_libs          |
| Viewer          | Qt 5 + OSG         | Desactive (BUILD_VIEWER_APPLICATION=OFF) |
