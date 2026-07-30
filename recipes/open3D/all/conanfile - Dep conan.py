from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import Environment
from conan.tools.files import apply_conandata_patches, collect_libs, export_conandata_patches, get, copy, replace_in_file
from conan.tools.gnu import PkgConfigDeps
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
        "with_tools": [True, False],
        "with_unit_tests": [True, False],
        "with_benchmarks": [True, False],
        "with_jupyter_extension": [True, False],
        "with_tensorflow_ops": [True, False],
        "with_pytorch_ops": [True, False],
        "with_open3d_ml": [True, False],
        "with_librealsense": [True, False],
        "with_azure_kinect": [True, False],
        # Dépendances tierces : False = vendored (embarqué par Open3D, comportement historique)
        #                        True  = utilise la recette Conan correspondante (USE_SYSTEM_*)
        "use_system_eigen3": [True, False],
        "use_system_fmt": [True, False],
        "use_system_tbb": [True, False],
        "use_system_curl": [True, False],
        "use_system_openssl": [True, False],
        "use_system_libpng": [True, False],
        "use_system_libjpeg": [True, False],
        "use_system_jsoncpp": [True, False],
        "use_system_glew": [True, False],
        "use_system_glfw": [True, False],
        "use_system_assimp": [True, False],
        "use_system_qhullcpp": [True, False],
        "use_system_embree": [True, False],
        "use_system_nanoflann": [True, False],
        "use_system_tinygltf": [True, False],
        "use_system_tinyobjloader": [True, False],
        "use_system_msgpack": [True, False],
        "use_system_zeromq": [True, False],
        "use_system_liblzf": [True, False],
     }
    default_options = {
        # minizip (dep d'assimp) expose HAVE_BZIP2 en define public -> remonte jusqu'à
        # utility/ExtractZIP.cpp qui inclut alors <bzlib.h> sans son include dir.
        "minizip/*:bzip2": False,
        "shared": False,
        "fPIC": False,
        "with_cuda": False,
        "with_gui": False,
        "with_python_module": False,
        "with_ispc_module": False,
        "with_webrtc": False,
        "with_examples": False,
        "with_tools": False,          # exécutables annexes (ConvertPointCloud, GLInfo...) : inutiles ici
        "with_unit_tests": False,
        "with_benchmarks": False,
        "with_jupyter_extension": False,
        "with_tensorflow_ops": False,
        "with_pytorch_ops": False,
        "with_open3d_ml": False,
        "with_librealsense": False,
        "with_azure_kinect": False,
        "use_system_eigen3": True,
        "use_system_fmt": True,
        "use_system_tbb": True,
        "use_system_curl": True,
        "use_system_openssl": True,
        "use_system_libpng": True,   # nécessite minizip (voir generate()) pour unzip.h/ioapi.h
        "use_system_libjpeg": True,
        "use_system_jsoncpp": True,
        "use_system_glew": True,       # compilé même si BUILD_GUI=OFF (visualizer OpenGL legacy)
        "use_system_glfw": True,       # idem
        "use_system_assimp": True,
        "use_system_qhullcpp": False,  # vendored : le paquet Conan qhull ne fournit pas libqhullcpp
        "use_system_embree": True,     # nécessite recette forkée, voir embree-msvc-avx512.patch
        "use_system_nanoflann": True,
        "use_system_tinygltf": True,   # header-only, voir defines TINYGLTF_IMPLEMENTATION dans generate()
        "use_system_tinyobjloader": True,
        "use_system_msgpack": True,
        "use_system_zeromq": True,
        "use_system_liblzf": False,    # vendored : mismatch de layout d'include (liblzf/lzf.h vs lzf.h)
        # Contrainte transitive : onetbb exige hwloc en shared
        "hwloc/*:shared": True,
    }
    
    short_paths = True

    # option Conan -> (référence du paquet, variable CMake USE_SYSTEM_* d'Open3D)
    _system_deps = {
        "use_system_eigen3":   ("eigen/3.4.0",          "USE_SYSTEM_EIGEN3"),
        "use_system_fmt":      ("fmt/10.2.1",           "USE_SYSTEM_FMT"),
        "use_system_tbb":      ("onetbb/2021.12.0",     "USE_SYSTEM_TBB"),
        "use_system_curl":     ("libcurl/8.10.1",       "USE_SYSTEM_CURL"),
        "use_system_openssl":  ("openssl/3.3.2",        "USE_SYSTEM_OPENSSL"),
        "use_system_libpng":   ("libpng/1.6.44",        "USE_SYSTEM_PNG"),
        "use_system_libjpeg":  ("libjpeg-turbo/3.0.4",  "USE_SYSTEM_JPEG"),
        "use_system_jsoncpp":  ("jsoncpp/1.9.5",         "USE_SYSTEM_JSONCPP"),
        "use_system_glew":     ("glew/2.2.0",           "USE_SYSTEM_GLEW"),
        "use_system_glfw":     ("glfw/3.4",             "USE_SYSTEM_GLFW"),
        "use_system_assimp":   ("assimp/5.4.3",         "USE_SYSTEM_ASSIMP"),
        "use_system_qhullcpp": ("qhull/8.0.1",          "USE_SYSTEM_QHULLCPP"),
        "use_system_embree":   ("embree/4.4.1",         "USE_SYSTEM_EMBREE"),
        "use_system_nanoflann":     ("nanoflann/1.6.0",       "USE_SYSTEM_NANOFLANN"),
        "use_system_tinygltf":      ("tinygltf/2.9.7",        "USE_SYSTEM_TINYGLTF"),
        "use_system_tinyobjloader": ("tinyobjloader/2.0.0-rc10", "USE_SYSTEM_TINYOBJLOADER"),
        "use_system_msgpack":       ("msgpack-cxx/7.0.0",     "USE_SYSTEM_MSGPACK"),
        "use_system_zeromq":        (["zeromq/4.3.5", "cppzmq/4.10.0"], "USE_SYSTEM_ZEROMQ"),
        "use_system_liblzf":        ("liblzf/3.6",            "USE_SYSTEM_LIBLZF"),
    }

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

    def requirements(self):
        for opt_name, (refs, _) in self._system_deps.items():
            if self.options.get_safe(opt_name):
                for ref in (refs if isinstance(refs, list) else [refs]):
                    self.requires(ref)

        if self.options.get_safe("use_system_tinygltf"):
            self.requires("stb/cci.20240531", override=True)  # tinygltf et assimp veulent des versions différentes

        if self.options.get_safe("use_system_libpng"):
            # unzip.h/ioapi.h (utility/ExtractZIP.cpp) sont le contrib/minizip de zlib :
            # identique au paquet Conan minizip, qui les installe sous include/minizip.
            self.requires("minizip/1.2.13")

    def build_requirements(self):
        if self.options.get_safe("use_system_curl") or self.options.get_safe("use_system_zeromq"):
            self.tool_requires("pkgconf/2.1.0")  # nécessaire à la détection curl/libzmq via pkg-config

    def source(self):
        get(self, **self.conan_data["sources"][self.version][0],
            destination=self.source_folder, strip_root=True)
    
    def _patch_sources(self):
        apply_conandata_patches(self)

        # include_directories() (portée dossier, hérité par toutes les cibles définies après,
        # y compris dans les sous-dossiers) : bien plus fiable que CMAKE_CXX_FLAGS ou la variable
        # d'environnement INCLUDE, que MSBuild ignore par défaut (contrairement à Ninja/Make).
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        'message(STATUS "Open3D ${OPEN3D_VERSION_FULL}")',
                        'message(STATUS "Open3D ${OPEN3D_VERSION_FULL}")\n'
                        'include_directories(${OPEN3D_CONAN_EXTRA_INCLUDE_DIRS})',
                        strict=False)

        # cpp/tools et OfflineReconstruction sont ajoutés sans condition par Open3D ;
        # on les gate derrière with_tools. strict=False : idempotent si déjà patché.
        replace_in_file(self, os.path.join(self.source_folder, "cpp", "CMakeLists.txt"),
                        "add_subdirectory(tools)",
                        "if(BUILD_OPEN3D_TOOLS)\n    add_subdirectory(tools)\nendif()",
                        strict=False)
        replace_in_file(self, os.path.join(self.source_folder, "cpp", "apps", "CMakeLists.txt"),
                        "open3d_add_app_common(OfflineReconstruction OfflineReconstruction OfflineReconstruction)",
                        "if(BUILD_OPEN3D_TOOLS)\n    open3d_add_app_common(OfflineReconstruction OfflineReconstruction OfflineReconstruction)\nendif()",
                        strict=False)
    
    def _inject_header_dep_flags(self, tc, dep_name, extra_includedirs):
        """Open3D ne propage pas toujours les include dirs des dépendances "system" vers
        toutes ses cibles internes (glew/glfw en tant que cibles HEADER, cppzmq et minizip
        qui n'apparaissent dans aucun find_package()/pkg-config). Plutôt que de compter sur
        la propagation via CMAKE_CXX_FLAGS (fragile selon les cibles), on empile les include
        dirs dans une liste accumulée en fin de generate() dans la variable d'environnement
        INCLUDE (MSVC) / CPLUS_INCLUDE_PATH (gcc/clang), que le compilateur consulte pour
        CHAQUE fichier compilé, indépendamment du graphe de cibles CMake. Les defines, eux,
        passent bien par CMAKE_CXX_FLAGS (extra_cxxflags), donc restent ici."""
        cpp = self.dependencies[dep_name].cpp_info.aggregated_components()
        extra_includedirs.extend(cpp.includedirs)
        for define in cpp.defines:
            tc.extra_cxxflags.append(f"-D{define}")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
        
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["STATIC_WINDOWS_RUNTIME"] = is_msvc_static_runtime(self)

        tc.cache_variables["BUILD_GUI"] = self.options.with_gui
        tc.cache_variables["BUILD_PYTHON_MODULE"] = self.options.with_python_module
        tc.cache_variables["BUILD_ISPC_MODULE"] = self.options.with_ispc_module
        tc.cache_variables["BUILD_WEBRTC"] = self.options.with_webrtc
        tc.cache_variables["BUILD_EXAMPLES"] = self.options.with_examples
        tc.cache_variables["BUILD_OPEN3D_TOOLS"] = bool(self.options.with_tools)  # cf. _patch_sources
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

        # Bascule Open3D sur les libs Conan pour chaque dépendance passée en mode "system"
        for opt_name, (_, cmake_var) in self._system_deps.items():
            tc.cache_variables[cmake_var] = bool(self.options.get_safe(opt_name))
        
        if self.options.get_safe("use_system_curl") and is_msvc(self):
            tc.extra_cxxflags.append("/wd4005")  # CURL_STATICLIB redéfinie par libcurl -> C4005 en warning-as-error

        # Include dirs à injecter via variable d'environnement (voir _inject_header_dep_flags)
        extra_includedirs = []

        if self.options.get_safe("use_system_glew"):
            self._inject_header_dep_flags(tc, "glew", extra_includedirs)
        if self.options.get_safe("use_system_glfw"):
            self._inject_header_dep_flags(tc, "glfw", extra_includedirs)
        if self.options.get_safe("use_system_zeromq"):
            extra_includedirs.extend(self.dependencies["cppzmq"].cpp_info.includedirs)  # zmq.hpp
        if self.options.get_safe("use_system_libpng"):
            extra_includedirs.extend(self.dependencies["minizip"].cpp_info.includedirs)  # unzip.h/ioapi.h

        if self.options.get_safe("use_system_tinygltf"):
            # tinygltf Conan est header-only ; Open3D ne définit ces macros que dans sa branche vendored
            tc.preprocessor_definitions["TINYGLTF_IMPLEMENTATION"] = None
            tc.preprocessor_definitions["STB_IMAGE_IMPLEMENTATION"] = None
            tc.preprocessor_definitions["STB_IMAGE_WRITE_IMPLEMENTATION"] = None

        if extra_includedirs:
            # Consommée par include_directories() injecté dans _patch_sources() : portée
            # CMake native, indépendante des flags CXX et de l'environnement du process.
            tc.cache_variables["OPEN3D_CONAN_EXTRA_INCLUDE_DIRS"] = ";".join(
                inc.replace("\\", "/") for inc in extra_includedirs)

        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("embree", "cmake_target_name", "embree")  # Open3D attend `embree` sans namespace
        deps.generate()

        if self.options.get_safe("use_system_curl") or self.options.get_safe("use_system_zeromq"):
            # curl et libzmq sont détectés par Open3D via pkg-config, pas find_package()
            pkg = PkgConfigDeps(self)
            pkg.generate()

            env = Environment()
            env.define_path("PKG_CONFIG_PATH", self.generators_folder)
            env.vars(self, scope="build").save_script("open3d_pkg_config_path")

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