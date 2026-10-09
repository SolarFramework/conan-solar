from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, export_conandata_patches, get, copy, replace_in_file 
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.54.0"

class ColmapConan(ConanFile):
    name = "colmap"
    license = "new BSD license"
    homepage = "https://colmap.github.io/"
    description = "a general-purpose Structure From Motion and Multi-View Stereo"
    url = "https://github.com/Solar-Framework/conan-solar/recipes/colmap/3.6"
    topics = ("computer-vision", "image-processing")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_cuda": [True, False],
               "cuda_arch": [None, "ANY"],
               "with_openmp": [True, False],
               "with_opengl": [True, False],
               "with_onnx": [True, False],
               "with_poselib": [True, False],
               "with_profiling": [True, False],
               "with_test": [True, False],
               "with_gui": [True, False],
               "with_cgal": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_cuda": False,
                       "cuda_arch": "all-major",
                       "with_openmp": True,
                       "with_opengl": True,
                       "with_onnx": False,
                       "with_poselib": True,
                       "with_profiling": False, #colmap binary needs -lprofiler -ltcmalloc on linux
                       "with_test": False,
                       "with_gui":False,
                       "with_cgal":False}
    
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
        #use glog for ceres, instead there are some conflicts between miniglog of ceres and glog of colmap
        self.options["ceres-solver"].use_glog = True
        self.options["ceres-solver"].use_gflags = True
        
        if (self.options.with_cuda):
            self.options["ceres-solver"].use_CUDA = True

        #Colmap needs to link FreeImage in shared mode to automatically initialize plugins; http://graphics.stanford.edu/courses/cs148-10-summer/docs/FreeImage3131.pdf
        if (Version(self.version) < "4.0.0"):
           self.options["freeimage"].shared=True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):      
        self.requires("boost/1.84.0")
        #use a freeImage without openexr and libtiff using openexr as freeimage is not compatible with openexr 3.x.x -> conflicts with openimageio
        if (Version(self.version) < "4.0.0"):
            self.requires("freeimage/3.18.0@")
        
        if (Version(self.version) >= "4.0.0"):
            self.requires("OpenImageIO/[~3.1]")
            self.requires("faiss/1.12.0")
            if self.options.with_onnx:
                self.requires("onnxruntime/1.24.4")
            #PoseLib has no tagged release recent enough for colmap (which pins an exact,
            #post-2.0.5 commit via FetchContent, see src/thirdparty/CMakeLists.txt); let
            #colmap's own CMake FetchContent fetch it instead of a conan package.

        #Qt for GUI - pb when no GUI
        if self.options.with_gui:
            self.requires("qt/6.7.3")
        #No GUI then no opengl => currently pb : must have opengl dependency in source code
        if self.options.with_opengl:
            self.requires("glew/2.2.0")
            self.requires("opengl/system")

        # Flann : Conan solar recipe : same as Conan center recipe with cpp-std 17 patch
        if (Version(self.version) < "3.13"):
            requires("flann/1.9.2@", transitive_headers=True)

        self.requires("sqlite3/3.46.0@")
        self.requires("metis/5.2.1@")

        if self.options.with_cgal:
            self.requires("cgal/5.6.1@")

        self.requires("ceres-solver/commit8c50a34@conan-solar/stable")
        #glog directly from ceres
        #gflags directly from ceres
    
    def validate(self):
        if self.options.shared:
            raise ConanInvalidConfiguration("Colmap does not provide shared build mode.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
    
    def _patch_sources(self):
        apply_conandata_patches(self) 


    def generate(self):
        # move dir for cmake build
        copy(self, "GenerateVersionDefinitions.cmake", os.path.join(self.source_folder, "cmake"), self.source_folder)
        # remove files for cmake build
        os.remove(os.path.join(self.source_folder, "cmake/FindMetis.cmake"))
        if (Version(self.version) >= "4.0.0"):
            os.remove(os.path.join(self.source_folder, "cmake/Findonnxruntime.cmake"))
        if (Version(self.version) < "4.0.0"):
            os.remove(os.path.join(self.source_folder, "cmake/FindFreeImage.cmake"))
        os.remove(os.path.join(self.source_folder, "cmake/FindGlew.cmake"))
        os.remove(os.path.join(self.source_folder, "cmake/FindGlog.cmake"))
        if (Version(self.version) < "3.13"):
            os.remove(os.path.join(self.source_folder, "cmake/FindFLANN.cmake"))
            os.remove(os.path.join(self.source_folder, "cmake/FindLZ4.cmake"))
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_SHARED_LIBS"] = bool(self.options.get_safe("shared", False))
        tc.cache_variables["BOOST_STATIC"] = True
        tc.cache_variables["CGAL_ENABLED"] = bool(self.options.get_safe("with_cgal", False))
        tc.cache_variables["OPENGL_ENABLED"] = self.options.get_safe("with_opengl", False)
        tc.cache_variables["OPENMP_ENABLED"] = self.options.get_safe("with_openmp", False)
        
        if (Version(self.version) >= "4.0.0"):
            tc.cache_variables["ONNX_ENABLED"] = self.options.get_safe("with_onnx", False)
            tc.cache_variables["FETCH_ONNX"] = False
            tc.cache_variables["POSELIB_ENABLED"] = self.options.get_safe("with_poselib", False)
            tc.cache_variables["FETCH_POSELIB"] = self.options.get_safe("with_poselib", False)
            tc.cache_variables["FETCH_FAISS"] = False
            # Force a deterministic hash map backend instead of colmap's own
            # auto-detection (Boost version dependent): package_info() below
            # mirrors this choice via the COLMAP_HASH_STD compile definition,
            # which downstream consumers (e.g. qmake/remaken based ones, that
            # don't get CMake's INTERFACE_COMPILE_DEFINITIONS automatically)
            # need to match exactly, since colmap/util/hash_containers.h picks
            # the actual container types based on this same macro.
            tc.cache_variables["COLMAP_HASH_MAP_BACKEND"] = "STD"
        
        tc.cache_variables["BLA_VENDOR"] = "Intel10_64lp"
        tc.cache_variables["CUDA_ENABLED"] = self.options.get_safe("with_cuda", False)
        tc.cache_variables["PROFILING_ENABLED"] = self.options.get_safe("with_profiling", False)
        tc.cache_variables["TEST_ENABLED"] = self.options.get_safe("with_test", False)
        tc.cache_variables["SIMD_ENABLED"] = True
        tc.cache_variables["GUI_ENABLED"] = self.options.get_safe("with_gui", False)
        #build for recent CUDA_ARCHS
        tc.variables["CMAKE_CUDA_ARCHITECTURES"] = self.options.cuda_arch        

        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

        if (Version(self.version) >= "4.0.0"):
            # Colmap headers (option_manager.h, mvs/*, file.h, ...) gate whole
            # members/declarations behind these COLMAP_*_ENABLED macros, which
            # colmap's own CMake only propagates to consumers through CMake's
            # target_compile_definitions(... PUBLIC/INTERFACE ...) mechanism.
            # Downstream builds that don't consume the colmap CMake target
            # directly (e.g. qmake/remaken, which only pulls include/lib dirs
            # and library names from this recipe's cpp_info) never see them,
            # so the consumer's view of the headers silently drifts from what
            # the compiled .a files actually contain (e.g. OptionManager loses
            # its patch_match_stereo/stereo_fusion members without
            # COLMAP_MVS_ENABLED). Mirror here exactly what generate() passes
            # to CMake above, so consumers observe the same macros colmap's
            # own library was compiled with.
            defines = [
                # MVS_ENABLED, LSD_ENABLED and COLMAP_HASH_MAP_BACKEND are not
                # exposed as recipe options: they are left at their CMakeLists
                # defaults / forced value above, so they're always active here.
                "COLMAP_MVS_ENABLED",
                "COLMAP_LSD_ENABLED",
                "COLMAP_HASH_STD",
            ]
            with_cuda = bool(self.options.get_safe("with_cuda", False))
            with_gui = bool(self.options.get_safe("with_gui", False))
            with_opengl = bool(self.options.get_safe("with_opengl", False)) and with_gui
            if with_cuda:
                defines.append("COLMAP_CUDA_ENABLED")
            if with_cuda or with_opengl:
                defines.append("COLMAP_GPU_ENABLED")
            if with_gui:
                defines.append("COLMAP_GUI_ENABLED")
            if self.options.get_safe("with_cgal", False):
                defines.append("COLMAP_CGAL_ENABLED")
            if self.options.get_safe("with_onnx", False):
                defines.append("COLMAP_ONNX_ENABLED")
            self.cpp_info.defines = defines
        # bindir = os.path.join(self.package_folder, "bin")
        # self.output.info("Appending PATH environment variable: {}".format(bindir))
        # self.env_info.PATH.append(bindir)
        
        # self.cpp_info.names["cmake_find_package"] = "colmap"
        # self.cpp_info.names["cmake_find_package_multi"] = "colmap"
        # self.cpp_info.includedirs = [os.path.join(self.package_folder,"include","colmap"), 
        #                              os.path.join(self.package_folder,"include","colmap","lib")]
        # self.cpp_info.libdirs = [os.path.join(self.package_folder,"lib","colmap")]
        
        # if self.options.with_cuda:
        #     if self.settings.os == 'Windows':
        #         cuda_platform = {'x86': 'Win32',
        #                          'x86_64': 'x64'}.get(str(self.settings.arch))
        #         cuda_path = os.environ.get('CUDA_PATH')
        #         self.cpp_info.libdirs.append(os.path.join(cuda_path, "lib", cuda_platform))
        #         print ("-------------------- libdirs=", self.cpp_info.libdirs)
            
        #     if self.settings.os == 'Linux':
        #         cuda_path = os.environ.get('CUDA_PATH')
        #         self.cpp_info.libdirs.append(os.path.join(cuda_path, "lib64"))
                        
        # self.cpp_info.libs = tools.collect_libs(self)


    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        # Fix all hard coded path to conan package in all .cmake files
#        common.fix_conan_path(self, self.package_folder, '*.cmake')
        
        if self.settings.os == 'Android':
            if not self.options.shared:
                self.cpp_info.includedirs.append(
                    os.path.join('sdk', 'native', 'jni', 'include'))
                self.cpp_info.libdirs.append(
                    os.path.join('sdk', 'native', 'staticlibs', self._android_arch))


