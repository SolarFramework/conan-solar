from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, rename, replace_in_file, rmdir, save
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os
import re
import textwrap

required_conan_version = ">=1.54.0"


class PopsiftConan(ConanFile):
    name = "popsift"
    license = "MPL v2 license"
    homepage = "https://github.com/alicevision/popsift/"
    description = "open-source implementation of the SIFT algorithm in CUDA"
    url = "https://github.com/Solar-Framework/conan-solar/recipes/popsift/1.0.0"
    topics = ("computer-vision", "image-processing")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
#    generators = "cmake", "cmake_find_package"
#    _cmake = None

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

#   def configure(self):
        # it is also necessary to remove the VS runtime
#        if self.settings.compiler == "Visual Studio":
#            del self.settings.compiler.runtime
            
    def validate(self):
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Visual Studio with static runtime is not supported for shared library.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    @property
    def _android_arch(self):
        arch = str(self.settings.arch)
        return tools.to_android_abi(arch)

    def _patch_sources(self):
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared

        tc.variables["PopSift_BUILD_EXAMPLES"] = 'OFF'
        
        if is_msvc(self):
            tc.variables["BUILD_WITH_STATIC_CRT"] = is_msvc_static_runtime(self)
        
        tc.generate()

        CMakeDeps(self).generate()
        
    def build(self):
        self._patch_sources()

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

    def package(self):
        # Retrieve common helpers
# import common

        # Fix all hard coded path to conan package in all .cmake files
#        common.fix_conan_path(self, self.package_folder, '*.cmake')
        cmake = CMake(self)
        cmake.install()
        if self.settings.os == 'Android':
            if not self.options.shared:
                self.cpp_info.includedirs.append(
                    os.path.join('sdk', 'native', 'jni', 'include'))
                self.cpp_info.libdirs.append(
                    os.path.join('sdk', 'native', 'staticlibs', self._android_arch))


