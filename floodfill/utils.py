# -*- coding: utf-8 -*-
'''Floodfill algorithm
:copyright: 2020, Timo Nogueira Brockmeyer
:license: MIT
'''

import importlib
import inspect

import numpy
import rasterio


def run_algo(name, **kwargs):
    """Load an algorithm-module and run its run()-function.

    :param name: name of the module implementing the algorithm
    :type name: str
    :return: [description]
    :rtype: [type]
    """
    module = importlib.import_module(f'floodfill.algorithms.{name}')
    # match kwargs
    sig = inspect.signature(module.run)
    matched = {k: v for k, v in kwargs.items() if k in sig.parameters.keys()}
    return module.run(**matched)


def read_data(file):
    """Read the raster file and return a numpy array.

    Only the first band of the raster file is read.

    :param file: file path
    :type file: str
    :return: a tuple of length two, containing an array
        of the raster data and the raster profile
    :rtype: tuple
    """
    with rasterio.open(file) as f:
        data = f.read(1)
        profile = f.profile
    return data, profile


def write_data(path, raster, profile):
    """Write the results to disc as a geotiff raster file.

    :param path: the file name and location to be written to
    :type path: str
    :param raster: the raster data
    :type raster: numpy.ndarray
    :param profile: the profile from the rasterio.io.DatasetReader
    :type profile: rasterio.profiles.Profile
    """
    raster = raster.astype(rasterio.uint16)
    with rasterio.Env():
        # take profile from input image and change data type
        profile.update(dtype=rasterio.uint16,
                       nodata=0)
        with rasterio.open(path, 'w', **profile) as dst:
            dst.write(raster, 1)


def isolate_burned_pixels(array, upper, lower):
    """This function sets alls entries of the given array
    with values between 'upper' and 'lower' to zero.

    Usually the burned pixels have specific values
    (e.g. the julian day of the year) and other values may occur
    in the dataset. This function helps to 'clean' the data so that
    all values outside the bound of 'upper' and 'lower' are
    set to zero.

    :param array: the raster data
    :type array: numpy.ndarray
    :param upper: the upper bound for the burned data values
    :type upper: int
    :param lower: the lower bound for the burned data values
    :type lower: int
    :return: the cleaned raster data
    :rtype: numpy.ndarray
    """
    not_burned = numpy.logical_or(array <= lower,
                                  array >= upper)
    array[not_burned] = 0
    return array
