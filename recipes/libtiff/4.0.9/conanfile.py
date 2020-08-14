#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import CMake, ConanFile, tools


class LibtiffConan(ConanFile):
    name = "libtiff"
    package_revision = ""
    upstream_version = "4.0.9"
    version = "{0}{1}".format(upstream_version, package_revision)

    description = "Library for Tag Image File Format (TIFF)"
    generators = "cmake"
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    exports = [
        "patches/add-component-options.patch",
        "patches/crt-secure-no-deprecate.patch",
        "patches/fix-cxx-shared-libs.patch"
    ]
    url = "https://github.com/Solar-Framework/conan-solar/recipes/libtiff/4.0.9"
    source_subfolder = "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("common/1.0.2@conan-solar/stable")
        if tools.os_info.is_windows:
            self.requires("zlib/1.2.11@conan-solar/stable")

    def source(self):
        tools.get("http://download.osgeo.org/libtiff/tiff-{0}.zip".format(self.upstream_version))
        os.rename('tiff-' + self.upstream_version, self.source_subfolder)

    def build(self):
        libtiff_source_dir = os.path.join(self.source_folder, self.source_subfolder)
        tools.patch(libtiff_source_dir, "patches/add-component-options.patch")
        tools.patch(libtiff_source_dir, "patches/crt-secure-no-deprecate.patch")
        tools.patch(libtiff_source_dir, "patches/fix-cxx-shared-libs.patch")

        # Import common flags and defines
        import common

        # Generate Cmake wrapper
        common.generate_cmake_wrapper(
            cmakelists_path='CMakeLists.txt',
            source_subfolder=self.source_subfolder,
            build_type=self.settings.build_type
        )

        cmake = CMake(self)

        cmake.definitions["lzma"] = False
        cmake.definitions["jpeg"] = False
        cmake.definitions["BUILD_TOOLS"] = False
        cmake.definitions["BUILD_TESTS"] = False
        cmake.definitions["BUILD_CONTRIB"] = False
        cmake.definitions["BUILD_DOCS"] = False
        if not tools.os_info.is_windows:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON"

        cmake.configure()
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if tools.os_info.is_linux:
            self.cpp_info.libs.append("m")
