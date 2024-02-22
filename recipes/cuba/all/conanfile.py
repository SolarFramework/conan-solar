from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, export_conandata_patches, get, copy, replace_in_file 
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os
import textwrap


required_conan_version = ">=1.54.0"

class CubaConan(ConanFile):
    name = "cuba"
    license = "Apache v2 license"
    homepage = "https://github.com/fixstars/cuda-bundle-adjustment"
    description = "This project implements a Bundle Adjustment algorithm with CUDA. It optimizes camera poses and landmarks (3D points) represented by a graph."
    package_type = "library"
    topics = ("optimization", "non-linear least squares")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "float32": [True, False],
        "cuda_arch_bin": [None, "ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "float32": False,
        "cuda_arch_bin": "Auto",
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
        self.requires("eigen/3.4.0", transitive_headers=True)

    def validate(self):
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Visual Studio with static runtime is not supported for shared library.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)
        
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"), "EIGEN3_INCLUDE_DIR", "Eigen3_INCLUDE_DIR")

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["WITH_G2O"] = 'OFF'
        tc.variables["ENABLE_SAMPLES"] = 'OFF'
        tc.variables["USE_FLOAT32"] = self.options.float32
        
        tc.variables["CUDA_NVCC_FLAGS"] = "--expt-relaxed-constexpr"

        if self.options.cuda_arch_bin:
            tc.variables["CUDA_ARCH"] = self.options.cuda_arch_bin

        if is_msvc(self):
            # set runtimes.
            if is_msvc_static_runtime(self):
                self.output.info("static runtime, cuba build will use flag /MT (or /MTd in debug mode)")
                tc.variables["CUDA_NVCC_RELEASE"] = "/MT;-O3"
                tc.variables["CUDA_NVCC_DEBUG"] = "/MTd;-O0; -G"
                tc.variables["CUDA_NVCC_MINSIZEREL"] = "/MT; -Os"
                tc.variables["CUDA_NVCC_RELWITHDEBINFO"] = "/MT;-O2;-G"
                tc.variables["CMAKE_CXX_FLAGS_RELEASE"] = "/MT"
                tc.variables["CMAKE_CXX_FLAGS_DEBUG"] = "/MTd"
                tc.variables["CMAKE_CXX_FLAGS_MINSIZEREL"] = "/MT"
                tc.variables["CMAKE_CXX_FLAGS_RELWITHDEBINFO"] = "/MT"
            else:
                self.output.info("dynamic runtime, cuba build will use flag /MD (or /MDd in debug mode)")
                tc.variables["CUDA_NVCC_RELEASE"] = "/MD;-O3"
                tc.variables["CUDA_NVCC_DEBUG"] = "/MDd;-O0; -G"
                tc.variables["CUDA_NVCC_MINSIZEREL"] = "/MD; -Os"
                tc.variables["CUDA_NVCC_RELWITHDEBINFO"] = "/MD;-O2;-G"
                tc.variables["CMAKE_CXX_FLAGS_RELEASE"] = "/MD"
                tc.variables["CMAKE_CXX_FLAGS_DEBUG"] = "/MDd"
                tc.variables["CMAKE_CXX_FLAGS_MINSIZEREL"] = "/MD"
                tc.variables["CMAKE_CXX_FLAGS_RELWITHDEBINFO"] = "/MD"
        elif self.options.fPIC:
            tc.variables["CUDA_NVCC_FLAGS"] += " --compiler-options -fPIC"
        
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
