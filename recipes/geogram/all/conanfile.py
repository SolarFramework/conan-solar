from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os
from shutil import copy, copyfile

required_conan_version = ">=1.29.1"

class GeogramConan(ConanFile):
    name = "geogram"
    version = "1.7.7"
    license = "MPLv2 license"
    homepage = "https://github.com/alicevision/geogram"
    description = ""
    url = "https://github.com/Solar-Framework/conan-solar"
    topics = ("computer-vision", "image-processing")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]#,
    }
               #"with_cuda": [True, False],
               #"with_openmp": [True, False],
               #"with_opengl": [True, False],
               #"with_profiling": [True, False],
               #"with_test": [True, False]}
    default_options = {"shared": False#,
    }
                       #"with_cuda": True,
                       #"with_openmp": True,
                       #"with_opengl": True,
                       #"with_profiling": True, #colmap binary needs -lprofiler -ltcmalloc on linux
                       #"with_test": False}
    exports_sources = ["CMakeLists.txt", "patches/*"]
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    generators = "cmake", "cmake_find_package"
    short_paths = True

    #def requirements(self):
    
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("geogram-{}".format(self.version), self._source_subfolder)

    @property
    def _android_arch(self):
        arch = str(self.settings.arch)
        return tools.to_android_abi(arch)

    def build(self):

        cmake = CMake(self)
        cmake.definitions["VORPALINE_BUILD_DYNAMIC"] = "ON" if self.options.shared else "OFF"
        cmake.definitions["GEOGRAM_LIB_ONLY"] = "ON"

        if not tools.os_info.is_windows:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = True
            cmake.definitions["VORPALINE_PLATFORM"] = "Linux64-gcc"
        
        if tools.os_info.is_windows:
            cmake.definitions["VORPALINE_PLATFORM"] = "Win64-vs2015"

        cmake.configure(build_folder=self._build_subfolder)
        cmake.build()
        cmake.install()

    def package_info(self):

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        self.cpp_info.names["cmake_find_package"] = "geogram"
        self.cpp_info.names["cmake_find_package_multi"] = "geogram"
        self.cpp_info.includedirs = [os.path.join(self.package_folder,"include","geogram1"),
                                     os.path.join(self.package_folder,"include","GLFW")]
        self.cpp_info.libdirs = [os.path.join(self.package_folder,"lib")]
        self.cpp_info.libs = tools.collect_libs(self)

    def package(self):

        if self.settings.os == 'Android':
            if not self.options.shared:
                self.cpp_info.includedirs.append(
                    os.path.join('sdk', 'native', 'jni', 'include'))
                self.cpp_info.libdirs.append(
                    os.path.join('sdk', 'native', 'staticlibs', self._android_arch))


