from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.29.1"


class ColmapConan(ConanFile):
    name = "popsift"
    license = "MPL v2 license"
    homepage = "https://github.com/alicevision/popsift/"
    description = "open-source implementation of the SIFT algorithm in CUDA"
    url = "https://github.com/Solar-Framework/conan-solar/recipes/popsift/1.0.0"
    topics = ("computer-vision", "image-processing")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    exports_sources = ["CMakeLists.txt", "patches/**"]
    source_subfolder = "source_subfolder"
    generators = "cmake", "cmake_find_package"
    _cmake = None

    def configure(self):
        # it is also necessary to remove the VS runtime
        if self.settings.compiler == "Visual Studio":
            del self.settings.compiler.runtime

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("popsift-{}".format(self.version), self.source_subfolder)

    @property
    def _android_arch(self):
        arch = str(self.settings.arch)
        return tools.to_android_abi(arch)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        popsift_source_dir = os.path.join(self.source_folder, "source_subfolder")

        cmake = CMake(self)

        if self.options.shared :
            cmake.definitions["BUILD_SHARED_LIBS"] = 'ON'
        else :
            cmake.definitions["BUILD_SHARED_LIBS"] = 'OFF'

        cmake.definitions["PopSift_BUILD_EXAMPLES"] = 'OFF'

        cmake.configure()
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

    def package(self):
        # Retrieve common helpers
# import common

        # Fix all hard coded path to conan package in all .cmake files
#        common.fix_conan_path(self, self.package_folder, '*.cmake')
        
        if self.settings.os == 'Android':
            if not self.options.shared:
                self.cpp_info.includedirs.append(
                    os.path.join('sdk', 'native', 'jni', 'include'))
                self.cpp_info.libdirs.append(
                    os.path.join('sdk', 'native', 'staticlibs', self._android_arch))


