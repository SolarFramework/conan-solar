from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os
from shutil import copy, copyfile

required_conan_version = ">=1.29.1"

class ColmapConan(ConanFile):
    name = "colmap"
    license = "new BSD license"
    homepage = "https://colmap.github.io/"
    description = "a general-purpose Structure From Motion and Multi-View Stereo"
    url = "https://github.com/Solar-Framework/conan-solar/recipes/colmap/3.6"
    topics = ("computer-vision", "image-processing")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "with_cuda": [True, False],
               "with_openmp": [True, False],
               "with_opengl": [True, False],
               "with_profiling": [True, False],
               "with_test": [True, False],
               "with_gui": [True, False]}
    default_options = {"shared": False,
                       "with_cuda": False,
                       "with_openmp": True,
                       "with_opengl": True,
                       "with_profiling": False, #colmap binary needs -lprofiler -ltcmalloc on linux
                       "with_test": False,
                       "with_gui":False}
    exports_sources = ["CMakeLists.txt", "patches/*"]
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    generators = "cmake", "cmake_find_package"
    short_paths = True

    def requirements(self):
        self.requires("ceres-solver/2.0.0")
        #glog directly from ceres
        #gflags directly from ceres
      
        # boost in 1.74 : conflict with other because have zlib/1.2.11
        self.requires("boost/1.76.0")
        self.requires("freeimage/3.18.0")
        
        #Qt for GUI - pb when no GUI
        if self.options.with_gui:
            self.requires("qt/5.15.2")
        #No GUI then no opengl => currently pb : must have opengl dependency in source code
        if self.options.with_opengl:
            self.requires("glew/2.2.0")
            self.requires("opengl/system")

        # Flann : Conan solar recipe : same as Conan center recipe with cpp-std 17 patch
        self.requires("flann/1.9.1@conan-solar/stable")        
        #use glog for ceres, instead there are some conflicts between miniglog of ceres and glog of colmap
        self.options["ceres-solver"].use_glog = True
        self.options["ceres-solver"].use_gflags = True
        #Colmap needs to link FreeImage in shared mode to automatically initialize plugins; http://graphics.stanford.edu/courses/cs148-10-summer/docs/FreeImage3131.pdf
        self.options["freeimage"].shared=True
        
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("colmap-{}".format(self.version), self._source_subfolder)
        
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
                        
    @property
    def _android_arch(self):
        arch = str(self.settings.arch)
        return tools.to_android_abi(arch)

    def build(self):
        # move dir for cmake build
        copy(os.path.join(self._source_subfolder, "cmake/GenerateVersionDefinitions.cmake"), os.path.join(self._source_subfolder, "GenerateVersionDefinitions.cmake"))
        # remove files for cmake build
        os.remove(os.path.join(self._source_subfolder, "cmake/FindEigen3.cmake"))
        os.remove(os.path.join(self._source_subfolder, "cmake/FindFreeImage.cmake"))
        os.remove(os.path.join(self._source_subfolder, "cmake/FindGlew.cmake"))
        os.remove(os.path.join(self._source_subfolder, "cmake/FindGlog.cmake"))        
            
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"
        cmake.definitions["BOOST_STATIC"] = False if self.options.shared else True
        cmake.definitions["CGAL_ENABLED"] = True
        cmake.definitions["OPENGL_ENABLED"] = self.options.with_opengl
        cmake.definitions["OPENMP_ENABLED"] = self.options.with_openmp
        cmake.definitions["CUDA_ENABLED"] = self.options.with_cuda
        cmake.definitions["PROFILING_ENABLED"] = self.options.with_profiling
        cmake.definitions["TEST_ENABLED"] = self.options.with_test
        cmake.definitions["SIMD_ENABLED"] = True
        cmake.definitions["GUI_ENABLED"] = self.options.with_gui

        if not tools.os_info.is_windows:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = True

        cmake.configure(build_folder=self._build_subfolder)
        cmake.build()
        cmake.install()

    def package_info(self):
    
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
        
        self.cpp_info.names["cmake_find_package"] = "colmap"
        self.cpp_info.names["cmake_find_package_multi"] = "colmap"
        self.cpp_info.includedirs = [os.path.join(self.package_folder,"include","colmap"), 
                                     os.path.join(self.package_folder,"include","colmap","lib")]
        self.cpp_info.libdirs = [os.path.join(self.package_folder,"lib","colmap")]
        
        if self.options.with_cuda and self.settings.compiler == 'Visual Studio':
            cuda_platform = {'x86': 'Win32',
                             'x86_64': 'x64'}.get(str(self.settings.arch))
            cuda_path = os.environ.get('CUDA_PATH')
            self.cpp_info.libdirs.append(os.path.join(cuda_path, "lib", cuda_platform))
                        
        self.cpp_info.libs = tools.collect_libs(self)


    def package(self):
        
        # Fix all hard coded path to conan package in all .cmake files
#        common.fix_conan_path(self, self.package_folder, '*.cmake')
        
        if self.settings.os == 'Android':
            if not self.options.shared:
                self.cpp_info.includedirs.append(
                    os.path.join('sdk', 'native', 'jni', 'include'))
                self.cpp_info.libdirs.append(
                    os.path.join('sdk', 'native', 'staticlibs', self._android_arch))


