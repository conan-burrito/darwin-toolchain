from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version

import os
import copy


# Adapted from https://github.com/theodelrieu/conan-darwin-toolchain 1.0.8
class DarwinToolchainConan(ConanFile):
    name = "darwin-toolchain"
    license = "Apple"
    settings = 'os', 'arch', 'build_type', 'os_build', 'compiler'
    options = {'bitcode': [True, False], 'with_arc': [True, False], 'hidden_visibility': [True, False]}
    default_options = 'bitcode=True', 'with_arc=True', 'hidden_visibility=True'
    description = 'Darwin toolchain to (cross) compile macOS/iOS/watchOS/tvOS'
    url = 'https://github.com/conan-burrito/darwin-toolchain'
    build_policy = 'missing'

    # This file will be included by conan CMake build helper by setting the CONAN_CMAKE_TOOLCHAIN_FILE environment
    # variable
    exports_sources = 'darwin-toolchain.cmake'

    @property
    def cmake_system_name(self):
        if self.settings.os == "Macos":
            return "Darwin"

        return str(self.settings.os)

    @property
    def cmake_system_processor(self):
        return {"x86": "i386",
                "x86_64": "x86_64",
                "armv7": "arm",
                "armv8": "aarch64"}.get(str(self.settings.arch))

    def config_options(self):
        # build_type is only useful for bitcode
        if self.settings.os == "Macos":
            del self.settings.build_type
            del self.options.bitcode

    def configure(self):
        # We may export recipes on a Linux machine, thus we have to rely on os_build and not sys.platform
        if self.settings.os_build != "Macos":
            raise ConanInvalidConfiguration("Build machine must be Macos")
        if not tools.is_apple_os(self.settings.os):
            raise ConanInvalidConfiguration("os must be an Apple os")
        if self.settings.os in ["watchOS", "tvOS"] and not self.options.bitcode:
            raise ConanInvalidConfiguration("bitcode is required on watchOS/tvOS")
        if self.settings.os == "watchOS" and self.settings.arch not in ["armv7k", "armv8", "x86", "x86_64"]:
            raise ConanInvalidConfiguration("watchOS: Only supported archs: [armv7k, armv8, x86, x86_64]")

    def package(self):
        self.copy("darwin-toolchain.cmake")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        darwin_arch = tools.to_apple_arch(self.settings.arch)

        if self.settings.os == "watchOS" and self.settings.arch == "armv8":
            darwin_arch = "arm64_32"

        xcrun = tools.XCRun(self.settings)
        sysroot = xcrun.sdk_path

        self.cpp_info.sysroot = sysroot

        common_flags = ["-isysroot%s" % sysroot]

        if self.settings.get_safe("os.version"):
            sdk = self.settings.get_safe('os.sdk')
            subsystem = self.settings.get_safe('os.subsystem')
            common_flags.append(tools.apple_deployment_target_flag(self.settings.os, self.settings.os.version, sdk, subsystem, self.settings.arch))

        if self.settings.os != "Macos":
            if self.options.bitcode:
                if self.settings.build_type == "Debug":
                    bitcode_flag = "-fembed-bitcode-marker"
                else:
                    bitcode_flag = "-fembed-bitcode"
                common_flags.append(bitcode_flag)

        if self.options.with_arc:
            common_flags.append('-fobjc-arc')
            self.env_info.CONAN_CMAKE_WITH_ARC = 'YES'
        else:
            common_flags.append('-fno-objc-arc')
            self.env_info.CONAN_CMAKE_WITH_ARC = 'NO'

        if self.options.hidden_visibility:
            common_flags.extend(['-fvisibility=hidden', '-fvisibility-inlines-hidden'])
            self.env_info.CONAN_CMAKE_HIDDEN_VISIBILITY = 'YES'
        else:
            self.env_info.CONAN_CMAKE_HIDDEN_VISIBILITY = 'NO'

        # https://forum.juce.com/t/error-building-ios-for-device-in-release-mode/28595/5
        # https://github.com/facebook/rocksdb/issues/4064
        if self.settings.os == 'iOS' and Version(self.settings.os.version) < Version(11):
            common_flags.append('-fno-aligned-allocation')

        # CMake issue, for details look https://github.com/conan-io/conan/issues/2378
        cflags = copy.copy(common_flags)
        cflags.extend(["-arch", darwin_arch])
        cxxflags = copy.copy(cflags)
        self.cpp_info.cflags = cflags
        self.cpp_info.cxxflags = cxxflags

        link_flags = copy.copy(common_flags)
        link_flags.append("-arch %s" % darwin_arch)
        self.cpp_info.sharedlinkflags.extend(link_flags)
        self.cpp_info.exelinkflags.extend(link_flags)

        # Set flags in environment too, so that CMake Helper finds them
        cflags_str = " ".join(cflags)
        cxxflags_str = " ".join(cxxflags)
        ldflags_str = " ".join(link_flags)

        self.env_info.CC = xcrun.cc
        self.env_info.CPP = "%s -E" % xcrun.cc
        self.env_info.CXX = xcrun.cxx
        self.env_info.AR = xcrun.ar
        self.env_info.RANLIB = xcrun.ranlib
        self.env_info.STRIP = xcrun.strip

        self.env_info.CFLAGS = cflags_str
        self.env_info.ASFLAGS = cflags_str
        self.env_info.ASMFLAGS = cflags_str
        self.env_info.CPPFLAGS = cflags_str
        self.env_info.CXXFLAGS = cxxflags_str
        self.env_info.LDFLAGS = ldflags_str

        self.env_info.CONAN_CMAKE_SYSTEM_NAME = self.cmake_system_name
        if self.settings.get_safe("os.version"):
            self.env_info.CONAN_CMAKE_OSX_DEPLOYMENT_TARGET = str(self.settings.os.version)
        self.env_info.CONAN_CMAKE_OSX_ARCHITECTURES = str(darwin_arch)
        self.env_info.CONAN_CMAKE_OSX_SYSROOT = sysroot
        self.env_info.CONAN_CMAKE_SYSTEM_PROCESSOR = self.cmake_system_processor
        self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = os.path.join(self.package_folder, "darwin-toolchain.cmake")

        self.output.info('cxxflags: %s' % self.cpp_info.cxxflags)
        self.output.info('ldflags: %s' % self.cpp_info.sharedlinkflags)
