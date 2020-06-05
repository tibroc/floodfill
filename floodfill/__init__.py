import logging

import numpy
import rasterio


def read_data(file):
    """Read the raster file and return a numpy array.

    Only the first band of the raster file is read.

    :param file: file path
    :type file: str
    :return: an array of the raster data
    :rtype: numpy.ndarray
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


def _get_neighbors(x, y, data, distance=1):
    """Helper function for the floodfill algorithm
    to identify neighbors of the focus pixel.

    :param x: x coordinate of the focus pixel
    :type x: int
    :param y: y coordinate of the focus pixel
    :type y: int
    :param data: the raster data
    :type data: numpy.ndarray
    :param distance: the distance for what to consider
        a neighbor, defaults to 1
    :type distance: int, optional
    :return: a boolean array where the neighboring pixels
        of the focus pixel are set to True and all other
        values are False.
    :rtype: numpy.ndarray
    """
    mask = numpy.zeros_like(data, dtype=numpy.bool)
    y_max, x_max = data.shape
    y_low = max(y - distance, 0)
    y_high = min(y + distance + 1, y_max)
    x_low = max(x - distance, 0)
    x_high = min(x + distance + 1, x_max)
    mask[y_low:y_high, x_low:x_high] = True
    mask[y, x] = False
    return mask


def floodfill(raster, cut_off):
    """The floodfill agorithm as described in the paper.

    :param raster: the raster data
    :type raster: numpy.ndarray
    :param cut_off: the cut-off value in days –
        this value is a temporal threshold of when to
        consider two fires distinct events.
    :type cut_off: int
    :return: a tuple of length two, containing two numpy.ndarrays
        with the same dimensions as the input 'raster'.
        The first item are the fire patches as connected components
        where each event has a unique id.
        The second item are the burn dates.
    :rtype: tuple
    """

    # get coordinates of burned pixels
    y_coor, x_coor = numpy.where(raster > 0)
    n_pixels = len(y_coor)
    logging.info(f"Found {n_pixels} candidate pixels.")

    # iterate through the pixels
    burn_date_raster = numpy.zeros_like(raster, dtype=numpy.int16)
    fire_id_raster = numpy.zeros_like(raster, dtype=numpy.uint16)
    fire_counter = 1
    for y, x in zip(y_coor, x_coor):

        pixel_date = raster[y, x]

        # get pixel neighbors
        neighbor_mask = _get_neighbors(x, y, raster)
        neighbor_ids = fire_id_raster[neighbor_mask]
        neighbor_dates = burn_date_raster[neighbor_mask]

        # meta data of pixel neighbors
        current_fire = numpy.abs(neighbor_dates - pixel_date) <= cut_off
        old_fire_present = neighbor_ids.sum() > 0
        n_current_fires = current_fire.sum()
        current_ids = numpy.unique(neighbor_ids[current_fire])
        n_current_ids = len(current_ids)

        # evaluate pixel
        if not old_fire_present or (old_fire_present and n_current_fires == 0):
            # new fire, because there are no previous
            # or only old fires registered in this neighborhood
            if fire_id_raster[y, x] > 0:
                # an old fire was already here
                logging.info("An old fire was already present"
                             f"at pixel ({y},{x}).")
                continue
            # we actually found a completely new fire
            fire_id_raster[y, x] = fire_counter
            burn_date_raster[y, x] = pixel_date
            fire_counter += 1
            continue

        if old_fire_present and n_current_fires > 0:
            if n_current_fires == 1 or \
                    (n_current_fires > 1 and n_current_ids == 1):
                fire_id_raster[y, x] = current_ids[0]
                burn_date_raster[y, x] = pixel_date
                continue
            if n_current_fires > 1 and n_current_ids > 1:
                # find all pixels with these ids
                which = numpy.isin(fire_id_raster, current_ids)
                fire_id_raster[which] = current_ids.min()  # assign lowest id
                fire_id_raster[y, x] = current_ids.min()
                burn_date_raster[y, x] = pixel_date

    return fire_id_raster, burn_date_raster
