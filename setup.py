#!/usr/bin/env python
# encoding: utf-8
#
# setup.py
#
# Created by José Sánchez-Gallego on 5 May 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from setuptools import setup, find_packages

import os
import warnings


def convert_md_to_rst(fp):
    try:
        import pypandoc
        output = pypandoc.convert_file(fp, 'rst')
        return output
    except ImportError:
        warnings.warn('cannot import pypandoc.', UserWarning)
        return open(fp).read()


requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
install_requires = [line.strip().replace('==', '>=') for line in open(requirements_file)
                    if not line.strip().startswith('#') and line.strip() != '']

NAME = 'bmo'
VERSION = '0.2.7dev'


def run(packages):

    setup(name=NAME,
          version=VERSION,
          license='BSD3',
          description='The BMO camera controller for LCO',
          long_description=convert_md_to_rst('README.md'),
          author='José Sánchez-Gallego, and Conor Sayres',
          author_email='gallegoj@uw.edu',
          keywords='bmo astronomy camera',
          url='https://github.com/ApachePointObservatory/bmo',
          include_package_data=True,
          packages=packages,
          # install_requires=install_requires,
          package_dir={'': 'python'},
          scripts=[],
          classifiers=[
              'Development Status :: 4 - Beta',
              'Intended Audience :: Science/Research',
              'License :: OSI Approved :: BSD License',
              'Natural Language :: English',
              'Operating System :: OS Independent',
              'Programming Language :: Python',
              'Programming Language :: Python :: 2.6',
              'Programming Language :: Python :: 2.7',
              'Topic :: Documentation :: Sphinx',
              'Topic :: Software Development :: Libraries :: Python Modules',
          ],
          )


if __name__ == '__main__':

    packages = find_packages(where='python')

    # Runs distutils
    run(packages)
