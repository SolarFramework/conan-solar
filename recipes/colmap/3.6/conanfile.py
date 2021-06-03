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
               "with_test": [True, False]}
    default_options = {"shared": False,
                       "with_cuda": True,
                       "with_openmp": True,
                       "with_opengl": True,
                       "with_profiling": True, #colmap binary needs -lprofiler -ltcmalloc on linux
                       "with_test": False}
    exports_sources = ["CMakeLists.txt", "patches/*"]
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    generators = "cmake", "cmake_find_package"
    short_paths = True

    def requirements(self):
        self.requires("ceres-solver/2.0.0@conan-solar/stable")
        #self.requires("glog/0.4.0") # depends with ceres
        #self.requires("gflags/2.2.2@conan-solar/stable")  # depends with ceres
        self.requires("boost/1.75.0")
        self.requires("FreeImage/3.18.0@conan-solar/stable")
        self.requires("qt/5.15.2@bincrafters/stable")
        if self.options.with_opengl:
            self.requires("glew/2.2.0")
            self.requires("opengl/system")
        self.requires("flann/1.9.1@conan-solar/stable")        
        
        # Or adjust any other available option
        self.options["qt"].with_zstd = False
        self.options["ceres-solver"].use_glog = True
        self.options["ceres-solver"].use_gflags = True
        self.options["ceres-solver"].use_cxsparse = False
        # TODO keep ?!
        self.options["boost"].zlib=False
        self.options["boost"].bzip2=False
        self.options["boost"].numa=False
        
        self.options["flann"].shared = self.options.shared
        self.options["boost"].shared = self.options.shared
        self.options["ceres-solver"].shared = self.options.shared
        self.options["FreeImage"].shared = self.options.shared
        #todo : check other libs as shared?!

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("colmap-{}".format(self.version), self._source_subfolder)
        
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        
        # OLD replacement - now done with patches
        #cmake_path = os.path.join(self._source_subfolder, "CMakeLists.txt")
        #tools.replace_in_file(cmake_path, "set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)", "set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR})")
        
        #cmakelib_path = os.path.join(self._source_subfolder, "lib/CMakeLists.txt")
        #tools.replace_in_file(cmakelib_path, "add_subdirectory(FLANN)", "#add_subdirectory(FLANN)")
                        
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
        self.cpp_info.includedirs = ["include", 
                                        os.path.join("include","colmap" "base"), 
                                        os.path.join("include","colmap" "cont²rollers"),
                                        os.path.join("include","colmap" "estimators"),
                                        #os.path.join("include","colmap" "exe"),
                                        os.path.join("include","colmap" "feature"),
                                        #os.path.join("include","colmap" "lib"),
                                        os.path.join("include","colmap" "mvs"),
                                        os.path.join("include","colmap" "optim"),
                                        os.path.join("include","colmap" "retrieval"),
                                        os.path.join("include","colmap" "sfm"),
                                        os.path.join("include","colmap" "tools"),
                                        os.path.join("include","colmap" "ui"),
                                        os.path.join("include","colmap" "util")]
        self.cpp_info.libs = tools.collect_libs(self)


    def package(self):
        # Retrieve common helpers
        import common

        # Fix all hard coded path to conan package in all .cmake files
#        common.fix_conan_path(self, self.package_folder, '*.cmake')
        
        if self.settings.os == 'Android':
            if not self.options.shared:
                self.cpp_info.includedirs.append(
                    os.path.join('sdk', 'native', 'jni', 'include'))
                self.cpp_info.libdirs.append(
                    os.path.join('sdk', 'native', 'staticlibs', self._android_arch))


