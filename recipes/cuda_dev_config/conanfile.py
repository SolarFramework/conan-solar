#!/usr/bin/env cuda
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import os
import re

## somehow exporting does not provide access to package options
# so defining cuda_root only works with conan create, but not conan export ..
if tools.os_info.is_windows:
    CUDA_ROOT_DEFAULT = "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v11.3"
elif tools.os_info.is_linux:
    CUDA_ROOT_DEFAULT = "/usr/local/cuda-11.3"
else:
    raise RuntimeError("Unsupported Platform")


# pylint: disable=W0201
class CUDADevConfigConan(ConanFile):
    name = "cuda_dev_config"
    version = "1.1"
    description = "Configuration of CUDA SDK for use as a development dependency."
    url = "https://github.com/ulricheck/conan-cuda_dev_config"
    author = "Ulrich Eck <ulrich.eck@tum.de>"
    options = { ""
                "cuda_version": ["11.3","11.2","11.1","11.0","10.2", "10.1", "10.0", "9.1", "9.0"],
        "cuda_root": "ANY",
        }
    default_options = (
        "cuda_version=11.3", 
        "cuda_root=%s" % CUDA_ROOT_DEFAULT,
        )
    settings = "os", "arch"
    build_policy = "missing"
    supportedVersions = ["11.3","11.2","11.1","11.0","10.2", "10.1", "10.0", "9.1", "9.0"]

    def package_id(self):
        self.info.header_only()
        self.info.options.cuda_version = self.cuda_version

    def package_info(self):
        if self.have_cuda_dev:
            self.cpp_info.bindirs = [self.cuda_bindir,]
            self.user_info.cuda_version = self.cuda_version
            self.user_info.cuda_root = str(self.options.cuda_root)
            self.env_info.path.append(str(self.options.cuda_root))
            self.env_info.CUDA_SDK_ROOT_DIR = str(self.options.cuda_root)

    @property
    def have_cuda_dev(self):
        if not self.cuda_version:
            return False
        if not os.path.exists(os.path.join(self.get_cuda_path("include"), 'cuda.h')):
            return False
        return True

    @property
    def cuda_version(self):

					
        if not hasattr(self, '_cuda_version'):
            cmd = "--version"
            result = self.run_nvcc_command(cmd)
            match = re.match( r".*, (\w+) ({}).*".format( self.options.cuda_version ), result.splitlines()[3])
            self._cuda_version = None
            if match:
                vt, version = match.groups()
                if vt == 'release':
                    self._cuda_version = version
                    self.output.info("Found CUDA SDK: %s" % self._cuda_version)
            else:
                self.output.info("Invalid response from calling nvcc --version: %r" % result)
        return self._cuda_version

    @property
    def cuda_bindir(self):
        return self.get_cuda_path("bin")

    def get_cuda_path(self, dir_name):
        if tools.os_info.is_windows and not os.path.exists(str(self.options.cuda_root)):
            default_path = "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v{}"
            for version in self.supportedVersions:
                cudaPath = default_path.format(version)
                if os.path.exists(cudaPath):
                    self.options.cuda_root = cudaPath
                    break
        return os.path.join(str(self.options.cuda_root), dir_name)

    def run_nvcc_command(self, cmd):
        nvcc_executable = os.path.join(self.cuda_bindir, "nvcc")
        output = StringIO()
        self.output.info('running command: "{0}" {1}'.format(nvcc_executable, cmd))
        self.run('"{0}" {1}'.format(nvcc_executable, cmd), output=output)
        result = output.getvalue().strip()
        return result if result and result != "" else None
