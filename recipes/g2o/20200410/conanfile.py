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
               "opengl": [True,False],
               "apps":[True,False],
               "examples":[True,False]			   
			  }
    default_options = {"shared": True,
	                   "csparse": True,
                       "opengl": False,
                       "apps":False,
                       "examples":False}
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
        self.requires("common/1.0.2@conan-solar/stable")

    def source(self):
        tools.get("https://github.com/RainerKuemmerle/g2o/archive/{0}_git.tar.gz".format(self.version))
        os.rename("g2o-" + self.version + "_git", self.source_subfolder)

    @property
    def _android_arch(self):
        arch = str(self.settings.arch)
        return tools.to_android_abi(arch)
		
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

        cmake.definitions["BUILD_LGPL_SHARED_LIBS"] = False
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["G2O_USE_OPENGL"] = self.options.opengl
        cmake.definitions["G2O_USE_CSPARSE"] = self.options.csparse
        cmake.definitions["BUILD_CSPARSE"] = self.options.csparse
        cmake.definitions["G2O_BUILD_APPS"] = self.options.apps
        cmake.definitions["G2O_BUILD_EXAMPLES"] = self.options.examples

        if not tools.os_info.is_windows:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = True

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
		
        if self.settings.os == 'Android':
            if not self.options.shared:
                self.cpp_info.includedirs.append(
                    os.path.join('sdk', 'native', 'jni', 'include'))
                self.cpp_info.libdirs.append(
                    os.path.join('sdk', 'native', 'staticlibs', self._android_arch))
