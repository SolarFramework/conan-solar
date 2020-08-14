from conans import ConanFile, tools, CMake
import os


class ZlibConan(ConanFile):
    name = "zlib"
    upstream_version = "1.2.11"
    package_revision = ""
    version = "{0}{1}".format(upstream_version, package_revision)

    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    url = "https://github.com/Solar-Framework/conan-solar/recipes/zlib/1.2.11"
    license = "http://www.zlib.net/zlib_license.html"
    description = "A massively spiffy yet delicately unobtrusive compression library"
    source_subfolder = "source_subfolder"
    short_paths = True

    def configure(self):
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("common/1.0.2@conan-solar/stable")

    def source(self):
        tools.get("https://zlib.net/zlib-{0}.tar.gz".format(self.upstream_version))
        os.rename("zlib-{0}".format(self.upstream_version), self.source_subfolder)

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

        if not tools.os_info.is_windows:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON"

        cmake.configure()
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
