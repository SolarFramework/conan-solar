import os
import shutil
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration

class cxsparsesolverConan(ConanFile):
    name = "cxsparse"
    filename = "CXSparse"
    license = "GNU Lesser General Public License"
    url = "https://github.com/Solar-Framework/conan-solar/recipes/cxsparse/3.1.1"
    homepage = "https://github.com/PetterS/CXSparse"
    description = ("A concise sparse Cholesky library.")
    topics = ("optimization","Non-linear Least Squares")
    settings = "os", "arch", "compiler", "build_type"
    generators = ["cmake", "cmake_find_package"]
    options = {"shared": [True, False]}
    default_options = "shared=False"
    exports_sources = ["CMakeLists.txt","patches/*"]
    

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
			
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename("%s-%s" % (self.filename, self.version), self._source_subfolder)

    def build(self):
        #Make sure that cmake finds gflags is use_gflags=True
        #tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
         #                     "find_package(Gflags)",
          #                    "find_package(Gflags REQUIRED)")
        #On windows the library names can be gflags.dll or gflags_static.lib
        #tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "FindGflags.cmake"),
        #                      "find_library(GFLAGS_LIBRARY NAMES gflags",
        #                      "find_library(GFLAGS_LIBRARY NAMES gflags gflags_static")
        cxsparse_source_dir = os.path.join(self.source_folder, "source_subfolder")
        shutil.copy("patches/CMakeLists.txt",
            os.path.join(cxsparse_source_dir, "CMakeLists.txt"))
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        if self.settings.os == "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON"
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("FindCXSparse.cmake", src="patches", dst=".", keep_path=False)
		
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        
        
