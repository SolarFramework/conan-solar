from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os
from shutil import copy, copyfile

required_conan_version = ">=1.29.1"

import os
import subprocess
from shutil import copy, copyfile

required_conan_version = ">=1.29.1"

class OpengvConan(ConanFile):
    
    name = "opengv"
    license = "MPLv2 license"
    homepage = "https://laurentkneip.github.io/opengv/"
    description = "OpenGV library"
    url = "https://github.com/Solar-Framework/conan-solar"
    topics = ("computer-vision", "image-processing")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["CMakeLists.txt"]
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    generators = "cmake", "cmake_find_package"
    short_paths = True

    def requirements(self):
        for req in self.conan_data["requirements"]:
            self.requires(req)
        
    def source(self):
        subprocess.check_call(["git", "clone", self.conan_data["sources"][self.version]["git"], self._source_subfolder])
        os.chdir(self._source_subfolder)
        subprocess.check_call(["git", "checkout", self.version])

    def build(self):

        cmake = CMake(self)
        cmake.definitions["BUILD_TESTS"] = "OFF"
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build()
        cmake.install()

    def package_info(self):
    
        self.cpp_info.names["cmake_find_package"] = "opengv"
        self.cpp_info.names["cmake_find_package_multi"] = "opengv"
        self.cpp_info.includedirs = [os.path.join(self.package_folder,"include")]
        self.cpp_info.libdirs = [os.path.join(self.package_folder,"lib")]

        self.cpp_info.libs = tools.collect_libs(self)
