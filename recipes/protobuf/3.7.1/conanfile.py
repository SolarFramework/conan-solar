#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from conans import ConanFile, CMake, tools


class ProtobufConan(ConanFile):
    name = "protobuf"
    upstream_version = "3.7.1"
    package_revision = ""
    version = "{0}{1}".format(upstream_version, package_revision)

    url = "https://github.com/Solar-Framework/conan-solar/recipes/protobuf/3.7.1"
    homepage = "https://github.com/protocolbuffers/protobuf"
    topics = ("conan", "protobuf", "protocol-buffers", "protocol-compiler", "serialization", "rpc")
    description = "Protocol Buffers - Google's data interchange format"
    license = "BSD-3-Clause"
    exports_sources = [
        "patches/protoc.cmake.patch"
    ]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    source_subfolder = "source_subfolder"
    short_paths = True

    def configure(self):
        if 'CI' not in os.environ:
            os.environ["CONAN_SYSREQUIRES_MODE"] = "verify"

    def requirements(self):
        self.requires("common/1.0.2@conan-solar/stable")
        if tools.os_info.is_windows:
            self.requires("zlib/1.2.11@conan-solar/stable")

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.upstream_version))
        extracted_dir = self.name + "-" + self.upstream_version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        proto_source_dir = os.path.join(self.source_folder, self.source_subfolder)
        tools.patch(proto_source_dir, "patches/protoc.cmake.patch")

        # Import common flags and defines
        import common

        # Generate Cmake wrapper
        common.generate_cmake_wrapper(
            cmakelists_path='CMakeLists.txt',
            source_subfolder=self.source_subfolder + '/cmake',
            build_type=self.settings.build_type
        )

        cmake = CMake(self, set_cmake_flags=True)

        cmake.definitions["protobuf_BUILD_TESTS"] = False
        cmake.definitions["protobuf_WITH_ZLIB"] = True

        # To avoid protoc plugin dependencies hell, we force a static build.
        # This is the only way to be able to build correctly grpc as the grpc plugin
        # is linked with protobuf libraries and other libraries, launch protoc
        cmake.definitions["protobuf_BUILD_SHARED_LIBS"] = False
        cmake.definitions["protobuf_MSVC_STATIC_RUNTIME"] = False

        if not tools.os_info.is_windows:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON"

        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        if tools.os_info.is_windows:
            self.copy("*.dll", dst="bin", src=self.deps_cpp_info["zlib"].bin_paths[0])

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs.sort(reverse=True)
