# -*- coding: utf-8 -*-

"""
RFC basics for Python
Easy to use and RFC compliant methods
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?py;rfc_basics

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
setup.py
"""

from os import makedirs, path

try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup
#

try:
    from dNG.distutils.command.build_py import BuildPy
    from dNG.distutils.command.sdist import Sdist
    from dNG.distutils.temporary_directory import TemporaryDirectory
except ImportError:
    raise RuntimeError("'dng-builder-suite' prerequisite not matched")
#

def get_version():
    """
Returns the version currently in development.

:return: (str) Version string
:since:  v0.1.1
    """

    return "v1.0.0"
#

with TemporaryDirectory(dir = ".") as build_directory:
    parameters = { "pyRfcBasicsVersion": get_version() }

    BuildPy.set_build_target_path(build_directory)
    BuildPy.set_build_target_parameters(parameters)

    Sdist.set_build_target_path(build_directory)
    Sdist.set_build_target_parameters(parameters)

    makedirs(path.join(build_directory, "src", "dNG"))

    _setup = { "name": "dng-rfc-basics",
               "version": get_version()[1:],
               "description": "Easy to use and RFC compliant methods",
               "long_description": """RFC Basics is a Python module intended to implement missing RFC standards used for different purposes.""",
               "author": "direct Netware Group et al.",
               "author_email": "web@direct-netware.de",
               "license": "MPL2",
               "url": "https://www.direct-netware.de/redirect?py;rfc_basics",

               "platforms": [ "any" ],

               "packages": [ "dNG" ],

               "data_files": [ ( "docs", [ "LICENSE", "README" ]) ]
             }

    # Override build_py to first run builder.py
    _setup['cmdclass'] = { "build_py": BuildPy, "sdist": Sdist }

    setup(**_setup)
#
