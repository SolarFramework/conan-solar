from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, export_conandata_patches, get, copy 
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.54.0"

class open3dConan(ConanFile):
    name = "open3d"
    homepage = "https://github.com/isl-org/Open3D"
    license = "MIT"
    description = "Open3D is an open-source library that supports rapid development of software that deals with 3D data."
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_cuda": [True,False],
     }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_cuda": False,
    }
    
    short_paths = True

    @property
    def _android_arch(self):
        arch = str(self.settings.arch)
        return tools.to_android_abi(arch)

    def export_sources(self):
        export_conandata_patches(self)
        
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Visual Studio with static runtime is not supported for shared library.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version][0],
            destination=self.source_folder, strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)
        
    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_PYHTON_MODULE"] = False
        tc.variables["BUILD_GUI"] = False
        tc.variables["BUILD_ISPC_MODULE"] = False
        tc.variables["BUILD_WEBRTC"] = False
        tc.variables["GLIBCXX_USE_CXX11_ABI"] = False
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        tc.variables["CMAKE_DEBUG_POSTFIX"] = ""
        
        if (self.options.with_cuda):
            tc.variables["BUILD_CUDA_MODULE"] = True
        
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        
        # Fix all hard coded path to conan package in all .cmake files
        # common.fix_conan_path(self, self.package_folder, '*.cmake')
        if self.settings.os == 'Android':
            if not self.options.shared:
                self.cpp_info.includedirs.append(
                    os.path.join('sdk', 'native', 'jni', 'include'))
                self.cpp_info.libdirs.append(
                    os.path.join('sdk', 'native', 'staticlibs', self._android_arch))
