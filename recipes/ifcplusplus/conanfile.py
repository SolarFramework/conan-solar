from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir, mkdir
import os


class IfcPlusPlusConan(ConanFile):
    name = "ifcplusplus"
    version = "2.5.0"
    description = (
        "Open source C++ class model, reader and writer for IFC files in STEP format. "
        "Features smart pointer memory management and parallel reader for multi-core CPUs."
    )
    license = "MIT"
    url = "https://github.com/ifcquery/ifcplusplus"
    homepage = "https://github.com/ifcquery/ifcplusplus"
    topics = ("ifc", "bim", "step", "building", "geometry")

    package_type = "static-library"  # add_library(IfcPlusPlus STATIC ...) est hardcode
    settings = "os", "compiler", "build_type", "arch"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(
            self,
            url="https://github.com/ifcquery/ifcplusplus/archive/refs/tags/2.5.tar.gz",
            destination=self.source_folder,
            strip_root=True,
        )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_VIEWER_APPLICATION"] = False
        tc.variables["BUILD_CONSOLE_APPLICATION"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

        cmake = CMake(self)
        cmake.install()

        # Le CMakeLists.txt upstream installe le .lib dans bin/ (ARCHIVE DESTINATION bin)
        # On le recopie dans lib/ pour respecter les conventions Conan
        src_bin = os.path.join(self.package_folder, "bin")
        dst_lib = os.path.join(self.package_folder, "lib")
        mkdir(self, dst_lib)
        copy(self, "*.lib", src=src_bin, dst=dst_lib)
        copy(self, "*.a",   src=src_bin, dst=dst_lib)
        rmdir(self, src_bin)
        rmdir(self, os.path.join(self.package_folder, "share"))

        # Les includes external sont declares PRIVATE dans le CMake upstream
        # donc non installes automatiquement — on les copie manuellement en une passe
        src_ext = os.path.join(self.source_folder, "IfcPlusPlus", "src", "external")
        dst_ext = os.path.join(self.package_folder, "include", "external")
        # Tout copier d'un coup en preservant la structure
        copy(self, "*.h",   src=src_ext, dst=dst_ext, keep_path=True)
        copy(self, "*.hpp", src=src_ext, dst=dst_ext, keep_path=True)
        copy(self, "*.inl", src=src_ext, dst=dst_ext, keep_path=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "IFCPP::IfcPlusPlus")
        # DEBUG_POSTFIX "d" est defini dans le CMakeLists.txt upstream :
        # Debug  -> IfcPlusPlusd.lib
        # Release -> IfcPlusPlus.lib
        if self.settings.build_type == "Debug":
            self.cpp_info.libs = ["IfcPlusPlusd"]
        else:
            self.cpp_info.libs = ["IfcPlusPlus"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = [
            "include",                                  # src/ifcpp (installe par cmake.install)
            "include/ifcpp/IFC4X3/include",
            "include/external",                         # utf8.h racine
            "include/external/glm",                     # glm (via #include <glm/glm.hpp>)
            "include/external/Carve/src/include",       # carve/*.h
            "include/external/RapidJSON",               # rapidjson/*.h
            "include/external/utf8",                    # utf8/*.h
            "include/external/zip-master",              # zip.h
        ]

        # Defines necessaires cote consommateur pour linker en statique
        self.cpp_info.defines = [
            "IFCQUERY_STATIC_LIB",
            "_HAS_AUTO_PTR_ETC=1",
            "UNICODE",
            "_UNICODE",
        ]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["Bcrypt"]
        elif self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread"]
