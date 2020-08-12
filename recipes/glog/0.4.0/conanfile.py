from conans import ConanFile, CMake, tools
import os


class LibGlogConan(ConanFile):
    name = "glog"
    package_revision = ""
    upstream_version = "0.4.0"
    version = "{0}{1}".format(upstream_version, package_revision)

    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    url = "https://github.com/Solar-Framework/conan-solar/recipes/glog/0.4.0"
    license = "BSD 3-Clause"
    description = "C++ implementation of the Google logging module."
    source_subfolder = "source_subfolder"
    short_paths = True

    def requirements(self):
        self.requires("common/1.0.2@conan-solar/stable")

    def source(self):
        tools.get("https://github.com/google/glog/archive/v{0}.tar.gz".format(self.upstream_version))
        os.rename("glog-" + self.upstream_version, self.source_subfolder)

    def build(self):
        # Import common flags and defines
        import common

        # Generate Cmake wrapper
        common.generate_cmake_wrapper(
            cmakelists_path='CMakeLists.txt',
            source_subfolder=self.source_subfolder,
            build_type=self.settings.build_type
        )

        cmake = CMake(self)

        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.definitions["WITH_GFLAGS"] = "OFF"
        if not tools.os_info.is_windows:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON"

        cmake.configure()
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
