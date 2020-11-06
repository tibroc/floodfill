# -*- coding: utf-8 -*-
'''Tests
:copyright: 2020, Timo Nogueira Brockmeyer
:license: MIT
'''

import os
import unittest
import tempfile

import numpy
import rasterio

import floodfill
from floodfill import __main__
from floodfill.algorithms import nogueira_etal


TEST_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../tests/test_data.tif')


class TestDataIo(unittest.TestCase):

    def setUp(self):
        self.data, self.profile = floodfill.read_data(TEST_FILE)

    def test_reading(self):
        self.assertIsInstance(self.profile, rasterio.profiles.Profile)
        self.assertIsNotNone(self.data)
        self.assertListEqual([self.profile['height'], self.profile['width']],
                             list(self.data.shape))

    def test_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            file_name = os.path.join(tmp, 'test.tif')
            floodfill.write_data(file_name, self.data, self.profile)
            self.assertTrue(os.path.isfile(file_name))

            # read data again and check if it is the same
            data_tmp, profile_tmp = floodfill.read_data(file_name)
            self.assertTrue(numpy.all(data_tmp == self.data))


class TestCleaning(unittest.TestCase):

    def test_cleaning(self):
        """Check if data cleaning works as intended.
        """
        data, _ = floodfill.read_data(TEST_FILE)
        lower = 1  # lower fire value bound
        upper = 366  # upper fire value bound
        data[0, 0] = -1  # create lower outlier
        data[0, 1] = 10000  # create upper outlier
        data = floodfill.isolate_burned_pixels(data, upper, lower)
        self.assertLessEqual(data.max(), upper)
        min_burned = data[data != 0].min()
        self.assertGreaterEqual(min_burned, lower)


class TestMain(unittest.TestCase):

    def test_process_file(self):
        data, _ = floodfill.read_data(TEST_FILE)
        with tempfile.TemporaryDirectory() as tmp:
            config = __main__.parse_command_line(
                [f'--input={TEST_FILE}', f'--output-folder={tmp}', '-b'])
            __main__.process_file(config.input, config=config)

            # construct file names
            bd_file = __main__._get_filename(config.output_folder,
                                             config.input,
                                             'floodfill_burndates')
            id_file = __main__._get_filename(config.output_folder,
                                             config.input,
                                             'floodfill_ids')
            self.assertTrue(os.path.isfile(bd_file))
            self.assertTrue(os.path.isfile(id_file))

            # read data again and check if it is the same
            burn_dates, _ = floodfill.read_data(bd_file)
            self.assertTrue(numpy.all(burn_dates == data))


class TestNogueiraEtal(unittest.TestCase):

    def test_get_neighbors(self):
        """Check if neighbors are always correctly identified,
        even when on the borders.
        """
        test_array = numpy.zeros((3, 3))
        sum_true = []
        for i in range(0, 3):
            for j in range(0, 3):
                sum_true.append(
                    numpy.sum(
                        nogueira_etal._get_neighbors(i, j, test_array, 1)
                    )
                )
        self.assertListEqual(sum_true, [3, 5, 3, 5, 8, 5, 3, 5, 3])

    def test_floodfill(self):
        """Test the floodfill algorithm itself.
        """
        data, _ = floodfill.read_data(TEST_FILE)
        data = floodfill.isolate_burned_pixels(data, 366, 1)
        ids, burn_dates = nogueira_etal.run(data, 3)
        self.assertEqual(ids.max(), 929)  # correct number of fires found?

        # are the burn dates still the same as in the input?
        self.assertTrue(numpy.all(burn_dates == data))


if __name__ == '__main__':
    unittest.main()
