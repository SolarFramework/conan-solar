import os
import shutil
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.54.0"


class CeressolverConan(ConanFile):
    name = "ceres-solver"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://ceres-solver.org/"
    description = (
        "Ceres Solver is an open source C++ library for modeling "
        "and solving large, complicated optimization problems"
    )
    topics = ("optimization", "non-linear least squares")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_CUDA": [True, False],
        "use_glog":  [True, False], #TODO Set to true once gflags with nothreads=False binaries are available. Using MINILOG has a big performance drawback.
        "use_gflags": [True, False, "deprecated"],
        "use_custom_blas": [True, False],
        "use_eigen_sparse": [True, False],
        "use_TBB": [True, False],
        "use_CXX11_threads": [True, False],
        "use_CXX11": [True, False],
        "use_schur_specializations": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_CUDA" : False,
        "use_glog": False,
        "use_gflags": "deprecated",
        "use_custom_blas": True,
        "use_eigen_sparse": True,
        "use_TBB": False,
        "use_CXX11_threads": False,
        "use_CXX11": False,
        "use_schur_specializations": True,
    }

    @property
    def _min_cppstd(self):
        if Version(self.version) >= "2.2.0":
            return "17"
        if Version(self.version) >= "2.0.0":
            return "14"
        return "98"

    @property
    def _compilers_minimum_version(self):
        return {
            "14": {
                "apple-clang": "5",
                "clang": "5",
                "gcc": "5",
                "msvc": "190",
                "Visual Studio": "14",
            },
            "17": {
                "apple-clang": "10",
                "clang": "7",
                "gcc": "8",
                "msvc": "191",
                "Visual Studio": "15",
            },
        }.get(self._min_cppstd, {})

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) >= "2.0":
            del self.options.use_TBB
            del self.options.use_CXX11_threads
            del self.options.use_CXX11

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.use_gflags != "deprecated":
            self.output.warning("use_gflags option is deprecated")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True)
        if self.options.use_glog:
            self.requires("glog/0.6.0", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("use_TBB"):
            self.requires("onetbb/2020.3")
        if self.version == "commit8c50a34":
            self.requires("abseil/[>=20240116.1 <=20250127.0]", transitive_headers=True, transitive_libs=True)

    def package_id(self):
        del self.info.options.use_gflags

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def build_requirements(self):
        if Version(self.version) >= "2.2.0":
            self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MINIGLOG"] = not self.options.use_glog
        tc.variables["GFLAGS"] = False # useless for the lib itself, gflags is not a direct dependency
        tc.variables["SUITESPARSE"] = False
        tc.variables["LAPACK"] = False
        tc.variables["SCHUR_SPECIALIZATIONS"] = self.options.use_schur_specializations
        tc.variables["CUSTOM_BLAS"] = self.options.use_custom_blas
        tc.variables["EIGENSPARSE"] = self.options.use_eigen_sparse
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_DOCUMENTATION"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_BENCHMARKS"] = False

        ceres_version = Version(self.version)
        if ceres_version >= "2.2.0":
            tc.variables["USE_CUDA"] = self.options.use_CUDA;
        elif ceres_version >= "2.1.0":
            tc.variables["CUDA"] = self.options.use_CUDA;
        if ceres_version >= "2.2.0":
            tc.variables["EIGENMETIS"] = False
        if ceres_version >= "2.0.0":
            tc.variables["PROVIDE_UNINSTALL_TARGET"] = False
            if is_apple_os(self):
                tc.variables["ACCELERATESPARSE"] = True
        if ceres_version < "2.2.0":
            tc.variables["CXSPARSE"] = False
            if is_msvc(self):
                tc.variables["MSVC_USE_STATIC_CRT"] = is_msvc_static_runtime(self)
        if ceres_version < "2.1.0":
            tc.variables["LIB_SUFFIX"] = ""
        if ceres_version < "2.0.0":
            tc.variables["CXX11"] = self.options.use_CXX11
            tc.variables["OPENMP"] = False
            tc.variables["TBB"] = self.options.use_TBB
            tc.variables["CXX11_THREADS"] = self.options.use_CXX11_threads
        # IOS_DEPLOYMENT_TARGET variable was added to iOS.cmake file in 1.12.0 version
        if self.settings.os == "iOS":
            tc.variables["IOS_DEPLOYMENT_TARGET"] = self.settings.os.version
        tc.generate()

        CMakeDeps(self).generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "CMake"))
        self._create_cmake_module_variables(os.path.join(self.package_folder, self._module_variables_file_rel_path))

    def _create_cmake_module_variables(self, module_file):
        # Define several variables of upstream CMake config file which are not
        # defined out of the box by CMakeDeps.
        # See https://github.com/ceres-solver/ceres-solver/blob/master/cmake/CeresConfig.cmake.in
        content = textwrap.dedent(f"""\
            set(CERES_FOUND TRUE)
            set(CERES_VERSION {self.version})
            if(NOT DEFINED CERES_LIBRARIES)
                set(CERES_LIBRARIES Ceres::ceres)
            endif()
        """)
        save(self, module_file, content)

    @property
    def _module_variables_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    @property
    def _cuda_toolkit_root(self):
        # CUDA is consumed as a system dependency here (found via find_package(CUDAToolkit) at
        # build time, same as the colmap recipe), not as a conan package, so we locate it the
        # same way: CUDA_PATH/CUDAToolkit_ROOT env var, falling back to resolving nvcc on PATH.
        cuda_path = os.environ.get("CUDAToolkit_ROOT") or os.environ.get("CUDA_PATH")
        if cuda_path:
            return cuda_path
        nvcc = shutil.which("nvcc")
        if nvcc:
            # nvcc lives at <cuda_root>/bin/nvcc
            return os.path.dirname(os.path.dirname(nvcc))
        return None

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Ceres")
        self.cpp_info.set_property("cmake_target_name", "Ceres::ceres")
        # see https://github.com/ceres-solver/ceres-solver/blob/2.2.0/cmake/CeresConfig.cmake.in#L334-L340
        self.cpp_info.set_property("cmake_target_aliases", ["ceres"])
        self.cpp_info.set_property("cmake_build_modules", [self._module_variables_file_rel_path])

        libsuffix = ""
        if self.settings.build_type == "Debug":
            libsuffix = "-debug"
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["ceres"].libs = [f"ceres{libsuffix}"]
        if self.options.use_CUDA:
            # Ceres' CUDA-enabled build compiles its own CUDA kernels (used by
            # cuda_vector.cc/dense_cholesky.cc/dense_qr.cc, e.g. CudaSetZeroFP64,
            # CudaDtDxpy, CudaFP64ToFP32, CudaDsxpy) into a *separate* static library
            # (libceres_cuda_kernels[-debug].a) rather than folding them into libceres
            # itself. It must be listed after "ceres" so the linker sees it once the
            # unresolved references from libceres are already pending.
            self.cpp_info.components["ceres"].libs.append(f"ceres_cuda_kernels{libsuffix}")
        self.cpp_info.components["ceres"].includedirs.append(os.path.join("include", "ceres"))
        if not self.options.use_glog:
            self.cpp_info.components["ceres"].includedirs.append(os.path.join("include", "ceres", "internal", "miniglog"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ceres"].system_libs.append("m")
            if self.options.get_safe("use_CXX11_threads", True):
                self.cpp_info.components["ceres"].system_libs.append("pthread")
        elif is_apple_os(self):
            if Version(self.version) >= "2":
                self.cpp_info.components["ceres"].frameworks.append("Accelerate")
        self.cpp_info.components["ceres"].requires = ["eigen::eigen"]
        if self.options.use_glog:
            self.cpp_info.components["ceres"].requires.append("glog::glog")
        if self.options.get_safe("use_TBB"):
            self.cpp_info.components["ceres"].requires.append("onetbb::onetbb")
        if self.version == "commit8c50a34":
            self.cpp_info.components["ceres"].requires.append("abseil::abseil")

        if self.options.use_CUDA:
            # When built with USE_CUDA/CUDA, Ceres' own CUDA dense/sparse linear algebra
            # backends (cuda_vector.cc, dense_cholesky.cc, dense_qr.cc, cuda_sparse_cholesky.cc,
            # ...) call directly into cuBLAS/cuSOLVER/cuSPARSE/cuDSS. Ceres' upstream CMake
            # config links these privately into the static ceres lib target, but that is not
            # enough for a static consumer: without also declaring them here, a downstream
            # executable linking Ceres::ceres (e.g. colmap) fails with "undefined reference to
            # cublasCreate_v2/cusolverDn.../cusparse.../cudss..." at its own final link step.
            cuda_libs = ["cudart", "cublas", "cusparse", "cusolver"]
            if self.version == "commit8c50a34":
                # cuDSS (NVIDIA's sparse direct solver) support landed on ceres-solver's master
                # branch after the last tagged release (2.2.0); only this pinned master commit
                # actually calls into it.
                cuda_libs.append("cudss")
            self.cpp_info.components["ceres"].system_libs.extend(cuda_libs)

            cuda_root = self._cuda_toolkit_root
            if cuda_root:
                for lib_subdir in ("lib64", os.path.join("targets", "x86_64-linux", "lib"), "lib"):
                    candidate = os.path.join(cuda_root, lib_subdir)
                    if os.path.isdir(candidate):
                        self.cpp_info.components["ceres"].libdirs.append(candidate)
            if self.settings.os in ["Linux", "FreeBSD"]:
                # cuDSS installs its own .so via the distro package (not under the CUDA toolkit
                # tree) at this standard multiarch path on Debian/Ubuntu.
                multiarch_libdir = "/usr/lib/x86_64-linux-gnu"
                if os.path.isdir(multiarch_libdir):
                    self.cpp_info.components["ceres"].libdirs.append(multiarch_libdir)

        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.components["ceres"].system_libs.append(libcxx)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Ceres"
        self.cpp_info.names["cmake_find_package_multi"] = "Ceres"
        self.cpp_info.components["ceres"].build_modules["cmake_find_package"] = [self._module_variables_file_rel_path]
        self.cpp_info.components["ceres"].build_modules["cmake_find_package_multi"] = [self._module_variables_file_rel_path]
        self.cpp_info.components["ceres"].set_property("cmake_target_name", "Ceres::ceres")
