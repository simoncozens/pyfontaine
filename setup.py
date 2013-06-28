#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# fontaine.py
#
# Copyright (c) 2013,
# Виталий Волков <hash.3g@gmail.com>
# Dave Crossland <dave@understandinglimited.com>
#
# Released under the GNU General Public License version 3 or later.
# See accompanying LICENSE.txt file for details.

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='fontaine',
    version='1.0.1',
    description='Fontaine font tool',
    long_description = open("README.md").read(),
    author='Dave Crossland, Виталий Волков',
    author_email='dave@lab6.com',
    url='https://github.com/davelab6/pyfontaine',
    # more examples here http://docs.python.org/distutils/examples.html#pure-python-distribution-by-package
    packages=['fontaine', 'fontaine.charmaps', 'fontaine.structures',],
    license = "GNU GPL",
    requires=[
      'freetype',
      'lxml'
    ],
    package_data = {
        'fontaine': [
            'charmaps/names.db/*.*',
        ]
    }
)