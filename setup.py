# -*- coding: utf-8 -*-
##j## BOF

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

def get_version():
#
	"""
Returns the version currently in development.

:return: (str) Version string
:since:  v0.1.01
	"""

	return "v0.1.01"
#

from dNG.distutils.command.build_py import BuildPy
from dNG.distutils.temporary_directory import TemporaryDirectory

from distutils.core import setup
from os import path

with TemporaryDirectory(dir = ".") as build_directory:
#
	parameters = { "pyRfcBasicsVersion": get_version() }

	BuildPy.set_build_target_path(build_directory)
	BuildPy.set_build_target_parameters(parameters)

	_build_path = path.join(build_directory, "src")

	setup(name = "RFC basics for Python",
	      version = get_version(),
	      description = "Easy to use and RFC compliant methods",
	      long_description = """RFC Basics is a Python module intended to implement missing RFC standards used for different purposes.""",
	      author = "direct Netware Group",
	      author_email = "web@direct-netware.de",
	      license = "MPL2",
	      url = "https://www.direct-netware.de/redirect?py;rfc_basics",

	      package_dir = { "": _build_path },
	      packages = [ "dNG" ],

	      data_files = [ ( "docs", [ "LICENSE", "README" ]) ],

	      # Override build_py to first run builder.py over all PAS modules
	      cmdclass = { "build_py": BuildPy }
	)
#

##j## EOF