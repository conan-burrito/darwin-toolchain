if ((CMAKE_MAJOR_VERSION GREATER_EQUAL 3) AND (CMAKE_MINOR_VERSION GREATER_EQUAL 14))
   # CMake 3.14 added support for Apple platform cross-building
   # Platform/CMAKE_SYSTEM_NAME.cmake will be called later
   # Those files have broken quite a lot of things
   set(CMAKE_SYSTEM_NAME $ENV{CONAN_CMAKE_SYSTEM_NAME})
else()
   set(CMAKE_SYSTEM_NAME Darwin)
endif()

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM BOTH)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE BOTH)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY BOTH)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE NEVER)

set(CMAKE_OSX_DEPLOYMENT_TARGET $ENV{CONAN_CMAKE_OSX_DEPLOYMENT_TARGET})
set(CMAKE_OSX_ARCHITECTURES $ENV{CONAN_CMAKE_OSX_ARCHITECTURES})
set(CMAKE_OSX_SYSROOT $ENV{CONAN_CMAKE_OSX_SYSROOT})

# Setting CMAKE_SYSTEM_NAME results it CMAKE_SYSTEM_VERSION not being set
# For some reason, it must be the Darwin version (otherwise Platform/Darwin.cmake will not set some flags)
# Most probably a CMake bug... (https://gitlab.kitware.com/cmake/cmake/issues/20036)
set(CMAKE_SYSTEM_VERSION "${CMAKE_HOST_SYSTEM_VERSION}")
set(CMAKE_SYSTEM_PROCESSOR "$ENV{CONAN_CMAKE_SYSTEM_PROCESSOR}")

# Burrito stuff
set(CMAKE_XCODE_ATTRIBUTE_CLANG_ENABLE_OBJC_ARC $ENV{CONAN_CMAKE_WITH_ARC})
set(CMAKE_XCODE_ATTRIBUTE_GCC_SYMBOLS_PRIVATE_EXTERN $ENV{CONAN_CMAKE_HIDDEN_VISIBILITY})

# iOS development requires valid signing identity, team ID and bundle identifiers.
# If you are starting fresh on a new Mac you will probably have to crate a dummy application
# in order for Team ID and a related certificates to be generated, see the following links
# for details:
# https://stackoverflow.com/questions/18727894/how-can-i-find-my-apple-developer-team-id-and-team-agent-apple-id/18727947#18727947
# https://polly.readthedocs.io/en/latest/toolchains/ios/errors/polly_ios_bundle_identifier.html
set(CMAKE_XCODE_ATTRIBUTE_CODE_SIGN_IDENTITY $ENV{CONAN_IOS_SIGN_IDENTITY})
set(CMAKE_XCODE_ATTRIBUTE_DEVELOPMENT_TEAM $ENV{CONAN_IOS_DEV_TEAM_ID})
set(MACOSX_BUNDLE_GUI_IDENTIFIER $ENV{CONAN_IOS_BUNDLE_GUI_IDENTIFIER})

# Otherwise FindPthread will fail
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)