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
        "with_cuda": [True, False],
        "with_gui": [True, False],
        "with_python_module": [True, False],
        "with_ispc_module": [True, False],
        "with_webrtc": [True, False],
        "with_examples": [True, False],
        "with_unit_tests": [True, False],
        "with_benchmarks": [True, False],
        "with_jupyter_extension": [True, False],
        "with_tensorflow_ops": [True, False],
        "with_pytorch_ops": [True, False],
        "with_open3d_ml": [True, False],
        "with_librealsense": [True, False],
        "with_azure_kinect": [True, False],
     }
    default_options = {
        "shared": False,
        "fPIC": False,
        "with_cuda": False,
        "with_gui": False,
        "with_python_module": False,
        "with_ispc_module": False,
        "with_webrtc": False,
        "with_examples": False,
        "with_unit_tests": False,
        "with_benchmarks": False,
        "with_jupyter_extension": False,
        "with_tensorflow_ops": False,
        "with_pytorch_ops": False,
        "with_open3d_ml": False,
        "with_librealsense": False,
        "with_azure_kinect": False,
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
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
        
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        #tc.cache_variables["GLIBCXX_USE_CXX11_ABI"] = False
        #tc.cache_variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        #tc.cache_variables["CMAKE_DEBUG_POSTFIX"] = ""
        
        tc.cache_variables["STATIC_WINDOWS_RUNTIME"] = is_msvc_static_runtime(self)
        
        tc.cache_variables["BUILD_GUI"] = self.options.with_gui
        tc.cache_variables["BUILD_PYTHON_MODULE"] = self.options.with_python_module
        tc.cache_variables["BUILD_ISPC_MODULE"] = self.options.with_ispc_module
        tc.cache_variables["BUILD_WEBRTC"] = self.options.with_webrtc
        tc.cache_variables["BUILD_EXAMPLES"] = self.options.with_examples
        tc.cache_variables["BUILD_UNIT_TESTS"] = self.options.with_unit_tests
        tc.cache_variables["BUILD_BENCHMARKS"] = self.options.with_benchmarks
        tc.cache_variables["BUILD_JUPYTER_EXTENSION"] = self.options.with_jupyter_extension
        tc.cache_variables["BUILD_TENSORFLOW_OPS"] = self.options.with_tensorflow_ops
        tc.cache_variables["BUILD_PYTORCH_OPS"] = self.options.with_pytorch_ops
        tc.cache_variables["BUNDLE_OPEN3D_ML"] = self.options.with_open3d_ml
        tc.cache_variables["BUILD_LIBREALSENSE"] = self.options.with_librealsense
        tc.cache_variables["BUILD_AZURE_KINECT"] = self.options.with_azure_kinect
        
        if self.options.with_cuda:
            tc.cache_variables["BUILD_CUDA_MODULE"] = True
        else:
            tc.cache_variables["BUILD_CUDA_MODULE"] = False
        
        tc.generate()
    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        
        if not self.options.shared:
            self.cpp_info.defines.append("OPEN3D_STATIC")        
       
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