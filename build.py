from conan.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager(channel='stable')
    builder.add({
        'arch': 'armv8',
        'os': 'iOS',
        'os.version': '9.0',
        'compiler': 'apple-clang',
        'compiler.version': '10.0',
        'compiler.libcxx': 'libc++'
    }, {}, {}, {}, reference='darwin-toolchain/0.0.1')

    builder.run()
