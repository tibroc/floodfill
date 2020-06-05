import os
import unittest

import numpy
import rasterio

import floodfill

TEST_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../tests/test_data.tif')


class TestDataIo(unittest.TestCase):

    def test_reading(self):
        data, profile = floodfill.read_data(TEST_FILE)
        self.assertIsInstance(profile, rasterio.profiles.Profile)
        self.assertIsNotNone(data)
        self.assertListEqual([profile['height'], profile['width']],
                             list(data.shape))


class TestFloodfill(unittest.TestCase):

    def test_cleaning(self):
        data, _ = floodfill.read_data(TEST_FILE)
        lower = 1  # lower fire value bound
        upper = 366  # upper fire value bound
        data[0, 0] = -1  # create lower outlier
        data[0, 1] = 10000  # create upper outlier
        data = floodfill.isolate_burned_pixels(data, upper, lower)
        self.assertLessEqual(data.max(), upper)
        min_burned = data[data != 0].min()
        self.assertGreaterEqual(min_burned, lower)

    def test_get_neighbors(self):
        test_array = numpy.zeros((3, 3))
        sum_true = []
        for i in range(0, 3):
            for j in range(0, 3):
                sum_true.append(
                    numpy.sum(
                        floodfill._get_neighbors(i, j, test_array, 1)
                    )
                )
        self.assertListEqual(sum_true, [3, 5, 3, 5, 8, 5, 3, 5, 3])

    def test_floodfill(self):
        data, _ = floodfill.read_data(TEST_FILE)
        data = floodfill.isolate_burned_pixels(data, 366, 1)
        ids, burn_dates = floodfill.floodfill(data, 3)
        self.assertEqual(ids.max(), 929)
        self.assertEqual(numpy.sum(burn_dates != data), 0)


if __name__ == '__main__':
    unittest.main()
