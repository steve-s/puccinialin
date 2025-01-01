from __future__ import annotations

import platform
import sys
import sysconfig
import typing

# Known supported rustup targets from https://rust-lang.github.io/rustup/installation/other.html#manual-installation
rustup_targets = [
    "aarch64-apple-darwin",
    "aarch64-linux-android",
    "aarch64-pc-windows-msvc",
    "aarch64-unknown-linux-gnu",
    "aarch64-unknown-linux-musl",
    "arm-linux-androideabi",
    "arm-unknown-linux-gnueabi",
    "arm-unknown-linux-gnueabihf",
    "armv7-linux-androideabi",
    "armv7-unknown-linux-gnueabihf",
    "i686-apple-darwin",
    "i686-linux-android",
    "i686-pc-windows-gnu",
    "i686-pc-windows-msvc",
    "i686-unknown-linux-gnu",
    "loongarch64-unknown-linux-gnu",
    "loongarch64-unknown-linux-musl",
    "mips-unknown-linux-gnu",
    "mips64-unknown-linux-gnuabi64",
    "mips64el-unknown-linux-gnuabi64",
    "mipsel-unknown-linux-gnu",
    "powerpc-unknown-linux-gnu",
    "powerpc64-unknown-linux-gnu",
    "powerpc64le-unknown-linux-gnu",
    "s390x-unknown-linux-gnu",
    "x86_64-apple-darwin",
    "x86_64-linux-android",
    "x86_64-pc-windows-gnu",
    "x86_64-pc-windows-msvc",
    "x86_64-unknown-freebsd",
    "x86_64-unknown-illumos",
    "x86_64-unknown-linux-gnu",
    "x86_64-unknown-linux-musl",
    "x86_64-unknown-netbsd",
]


def get_triple(file: typing.IO) -> str:
    """Attempt to infer the rustc (and thereby rustup) target triple from SOABI.

    There are many different variables in Python that all return some platform information. `SOABI` is the tag of the
    shared library of native modules, which should match the binaries that we build on the rust side. For other
    platforms, we may need to query additional fields."""
    soabi = sysconfig.get_config_var("SOABI")
    if soabi:
        print(f"Python reports SOABI: {soabi}", file=file)
        if soabi.count("-") == 1:
            _python, platform = soabi.split("-", maxsplit=2)
        else:
            _python_interpreter, _python_version, platform = soabi.split(
                "-", maxsplit=2
            )
    else:
        # Older windows doesn't have SOABI
        platform = sysconfig.get_platform()
        print(f"Python reports platform: {platform}", file=file)

    # Linux
    if "-linux-" in platform:
        try:
            arch, linux, libc = platform.split("-")
        except ValueError:
            print(f"Unrecognized linux platform {platform}", file=file)
            sys.exit(1)
        if not linux == "linux":
            print(f"Unrecognized linux platform {platform}", file=file)
            sys.exit(1)
        target = f"{arch}-unknown-{linux}-{libc}"
    # macOS Intel
    elif platform == "darwin":
        target = "x86_64-apple-darwin"
    # macOS ARM
    elif platform == "darwin_arm64":
        target = "aarch64-apple-darwin"
    # Windows x86_64
    elif platform in ["win-amd64", "win_amd64"]:
        target = "x86_64-pc-windows-msvc"
    # Windows x86
    elif platform == "win32":
        target = "i686-pc-windows-msvc"
    else:
        print(f"Unsupported platform: {platform}", file=file)
        sys.exit(1)
    print(f"Computed rustc target triple: {target}", file=file)

    if target not in rustup_targets:
        print(f"Target triple not supported by rustup: {target}", file=file)
        sys.exit(1)

    return target


class Target:
    system: str

    def __init__(self, file: typing.IO):
        self.system = platform.system()

    def is_windows(self):
        return platform.system() == "Windows"

    def exe_suffix(self):
        """Return the suffix of an executable file.

        `.exe` on windows, `` on unix.

        Equivalent to `std::env::consts::EXE_SUFFIX` in rust.
        """
        if platform.system() == "Windows":
            return ".exe"
        else:
            return ""

    def env_path_separator(self):
        """Return the separator used in the PATH environment variable.

        `;` on windows, `:` on unix.
        """
        if platform.system() == "Windows":
            return ";"
        else:
            return ":"
