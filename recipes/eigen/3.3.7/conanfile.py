from conans import ConanFile, CMake, tools
import os
from glob import glob


class LibEigenConan(ConanFile):
    name = "eigen"
    package_revision = ""
    upstream_version = "3.3.7"
    version = "{0}{1}".format(upstream_version, package_revision)

    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    exports = [
        "patches/CMakeLists_disable_test.diff"
    ]
    url = "https://github.com/Solar-Framework/conan-solar/recipes/eigen/3.3.7"
    license = "http://eigen.tuxfamily.org"
    description = "Eigen is a C++ template library for linear algebra"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    short_paths = True

    def requirements(self):
        self.requires("common/1.0.2@conan-solar/stable")

    def source(self):
        tools.get("https://gitlab.com/libeigen/eigen/-/archive/{0}/eigen-{0}.tar.gz".format(self.upstream_version))
        os.rename(glob("eigen-*")[0], self.source_subfolder)

    @property
    def _android_arch(self):
        arch = str(self.settings.arch)
        return tools.to_android_abi(arch)

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
        cmake.verbose = True

        cmake.definitions["EIGEN_TEST_NOQT"] = "ON"
        cmake.definitions["BUILD_TESTING"] = "OFF"
        if not tools.os_info.is_windows:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON"

        cmake.configure(build_folder=self.build_subfolder)
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append('include/eigen3')
		if self.settings.os == 'Android':
            if not self.options.shared:
                self.cpp_info.includedirs.append(
                    os.path.join('sdk', 'native', 'jni', 'include'))
                self.cpp_info.libdirs.append(
                    os.path.join('sdk', 'native', 'staticlibs', self._android_arch))
