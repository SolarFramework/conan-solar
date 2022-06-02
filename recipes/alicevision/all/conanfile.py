from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
#from git import Repo
import os
import subprocess
from shutil import copy, copyfile

required_conan_version = ">=1.29.1"

class AliceVisionConan(ConanFile):
    
    name = "alicevision"
    license = "MPLv2 license"
    homepage = "https://github.com/alicevision/AliceVision"
    description = "Photogrammetric Computer Vision Framework "
    url = "https://github.com/Solar-Framework/conan-solar"
    topics = ("computer-vision", "image-processing")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "with_cuda": [True, False],
               "with_popsift": [True, False]
    }
    default_options = { "shared": False,
                        "with_cuda": False,
                        "with_popsift": True
    }
    exports_sources = ["CMakeLists.txt", "patches/*"]
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    generators = "cmake", "cmake_find_package"
    short_paths = True

    def requirements(self):
        for req in self.conan_data["requirements"]:
            self.requires(req)
        
    def source(self):
        subprocess.check_call(["git", "clone", self.conan_data["sources"][self.version]["git"], self._source_subfolder])
        os.chdir(self._source_subfolder)
        subprocess.check_call(["git", "checkout", self.version])
        subprocess.check_call(["git", "submodule", "update", "--init"])

        for patch in self.conan_data["patches"][self.version]:
            print("patch: ", patch)
            tools.patch(**patch)
                        
    @property
    def _android_arch(self):
        arch = str(self.settings.arch)
        return tools.to_android_abi(arch)

    def configure(self):
        self.options['openimageio'].with_ffmpeg = False
        self.options['openimageio'].with_freetype = False
        self.options['openimageio'].with_giflib = False
        self.options['openimageio'].with_hdf5 = False
        self.options['openimageio'].with_libheif = False
        self.options['openimageio'].with_libwebp = False
        self.options['openimageio'].with_opencolorio = False
        self.options['openimageio'].with_opencv = False
        self.options['openimageio'].with_ptex = False

    def build(self):

        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"
        cmake.definitions["ALICEVISION_REQUIRE_CERES_WITH_SUITESPARSE"] = "OFF" # ASE to valid
        cmake.definitions["AV_BUILD_POPSIFT"] = "ON" if self.options.with_popsift else "OFF"
        cmake.definitions["AV_BUILD_OPENGV"] = "OFF"  # ASE to valid
        cmake.definitions["ALICEVISION_USE_CUDA"] = "ON" if self.options.with_cuda else "OFF"

        if not tools.os_info.is_windows:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = True

        cmake.configure(build_folder=self._build_subfolder)
        cmake.build()
        cmake.install()

    def package_info(self):
    
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
        
        self.cpp_info.names["cmake_find_package"] = "alicevision"
        self.cpp_info.names["cmake_find_package_multi"] = "alicevision"
        self.cpp_info.includedirs = [os.path.join(self.package_folder,"include","alicevision"), 
                                     os.path.join(self.package_folder,"include","alicevision","lib")]
        self.cpp_info.libdirs = [os.path.join(self.package_folder,"lib","alicevision")]
        
        if self.options.with_cuda and self.settings.compiler == 'Visual Studio':
            cuda_platform = {'x86': 'Win32',
                             'x86_64': 'x64'}.get(str(self.settings.arch))
            cuda_path = os.environ.get('CUDA_PATH')
            self.cpp_info.libdirs.append(os.path.join(cuda_path, "lib", cuda_platform))
                        
        self.cpp_info.libs = tools.collect_libs(self)


#    def package(self):
#        
#        if self.settings.os == 'Android':
#            if not self.options.shared:
#                self.cpp_info.includedirs.append(
#                    os.path.join('sdk', 'native', 'jni', 'include'))
#                self.cpp_info.libdirs.append(
#                    os.path.join('sdk', 'native', 'staticlibs', self._android_arch))


