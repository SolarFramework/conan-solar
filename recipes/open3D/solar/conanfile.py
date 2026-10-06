import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import Environment
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir

required_conan_version = ">=2.0"


class Open3DConan(ConanFile):
    name = "open3d"
    license = "MIT"
    homepage = "https://www.open3d.org"
    url = "https://github.com/Solar-Framework/conan-solar/recipes/open3d"
    description = "Open3D: A Modern Library for 3D Data Processing"
    topics = ("3d", "point-cloud", "mesh", "reconstruction", "visualization", "cuda")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_cuda": [True, False],
        "cuda_arch": [None, "ANY"],
        "cuda_static_runtime": [True, False],
        "with_gui": [True, False],
        "with_openmp": [True, False],
        "with_ispc": [True, False],
        "with_ipp": [True, False],
        "with_realsense": [True, False],
        "with_azure_kinect": [True, False],
        "with_webrtc": [True, False],
        "headless_rendering": [True, False],
        "use_system_eigen": [True, False],
        "use_system_fmt": [True, False],
        "use_system_tbb": [True, False],
        "blas": ["mkl", "openblas_system", "openblas_source"],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_cuda": False,
        "cuda_arch": "all-major",
        "cuda_static_runtime": True,
        "with_gui": False,
        "with_openmp": True,
        "with_ispc": True,
        "with_ipp": True,
        "with_realsense": False,
        "with_azure_kinect": False,
        "with_webrtc": False,
        "headless_rendering": False,
        "use_system_eigen": True,
        "use_system_fmt": False,
        "use_system_tbb": False,
        "blas": "mkl",
    }

    short_paths = True

    @property
    def _min_cppstd(self):
        return 17

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.headless_rendering

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.with_cuda:
            del self.options.cuda_arch
            del self.options.cuda_static_runtime

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Eigen is in Open3D's public headers: same version as SolARFramework
        if self.options.use_system_eigen:
            self.requires("eigen/3.4.0", transitive_headers=True)

        # public headers include fmt: pinned to the fmt of SolARFramework's spdlog (update together)
        self.requires("fmt/12.1.0", transitive_headers=True)

        if self.options.use_system_tbb:
            self.requires("onetbb/2021.12.0")

        if self.settings.os == "Linux" and not self.options.headless_rendering:
            # libGL for the legacy Visualizer
            self.requires("opengl/system")

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)

        if self.options.with_gui:
            # prebuilt Filament requires libc++
            raise ConanInvalidConfiguration(
                "open3d:with_gui=True is not supported: the prebuilt Filament shipped with Open3D "
                "requires libc++ and cannot be linked against libstdc++. Use the legacy Visualizer "
                "(open3d::visualization::Visualizer) instead."
            )

        if self.options.with_cuda and self.settings.os == "Macos":
            raise ConanInvalidConfiguration("CUDA is not available on macOS.")

        if self.options.blas == "mkl" and self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration(
                "open3d:blas=mkl is only available on x86_64. Use blas=openblas_source "
                "(needs gfortran) or blas=openblas_system on this architecture."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.cache_variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.cache_variables["DEVELOPER_BUILD"] = False
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_UNIT_TESTS"] = False
        tc.cache_variables["BUILD_BENCHMARKS"] = False
        tc.cache_variables["BUILD_PYTHON_MODULE"] = False
        tc.cache_variables["BUILD_JUPYTER_EXTENSION"] = False
        tc.cache_variables["BUILD_TENSORFLOW_OPS"] = False
        tc.cache_variables["BUILD_PYTORCH_OPS"] = False

        tc.cache_variables["BUILD_GUI"] = bool(self.options.with_gui)
        tc.cache_variables["BUILD_WEBRTC"] = bool(self.options.with_webrtc)
        tc.cache_variables["BUILD_LIBREALSENSE"] = bool(self.options.with_realsense)
        tc.cache_variables["BUILD_AZURE_KINECT"] = bool(self.options.with_azure_kinect)
        tc.cache_variables["BUILD_ISPC_MODULE"] = bool(self.options.with_ispc)

        tc.cache_variables["WITH_OPENMP"] = bool(self.options.with_openmp)
        tc.cache_variables["WITH_IPP"] = bool(self.options.with_ipp)
        tc.cache_variables["WITH_MINIZIP"] = False

        if self.settings.os == "Linux":
            tc.cache_variables["ENABLE_HEADLESS_RENDERING"] = bool(self.options.headless_rendering)

        tc.cache_variables["USE_SYSTEM_EIGEN3"] = bool(self.options.use_system_eigen)
        tc.cache_variables["USE_SYSTEM_FMT"] = bool(self.options.use_system_fmt)
        tc.cache_variables["USE_SYSTEM_TBB"] = bool(self.options.use_system_tbb)

        # USE_SYSTEM_BLAS is only used when USE_BLAS is ON (otherwise MKL is linked statically)
        tc.cache_variables["USE_BLAS"] = self.options.blas != "mkl"
        tc.cache_variables["USE_SYSTEM_BLAS"] = self.options.blas == "openblas_system"

        tc.cache_variables["BUILD_CUDA_MODULE"] = bool(self.options.with_cuda)
        if self.options.with_cuda:
            # accept commas: remaken does not quote option values
            tc.cache_variables["CMAKE_CUDA_ARCHITECTURES"] = str(self.options.cuda_arch).replace(",", ";")
            # static CUDA runtime: consumers only need the driver
            tc.cache_variables["BUILD_WITH_CUDA_STATIC"] = bool(self.options.cuda_static_runtime)
            tc.cache_variables["BUILD_COMMON_CUDA_ARCHS"] = False

        # must match the SolAR stack ABI
        if self.settings.get_safe("compiler.libcxx") == "libstdc++":
            tc.cache_variables["GLIBCXX_USE_CXX11_ABI"] = False
        elif self.settings.get_safe("compiler.libcxx") == "libstdc++11":
            tc.cache_variables["GLIBCXX_USE_CXX11_ABI"] = True

        # CMake >= 4 rejects the old minimum versions of vendored dependencies (env var for sub-projects)
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"

        tc.generate()

        env = Environment()
        env.define("CMAKE_POLICY_VERSION_MINIMUM", "3.5")
        env.vars(self, scope="build").save_script("open3d_cmake_policy")

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        # expose GL/GLFW headers only, not the vendored Eigen/fmt
        third_party_include = os.path.join(self.package_folder, "include", "open3d", "3rdparty")
        for header_dir in ("GL", "GLFW"):
            copy(self, "*",
                 src=os.path.join(third_party_include, header_dir),
                 dst=os.path.join(self.package_folder, "glheaders", header_dir))

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Open3D")
        self.cpp_info.set_property("cmake_target_name", "Open3D::Open3D")
        self.cpp_info.set_property("pkg_config_name", "Open3D")

        self.cpp_info.libs = ["Open3D"]
        if not self.options.use_system_tbb:
            # vendored TBB installed next to libOpen3D
            self.cpp_info.libs.append("tbb_debug" if self.settings.build_type == "Debug" else "tbb")

        self.cpp_info.includedirs = ["include", "glheaders"]

        # consumers must use the same ABI
        libcxx = self.settings.get_safe("compiler.libcxx")
        if libcxx in ("libstdc++", "libstdc++11"):
            self.cpp_info.defines.append(
                "_GLIBCXX_USE_CXX11_ABI={}".format(0 if libcxx == "libstdc++" else 1))

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "pthread", "m"])
            if self.options.with_openmp:
                self.cpp_info.system_libs.append("gomp")
                self.cpp_info.cxxflags.append("-fopenmp")
                self.cpp_info.sharedlinkflags.append("-fopenmp")
                self.cpp_info.exelinkflags.append("-fopenmp")
            if self.options.blas == "openblas_system":
                self.cpp_info.system_libs.extend(["lapacke", "lapack", "blas"])
