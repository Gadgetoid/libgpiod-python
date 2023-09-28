# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: 2022 Bartosz Golaszewski <brgl@bgdev.pl>

import glob
from os import environ, path
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext as orig_build_ext
from shutil import rmtree


class build_ext(orig_build_ext):
    """
    setuptools install all C extentions even if they're excluded in setup().
    As a workaround - remove the tests directory right after all extensions
    were built (and possibly copied to the source directory if inplace is set).
    """

    def run(self):
        super().run()
        rmtree(path.join(self.build_lib, "tests"), ignore_errors=True)

try:
    with open("gpiod/version.py", "r") as fd:
        exec(fd.read())
except IOError:
    __version__ = open("libgpiod/NEWS", "r").readline()[10:].strip()

sources = [
        "gpiod/chip.cpp",
        "gpiod/iter.cpp",
        "gpiod/line_bulk.cpp",
        "gpiod/line.cpp",
        "libgpiod/bindings/python/gpiodmodule.c"
]

sources += glob.glob("libgpiod/lib/*.c")

gpiod_ext = Extension(
    "gpiod",
    sources=sources,
    define_macros=[("_GNU_SOURCE", "1")],
    include_dirs=["libgpiod/include", "libgpiod/lib", "gpiod"],
    extra_compile_args=["-Wall", "-Wextra", "-DGPIOD_VERSION_STR=\"{}\"".format(__version__)]
)

gpiosim_ext = Extension(
    "tests.gpiosim._ext",
    sources=["tests/gpiomockupmodule.c"],
    define_macros=[("_GNU_SOURCE", "1")],
    libraries=["gpiosim"],
    include_dirs=["include"],
    extra_compile_args=["-Wall", "-Wextra"],
)

extensions = [gpiod_ext]
if "GPIOD_WITH_TESTS" in environ and environ["GPIOD_WITH_TESTS"] == "1":
    extensions.append(gpiosim_ext)

setup(
    name="libgpiod",
    packages=find_packages(exclude=["tests", "tests.*"]),
    ext_modules=extensions,
    cmdclass={"build_ext": build_ext},
    version=__version__,
    author="Bartosz Golaszewski",
    author_email="brgl@bgdev.pl",
    description="Python bindings for libgpiod",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    platforms=["linux"],
    license="LGPLv2.1",
)
