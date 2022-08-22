from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os
import shutil

required_conan_version = ">=1.33.0"


class CoinOsiConan(ConanFile):
    name = "coin-osi"
    description = "COIN-OR Linear Programming Solver"
    version = "0.108.6"
    topics = ("clp", "simplex", "solver", "linear", "programming")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coin-or/Osi"
    license = ("EPL-2.0",)
    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    exports_sources = ["CMakeLists.txt", "patches/*"]
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    generators = "cmake", "cmake_find_package"
    short_paths = True

    _autotools = None

    # @property
    # def _source_subfolder(self):
        # return "source_subfolder"

    # @property
    # def _build_subfolder(self):
        # return "build_subfolder"

    # @property
    # def _settings_build(self):
        # return getattr(self, "settings_build", self.settings)

    # @property
    # def _user_info_build(self):
        # return getattr(self, "user_info_build", self.deps_user_info)

    # def config_options(self):
        # if self.settings.os == "Windows":
            # del self.options.fPIC

    # def configure(self):
        # if self.options.shared:
            # del self.options.fPIC

    def requirements(self):
        self.requires("coin-utils/2.11.4@conan-solar/stable")

    # def build_requirements(self):
        # self.build_requires("gnu-config/cci.20201022")
        # self.build_requires("pkgconf/1.7.4")
        # if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            # self.build_requires("msys2/cci.latest")

    # def validate(self):
        # if self.settings.os == "Windows" and self.options.shared:
            # raise ConanInvalidConfiguration("coin-osi does not support shared builds on Windows")
        # # FIXME: This issue likely comes from very old autotools versions used to produce configure.
        # if hasattr(self, "settings_build") and tools.cross_building(self) and self.options.shared:
            # raise ConanInvalidConfiguration("coin-osi shared not supported yet when cross-building")

    # def source(self):
        # tools.get(**self.conan_data["sources"][self.version],
                  # destination=self._source_subfolder, strip_root=True)
                  
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("Osi-releases-{}".format(self.version), self._source_subfolder)

    # @contextlib.contextmanager
    # def _build_context(self):
        # if self.settings.compiler == "Visual Studio":
            # with tools.vcvars(self):
                # env = {
                    # "CC": "cl -nologo",
                    # "CXX": "cl -nologo",
                    # "LD": "link -nologo",
                    # "AR": "lib",
                # }
                # with tools.environment_append(env):
                    # yield
        # else:
            # yield

    # def _configure_autotools(self):
        # if self._autotools:
            # return self._autotools
        # self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        # self._autotools.libs = []
        # yes_no = lambda v: "yes" if v else "no"
        # configure_args = [
            # "--enable-shared={}".format(yes_no(self.options.shared)),
            # "--without-blas"
            # "--without-lapack"
        # ]
        # if self.settings.compiler == "Visual Studio":
            # self._autotools.cxx_flags.append("-EHsc")
            # configure_args.append("--enable-msvc={}".format(self.settings.compiler.runtime))
            # if tools.Version(self.settings.compiler.version) >= 12:
                # self._autotools.flags.append("-FS")
        # self._autotools.configure(configure_dir=self._source_subfolder, args=configure_args)
        # return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    # os.path.join(self._source_subfolder, "config.sub"))
        # shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    # os.path.join(self._source_subfolder, "config.guess"))
        # with self._build_context():
            # autotools = self._configure_autotools()
            # autotools.make()
            
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build()
        cmake.install()

    # def package(self):
        # self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        # with self._build_context():
            # autotools = self._configure_autotools()
            # autotools.install(args=["-j1"]) # due to configure generated with old autotools version

        # tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

        # if self.settings.compiler == "Visual Studio":
            # for l in ("Osi", "OsiCommonTests"):
                # os.rename(os.path.join(self.package_folder, "lib", "lib{}.lib").format(l),
                          # os.path.join(self.package_folder, "lib", "{}.lib").format(l))

        # tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        # tools.rmdir(os.path.join(self.package_folder, "share"))
        
    def package(self):
        if self.settings.os == 'Android':
            if not self.options.shared:
                self.cpp_info.includedirs.append(
                    os.path.join('sdk', 'native', 'jni', 'include'))
                self.cpp_info.libdirs.append(
                    os.path.join('sdk', 'native', 'staticlibs', self._android_arch))

    def package_info(self):
        # self.cpp_info.components["libosi"].libs = ["Osi"]
        # self.cpp_info.components["libosi"].includedirs = [os.path.join("include", "coin")]
        # self.cpp_info.components["libosi"].requires = ["coin-utils::coin-utils"]
        # self.cpp_info.components["libosi"].names["pkg_config"] = "osi"

        # self.cpp_info.components["osi-unittests"].libs = ["OsiCommonTests"]
        # self.cpp_info.components["osi-unittests"].requires = ["libosi"]
        # self.cpp_info.components["osi-unittests"].names["pkg_config"] = "osi-unittests"
     
        self.cpp_info.names["cmake_find_package"] = "osi"
        self.cpp_info.names["cmake_find_package_multi"] = "osi"
        self.cpp_info.includedirs.append(os.path.join("include", "coin"))
        self.cpp_info.libdirs = [os.path.join(self.package_folder,"lib")]
        self.cpp_info.libs = tools.collect_libs(self)
