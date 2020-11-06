# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

path = os.path.abspath(os.path.dirname(__file__))


def read(filename):
    with open(os.path.join(path, filename), encoding='utf-8') as f:
        return f.read()


setup(
    name='floodfill',
    version='0.1',
    description='Floodfill algorithm for fire event detection',
    author='Timo Nogueira Brockmeyer',
    license='MIT',
    url='https://github.com/tibroc/floodfill',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    install_requires=read('requirements.txt').split(),
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
)
