from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, export_conandata_patches, get, copy 
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.54.0"

class g2oConan(ConanFile):
    name = "g2o"
    homepage = "https://github.com/RainerKuemmerle/g2o"
    license = "BSD"
    description = "g2o is an open-source C++ framework for optimizing graph-based nonlinear error functions."
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "csparse": [True,False],
        "opengl": [True,False],
        "apps":[True,False],
        "examples":[True,False],
        "openmp":[True, False]
     }
    default_options = {
        "shared": False,
        "fPIC": True,
        "csparse": False,
        "opengl": False,
        "apps":False,
        "examples":False,
        "openmp":False
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

    def requirements(self):
        self.requires("eigen/3.4.0@")

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
        tc.variables["BUILD_LGPL_SHARED_LIBS"] = False
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["G2O_USE_OPENGL"] = self.options.opengl
        tc.variables["G2O_USE_CSPARSE"] = self.options.csparse
        tc.variables["BUILD_CSPARSE"] = self.options.csparse
        tc.variables["G2O_BUILD_APPS"] = self.options.apps
        tc.variables["G2O_BUILD_EXAMPLES"] = self.options.examples
        tc.variables["G2O_USE_OPENMP"] = self.options.openmp
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        tc.variables["CMAKE_DEBUG_POSTFIX"] = ""
        
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        # add pre-compiled definition to use Ceres provided in g2o/EXTERNAL/ceres
        self.cpp_info.defines = ["G2O_USE_VENDORED_CERES=1"]

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
