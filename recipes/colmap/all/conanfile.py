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
               "with_cuda": [True, False],
               "cuda_arch": [None, "ANY"],
               "with_openmp": [True, False],
               "with_opengl": [True, False],
               "with_profiling": [True, False],
               "with_test": [True, False],
               "with_gui": [True, False],
               "with_cgal": [True, False]}
    default_options = {"shared": False,
                       "with_cuda": False,
                       "cuda_arch": "all-major",
                       "with_openmp": True,
                       "with_opengl": True,
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
        if self.options.shared:
            self.options.rm_safe("fPIC")
        #use glog for ceres, instead there are some conflicts between miniglog of ceres and glog of colmap
        self.options["ceres-solver"].use_glog = True
        self.options["ceres-solver"].use_gflags = True

        #Colmap needs to link FreeImage in shared mode to automatically initialize plugins; http://graphics.stanford.edu/courses/cs148-10-summer/docs/FreeImage3131.pdf
        self.options["freeimage"].shared=True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("ceres-solver/2.2.0")
        #glog directly from ceres
        #gflags directly from ceres
      
        self.requires("boost/1.84.0")
        self.requires("freeimage/3.18.0")
        
        #Qt for GUI - pb when no GUI
        if self.options.with_gui:
            self.requires("qt/5.15.2")
        #No GUI then no opengl => currently pb : must have opengl dependency in source code
        if self.options.with_opengl:
            self.requires("glew/2.2.0")
            self.requires("opengl/system")

        # Flann : Conan solar recipe : same as Conan center recipe with cpp-std 17 patch
        self.requires("flann/1.9.2@")

        self.requires("sqlite3/3.46.0@")
        self.requires("metis/5.2.1@")

        if self.options.with_cgal:
            self.requires("cgal/5.6.1@")
    
    def validate(self):
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Visual Studio with static runtime is not supported for shared library.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
    
    def _patch_sources(self):
        apply_conandata_patches(self) 


    def generate(self):
        # move dir for cmake build
        copy(self, "GenerateVersionDefinitions.cmake", os.path.join(self.source_folder, "cmake"), self.source_folder)
        # remove files for cmake build
        os.remove(os.path.join(self.source_folder, "cmake/FindMetis.cmake"))
        os.remove(os.path.join(self.source_folder, "cmake/FindFreeImage.cmake"))
        os.remove(os.path.join(self.source_folder, "cmake/FindGlew.cmake"))
        os.remove(os.path.join(self.source_folder, "cmake/FindGlog.cmake"))
        os.remove(os.path.join(self.source_folder, "cmake/FindFLANN.cmake"))
        os.remove(os.path.join(self.source_folder, "cmake/FindLZ4.cmake"))
        
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"
        tc.variables["BOOST_STATIC"] = True
        tc.variables["CGAL_ENABLED"] = bool(self.options.get_safe("with_cgal", False))
        tc.variables["OPENGL_ENABLED"] = self.options.get_safe("with_opengl", False)
        tc.variables["OPENMP_ENABLED"] = self.options.get_safe("with_openmp", False)
        tc.variables["CUDA_ENABLED"] = self.options.get_safe("with_cuda", False)
        tc.variables["PROFILING_ENABLED"] = self.options.get_safe("with_profiling", False)
        tc.variables["TEST_ENABLED"] = self.options.get_safe("with_test", False)
        tc.variables["SIMD_ENABLED"] = True
        tc.variables["GUI_ENABLED"] = self.options.get_safe("with_gui", False)
        #build for recent CUDA_ARCHS
        tc.variables["CMAKE_CUDA_ARCHITECTURES"] = self.options.cuda_arch
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)

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


