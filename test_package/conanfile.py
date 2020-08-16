from conans.model.conan_file import ConanFile
from conans import CMake
import os


class Test(ConanFile):
    settings = 'os', 'compiler', 'arch', 'build_type'
    generators = 'cmake'

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        cmd = os.path.join('bin', 'ios-test')
        if self.settings.os != 'Macos':
            # Ensure it fails
            try:
                self.run(cmd)
            except:
                pass
            else:
                raise Exception("Cross building failed!")
        else:
            self.run(cmd)