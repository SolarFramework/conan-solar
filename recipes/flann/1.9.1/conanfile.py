from conans import ConanFile, CMake, tools
import os


class LibFlannConan(ConanFile):
    name = "flann"
    upstream_version = "1.9.1"
    version = "{0}".format(upstream_version)

    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    exports = [
        "patches/flann_cmake_311.diff",
        "patches/c++17_support.diff",
        "patches/FindFLANN.cmake"
    ]
    url = "https://git.ircad.fr/conan/conan-flann"
    license = "BSD License"
    description = "Fast Library for Approximate Nearest Neighbors."
    source_subfolder = "source_subfolder"
    short_paths = True

    def requirements(self):
        self.requires("common/1.0.2@conan-solar/stable")

    def source(self):
        tools.get("https://github.com/mariusmuja/flann/archive/{0}.tar.gz".format(self.upstream_version))
        os.rename("flann-" + self.upstream_version, self.source_subfolder)

    def build(self):
        flann_source_dir = os.path.join(self.source_folder, self.source_subfolder)
        tools.patch(flann_source_dir, "patches/flann_cmake_311.diff")
        tools.patch(flann_source_dir, "patches/c++17_support.diff")

        # Import common flags and defines
        import common

        # Generate Cmake wrapper
        common.generate_cmake_wrapper(
            cmakelists_path='CMakeLists.txt',
            source_subfolder=self.source_subfolder,
            build_type=self.settings.build_type
        )

        cmake = CMake(self)

        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_DOC"] = "OFF"
        cmake.definitions["BUILD_TESTS"] = "OFF"
        cmake.definitions["BUILD_C_BINDINGS"] = "OFF"
        cmake.definitions["BUILD_MATLAB_BINDINGS"] = "OFF"
        cmake.definitions["BUILD_PYTHON_BINDINGS"] = "OFF"
        if not tools.os_info.is_windows:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON"

        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("patches/FindFLANN.cmake", src=".", dst=".", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
