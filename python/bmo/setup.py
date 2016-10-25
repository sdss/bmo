#!/usr/bin/env python3
# encoding: utf-8
#
# setup.py
#
# Created by José Sánchez-Gallego on 22 Oct 2016.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os

from distutils.core import setup
from distutils.extension import Extension

from Cython.Build import cythonize
import numpy


os.environ['CC'] = 'g++ -w -framework SBIGUDrv'
os.environ['CXX'] = 'g++ -w -framework SBIGUDrv'


# sbig_extension = Extension(
#     'controllers/src/sbig/csbig',
#     sources=['controllers/src/sbig/csbig.pyx', 'controllers/src/sbig/csbigcam.cpp',
#              'controllers/src/sbig/csbigimg.cpp'],
#     libraries=['cfitsio'],
#     include_dirs=[numpy.get_include()],
#     language='c++')


sx_extension = Extension(
    'controllers/csx',
    sources=['controllers/src/sx/csx.pyx', 'controllers/src/sx/sxccdusb.cpp'],
    libraries=['usb-1.0'],
    library_dirs=['/usr/local/lib'],
    include_dirs=[numpy.get_include(), '/usr/local/include/libusb-1.0'],
    language='c++')


setup(
    name='bmo',
    # ext_modules=cythonize([sbig_extension, sx_extension])
    ext_modules=cythonize([sx_extension])
)
