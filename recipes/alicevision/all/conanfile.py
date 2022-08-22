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
               "with_popsift": [True, False],
               "with_opengv": [True, False]
    }
    default_options = { "shared": False,
                        "with_cuda": False,
                        "with_popsift": False,
                        "with_opengv": False
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
        self.options['openimageio'].with_tbb = False

    def build(self):

        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"
        cmake.definitions["ALICEVISION_REQUIRE_CERES_WITH_SUITESPARSE"] = "OFF"
        cmake.definitions["AV_BUILD_POPSIFT"] = "ON" if self.options.with_popsift else "OFF"
        cmake.definitions["AV_BUILD_OPENGV"] = "ON" if self.options.with_opengv else "OFF"
        cmake.definitions["ALICEVISION_USE_CUDA"] = "ON" if self.options.with_cuda else "OFF"
        cmake.definitions["ALICEVISION_BUILD_DOC"] = "OFF"

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

    def requirements(self):

        self.requires("alembic/1.8.3")
        self.requires("boost/1.76.0")
        self.requires("eigen/3.4.0")
        self.requires("ceres-solver/2.0.0")
        self.requires("flann/1.9.1@conan-solar/stable")
        self.requires("openexr/2.5.7")
        self.requires("openimageio/2.3.13.0@conan-solar/boost_1_76")
        self.requires("geogram/1.7.7@conan-solar/stable")
        self.requires("zlib/1.2.12")
        if self.options.with_popsift :
            self.requires("popsift/1.0.0-rc3@conan-solar/stable")
        if self.options.with_opengv :
            self.requires("opengv/master")
        self.requires("coin-utils/2.11.4@conan-solar/stable")
        self.requires("coin-osi/0.108.6@conan-solar/stable")
        self.requires("coin-clp/1.17.6@conan-solar/stable")

