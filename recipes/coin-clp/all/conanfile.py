from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os
import shutil

required_conan_version = ">=1.33.0"


class CoinClpConan(ConanFile):
    name = "coin-clp"
    description = "COIN-OR Linear Programming Solver"
    version = "1.17.6"
    topics = ("clp", "simplex", "solver", "linear", "programming")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coin-or/Clp"
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
        self.requires("coin-osi/0.108.6@conan-solar/stable")

    # def validate(self):
        # if self.settings.os == "Windows" and self.options.shared:
            # raise ConanInvalidConfiguration("coin-clp does not support shared builds on Windows")
        # # FIXME: This issue likely comes from very old autotools versions used to produce configure.
        # if hasattr(self, "settings_build") and tools.cross_building(self) and self.options.shared:
            # raise ConanInvalidConfiguration("coin-clp shared not supported yet when cross-building")

    # def build_requirements(self):
        # self.build_requires("gnu-config/cci.20201022")
        # if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            # self.build_requires("msys2/cci.latest")
        # if self.settings.compiler == "Visual Studio":
            # self.build_requires("automake/1.16.4")

    # def source(self):
        # tools.get(**self.conan_data["sources"][self.version],
                  # destination=self._source_subfolder, strip_root=True)
                  
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("Clp-releases-{}".format(self.version), self._source_subfolder)

    # @contextmanager
    # def _build_context(self):
        # if self.settings.compiler == "Visual Studio":
            # with tools.vcvars(self.settings):
                # env = {
                    # "CC": "{} cl -nologo".format(tools.unix_path(self._user_info_build["automake"].compile)),
                    # "CXX": "{} cl -nologo".format(tools.unix_path(self._user_info_build["automake"].compile)),
                    # "LD": "{} link -nologo".format(tools.unix_path(self._user_info_build["automake"].compile)),
                    # "AR": "{} lib".format(tools.unix_path(self._user_info_build["automake"].ar_lib)),
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
        # ]
        # if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) >= 12:
            # self._autotools.flags.append("-FS")
        # self._autotools.configure(self._source_subfolder, args=configure_args)
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
        # # Installation script expects include/coin to already exist
        # tools.mkdir(os.path.join(self.package_folder, "include", "coin"))
        # with self._build_context():
            # autotools = self._configure_autotools()
            # autotools.install(args=["-j1"]) # due to configure generated with old autotools version

        # tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        # tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        # tools.rmdir(os.path.join(self.package_folder, "share"))
        # if self.settings.compiler == "Visual Studio":
            # for l in ("Clp", "ClpSolver", "OsiClp"):
                # tools.rename(os.path.join(self.package_folder, "lib", "lib{}.a").format(l),
                             # os.path.join(self.package_folder, "lib", "{}.lib").format(l))
                             
    def package(self):
        if self.settings.os == 'Android':
            if not self.options.shared:
                self.cpp_info.includedirs.append(
                    os.path.join('sdk', 'native', 'jni', 'include'))
                self.cpp_info.libdirs.append(
                    os.path.join('sdk', 'native', 'staticlibs', self._android_arch))

    def package_info(self):
        # self.cpp_info.components["clp"].libs = ["ClpSolver", "Clp"]
        # self.cpp_info.components["clp"].includedirs.append(os.path.join("include", "coin"))
        # self.cpp_info.components["clp"].names["pkg_config"] = "clp"
        # self.cpp_info.components["clp"].requires = ["coin-utils::coin-utils"]

        # self.cpp_info.components["osi-clp"].libs = ["OsiClp"]
        # self.cpp_info.components["osi-clp"].names["pkg_config"] = "osi-clp"
        # self.cpp_info.components["osi-clp"].requires = ["clp", "coin-osi::coin-osi"]

        # bin_path = os.path.join(self.package_folder, "bin")
        # self.output.info("Appending PATH environment variable: {}".format(bin_path))
        # self.env_info.PATH.append(bin_path)
        
        self.cpp_info.names["cmake_find_package"] = "clp"
        self.cpp_info.names["cmake_find_package_multi"] = "clp"
        self.cpp_info.includedirs.append(os.path.join("include", "coin"))
        self.cpp_info.libdirs = [os.path.join(self.package_folder,"lib")]
        self.cpp_info.libs = tools.collect_libs(self)
