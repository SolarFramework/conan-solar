import os
from conans import ConanFile, CMake, tools


class Libg2oConan(ConanFile):
    name = "g2o"
    upstream_version = "20200410"
    package_revision = ""
    version = "{0}{1}".format(upstream_version, package_revision)

    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "csparse": [True,False],
               "opengl": [True,False]			   
			  }
    default_options = {"shared": True,
	                   "csparse": True,
                       "opengl": False}
    exports = [
    ]
    url = "https://github.com/Solar-Framework/conan-solar/recipes/g2o/20200410"
    homepage = "https://github.com/RainerKuemmerle/g2o/"
    license = "BSD license (lGPL3+ with csparse_extension, GPL3+ with viewer, incremental and slam2d_g2o extension)"
    description = ("g2o is an open-source C++ framework for optimizing graph-based nonlinear error functions.")
    source_subfolder = "source_subfolder"
    short_paths = True

    def requirements(self):
        self.requires("eigen/3.3.7@conan-solar/stable")
        if self.options.csparse:
            self.requires("cxsparse/3.1.1@conan-solar/stable")
        self.requires("common/1.0.2@conan-solar/stable")

    def source(self):
        tools.get("https://github.com/RainerKuemmerle/g2o/archive/{0}_git.tar.gz".format(self.upstream_version))
        os.rename("g2o-" + self.upstream_version + "_git", self.source_subfolder)

    def build(self):
        g2o_source_dir = os.path.join(self.source_folder, self.source_subfolder)

        # Import common flags and defines
        import common

        # Generate Cmake wrapper
        common.generate_cmake_wrapper(
            cmakelists_path='CMakeLists.txt',
            source_subfolder=self.source_subfolder,
            build_type=self.settings.build_type
        )

        cmake = CMake(self)

        cmake.definitions["G20_BUILD_APPS"] = "OFF"
        cmake.definitions["G20_BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["G2O_USE_OPENGL"] = "OFF"
        cmake.definitions["G2O_USE_CSPARSE"] = "OFF"
        cmake.definitions["BUILD_CSPARSE"] = "OFF"
        cmake.definitions["BUILD_LGPL_SHARED_LIBS"] = "OFF"
        cmake.definitions["BUILD_SHARED_LIBS"] = "OFF"

        if self.options.opengl:
            cmake.definitions["G2O_USE_OPENGL"] = "ON"
			
        if self.options.csparse:
            cmake.definitions["G2O_USE_CPSARSE"] = "ON"
            cmake.definitions["BUILD_CSPARSE"] = "ON"

        if not tools.os_info.is_windows:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON"

        cmake.configure()
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

    def package(self):
        # Retrieve common helpers
        import common

        # Fix all hard coded path to conan package in all .cmake files
        common.fix_conan_path(self, self.package_folder, '*.cmake')