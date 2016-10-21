from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import os
import numpy

os.environ['CC'] = 'g++ -w -framework SBIGUDrv'
os.environ['CXX'] = 'g++ -w -framework SBIGUDrv'

setup(
    name='sdssCamera',
    ext_modules=cythonize(
        [Extension('./controllers/csbig',
                   sources=['controllers/csbig.pyx', 'src/csbigcam.cpp', 'src/csbigimg.cpp'],
                   libraries=['cfitsio'],
                   include_dirs=[numpy.get_include()],
                   language='c++')])
)
