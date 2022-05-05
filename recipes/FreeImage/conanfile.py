#https://github.com/p-brz/freeimage-conan
from conans import ConanFile, CMake, AutoToolsBuildEnvironment, tools
from conans.tools import download, check_sha256, unzip, replace_in_file
from conans.tools import Version
import os
from os import path
from shutil import copy, copyfile, rmtree

required_conan_version = ">=1.29.1"

class FreeimsageConan(ConanFile):
    name    = "FreeImage"
    license = "FIPL(http://freeimage.sourceforge.net/freeimage-license.txt)", "GPLv2", "GPLv3"
    homepage = "https://freeimage.sourceforge.io/"
    description = "Open source image loading library"
    url     = "https://github.com/Solar-Framework/conan-solar/recipes/FreeImage/3.18.0"
    topics = ("computer-vision", "image-processing")
    settings = "os", "compiler", "build_type", "arch"
    #version = "3.18.0"
    options = {
        "shared"          : [True, False],
        "use_cxx_wrapper" : [True, False],
        # if set, build library without "version number" (eg.: not generate libfreeimage-3-17.0.so)
        "no_soname"       : [True, False]
    }
    default_options = (
        "shared=False",
        "use_cxx_wrapper=True",
        "no_soname=False"
    )
    exports_sources = ("CMakeLists.txt", "*.h", "FreeImage/*", "patches/*")
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    generators = "cmake", "cmake_multi", "cmake_paths", "cmake_find_package"
    short_paths = True
        
    #Downloading from sourceforge
    #REPO = "http://downloads.sourceforge.net/project/freeimage/"
    #DOWNLOAD_LINK = REPO + "Source%20Distribution/3.18.0/FreeImage3180.zip"
    #Folder inside the zip
    #SRCDIR = _source_subfolder
    #FILE_SHA = 'f41379682f9ada94ea7b34fe86bf9ee00935a3147be41b6569c9605a53e438fd'
    
    def requirements(self):
        self.requires ("zlib/1.2.12")
        self.requires ("libpng/1.6.37")
        #self.requires ("libjpeg/9d") #vcpkg use libjpeg-turbo-2.0.6
        #self.requires ("libjpeg-turbo/2.0.6")
        self.requires ("libtiff/4.2.0") #vcpkg use 4.1.0
        self.requires ("openjpeg/2.3.1@conan-solar/stable")
        self.requires ("libwebp/1.1.0")
        self.requires ("libraw/0.19.5") #vcpkg use 201903-3
        self.requires ("jxrlib/v2019.10.9@conan-solar/stable") # vcpkg use 2019.10.9
        self.requires ("openexr/2.3.0@conan-solar/stable") # vcpkg 2.5.0            

    def configure(self):
        if self.settings.os == "Android":
            self.options.no_soname = True

        if self.settings.compiler == "Visual Studio":
            self.options.use_cxx_wrapper = False

    def source(self):
        self.download_source()
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        #for patch in self.conan_data["patches"].get(self.version, []):
            #tools.patch(**patch)
        # self.apply_patches()
        
        #os.remove(

    def download_source(self):
        # zip_name = self.name + ".zip"
        # download(self.DOWNLOAD_LINK, zip_name)
        # check_sha256(zip_name, self.FILE_SHA)
        # unzip(zip_name)
        # os.unlink(zip_name)
        
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name, self._source_subfolder)
        
        # This is not strictly necessary, but to make sure
        # that no "internal" libraries are used we remove them
        rmtree(os.path.join(self._source_subfolder, "Source/LibJPEG"), ignore_errors=True)
        rmtree(os.path.join(self._source_subfolder, "Source/LibPNG"), ignore_errors=True)
        rmtree(os.path.join(self._source_subfolder, "Source/LibTIFF4"), ignore_errors=True)
        rmtree(os.path.join(self._source_subfolder, "Source/Zlib"), ignore_errors=True)
        rmtree(os.path.join(self._source_subfolder, "Source/LibOpenJPEG"), ignore_errors=True)
        rmtree(os.path.join(self._source_subfolder, "Source/LibJXR"), ignore_errors=True)
        rmtree(os.path.join(self._source_subfolder, "Source/LibWebP"), ignore_errors=True)
        rmtree(os.path.join(self._source_subfolder, "Source/LibRawLite"), ignore_errors=True)
        rmtree(os.path.join(self._source_subfolder, "Source/OpenEXR"), ignore_errors=True)
        
    def build(self):
        if self.settings.compiler == "Visual Studio":
            self.build_visualstudio()
        else:
            self.build_visualstudio()

    def build_visualstudio(self):
        cmake = CMake(self)
        options = ''
        # cmake.configure(build_folder=self._build_subfolder)
        cmake.configure()
        cmake.build()
        cmake.install()

    def build_make(self):
        with tools.environment_append(self.make_env()):
            self.make_and_install()

    def make_and_install(self):
        options= "" if not self.options.use_cxx_wrapper else "-f Makefile.fip"

        make_cmd = "make %s" % (options)

        self.print_and_run(make_cmd               , cwd=self.SRCDIR)
        self.print_and_run(make_cmd + " install"  , cwd=self.SRCDIR)

    #def package(self):
        
        #cmake.configure()
        #cmake.install()        
        
    def package_info(self):

        #if self.options.use_cxx_wrapper:
        #    self.cpp_info.libs.append("freeimageplus")
        #else:
        #    self.cpp_info.libs      = ["freeimage"]
            
        #bindir = os.path.join(self.package_folder, "bin")
        bindir = self.package_folder
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        self.cpp_info.names["cmake_find_package"] = "FreeImage"
        self.cpp_info.names["cmake_find_package_multi"] = "FreeImage"
        self.cpp_info.includedirs = ["include", os.path.join("include","FreeImage")]
        #self.cpp_info.libs = ["FreeImage"]
        self.cpp_info.libs = tools.collect_libs(self)

    ################################ Helpers ######################################

    def print_and_run(self, cmd, **kw):
        cwd_ = "[%s] " % kw.get('cwd') if 'cwd' in kw else ''

        self.output.info(cwd_ + str(cmd))
        self.run(cmd, **kw)

    def make_env(self):
        env_build = AutoToolsBuildEnvironment(self)

        env = env_build.vars

        # AutoToolsBuildEnvironment sets CFLAGS and CXXFLAGS, so the default value
        # on the makefile is overwriten. So, we set here the default values again
        env["CFLAGS"] += " -O3 -fPIC -fexceptions -fvisibility=hidden"
        env["CXXFLAGS"] += " -O3 -fPIC -fexceptions -fvisibility=hidden -Wno-ctor-dtor-privacy"

        if self.options.shared: #valid only for modified makefiles
            env["BUILD_SHARED"] = "1"
        if self.settings.os == "Android":
            env["NO_SWAB"] = "1"
            env["ANDROID"] = "1"

            if not os.environ.get('ANDROID_NDK_HOME'):
                env['ANDROID_NDK_HOME'] = self.get_ndk_home()

        if self.options.no_soname:
            env["NO_SONAME"] = "1"

        if not hasattr(self, 'package_folder'):
            self.package_folder = "dist"

        env["DESTDIR"]    = self.package_folder
        env["INCDIR"]     = path.join(self.package_folder, "include")
        env["INSTALLDIR"] = path.join(self.package_folder, "lib")

        return env

    def get_ndk_home(self):
        android_toolchain_opt = self.options["android-toolchain"]
        android_ndk_info = self.deps_cpp_info["android-ndk"]
        if android_toolchain_opt and android_toolchain_opt.ndk_path:
            return android_toolchain_opt.ndk_path
        elif android_ndk_info:
            return android_ndk_info.rootpath

        self.output.warn("Could not find ndk home path")

        return None

    def apply_patches(self):
        self.output.info("Applying patches")

        #Copy "patch" files
        copy('CMakeLists.txt', self.SRCDIR)
        self.copy_tree("patches", self.SRCDIR)

        self.patch_android_swab_issues()
        self.patch_android_neon_issues()

        if self.settings.compiler == "Visual Studio":
            self.patch_visual_studio()

    def patch_android_swab_issues(self):
        librawlite = path.join(self.SRCDIR, "Source", "LibRawLite")
        missing_swab_files = [
            path.join(librawlite, "dcraw", "dcraw.c"),
            path.join(librawlite, "internal", "defines.h")
        ]
        replaced_include = '\n'.join(('#include <unistd.h>', '#include "swab.h"'))

        for f in missing_swab_files:
            self.output.info("patching file '%s'" % f)
            replace_in_file(f, "#include <unistd.h>", replaced_include)

    def patch_android_neon_issues(self):
        # avoid using neon
        libwebp_src = path.join(self.SRCDIR, "Source", "LibWebP", "src")
        rm_neon_files = [   path.join(libwebp_src, "dsp", "dsp.h") ]
        for f in rm_neon_files:
            self.output.info("patching file '%s'" % f)
            replace_in_file(f, "#define WEBP_ANDROID_NEON", "")

    def patch_visual_studio(self):
        replace_in_file(path.join(self.SRCDIR, 'Source/FreeImage/Plugin.cpp'), 's_plugins->AddNode(InitWEBP);', '')
        replace_in_file(path.join(self.SRCDIR, 'Source/FreeImage/Plugin.cpp'), 's_plugins->AddNode(InitJXR);', '')
        # snprintf was added in VS2015
        if self.settings.compiler.version >= 14:
            replace_in_file(path.join(self.SRCDIR, 'Source/LibRawLite/internal/defines.h'), '#define snprintf _snprintf', '')
            replace_in_file(path.join(self.SRCDIR, 'Source/ZLib/gzguts.h'), '#  define snprintf _snprintf', '')
            replace_in_file(path.join(self.SRCDIR, 'Source/LibTIFF4/tif_config.h'), '#define snprintf _snprintf', '')

    def copy_tree(self, src_root, dst_root):
        for root, dirs, files in os.walk(src_root):
            for d in dirs:
                dst_dir = path.join(dst_root, d)
                if not path.exists(dst_dir):
                    os.mkdir(dst_dir)

                self.copy_tree(path.join(root, d), dst_dir)

            for f in files:
                copyfile(path.join(root, f), path.join(dst_root, f))

            break
