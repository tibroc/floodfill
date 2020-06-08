
# -*- coding: utf-8 -*-
'''
Floodfill algorithm for fire event detection

This program implements the algorithm as described in:
Archibald, Sally & Roy, David. (2009).
Identifying individual fires from satellite-derived burned area data.
III-160 . 10.1109/IGARSS.2009.5417974.
~~~~~~~~~~~~~~~~~~~~~~
:copyright: 2020, Timo Nogueira Brockmeyer
:license: MIT
'''

import argparse
import glob
import logging
import multiprocessing
import os

import floodfill


def process_file(file):
    """Read and process one file and write the results
    to disc in the same format as the input file.

    :param file: the file to process
    :type file: str
    :param config: the config namespace from the command
        line parser
    :type config: argparse.Namespace
    """
    # read data
    data, profile = floodfill.read_data(file)

    # process data
    data = floodfill.isolate_burned_pixels(data,
                                           config.upper_value,
                                           config.lower_value)
    fire_ids, burn_dates = floodfill.floodfill(data, config.cut_off)

    # write data
    fname, ext = os.path.splitext(os.path.basename(file))

    # save burndates if required
    if config.save_bd:
        out_path_bds = os.path.join(config.output_folder,
                                    f"{fname}-floodfill_burndates{ext}")
        floodfill.write_data(out_path_bds, burn_dates, profile)

    # save patch ids
    out_path_ids = os.path.join(config.output_folder,
                                f"{fname}-floodfill_ids{ext}")
    floodfill.write_data(out_path_ids, fire_ids, profile)


def parse_command_line():
    """Parse the arguments from the command line.

    :return: the argument namespace
    :rtype: argparse.Namespace
    """

    parser = argparse.ArgumentParser(
        description='Identify fire events using the floodfill algorithm.')

    parser.add_argument('--input',
                        required=True,
                        help='The raster file tp process or root image folder '
                        'if use recursive mode.')

    parser.add_argument('--output-folder',
                        required=True,
                        help='Folder where the resulting raster images '
                        'will be saved')

    parser.add_argument('--cut-off',
                        type=int,
                        default=8,
                        help='Cut off value in days for burned pixels '
                        'belonging to the same event – defaults to 8.')

    parser.add_argument('--lower-value',
                        type=int,
                        default=1,
                        help='Minimum value of a burned pixel.'
                        'All data points below this value will be set to zero'
                        ' – defaults to 1.')

    parser.add_argument('--upper-value',
                        type=int,
                        default=366,
                        help='Maximum value of a burned pixel.'
                        'All data points above this value will be set to zero'
                        ' – defaults to 366.')

    parser.add_argument('--file-extension',
                        type=str,
                        default='.tif',
                        help='Extension of the files to read, e.g.'
                        '".tif" or ".tiff" – defaults to ".tif".')

    parser.add_argument('--n-workers',
                        type=int,
                        default=1,
                        help='Number of workers (max. = number of cpu cores). '
                        'If -r is set, input files can be processed in '
                        'parallel if number of workers is set > 1.')

    parser.add_argument('-b',
                        dest='save_bd',
                        action='store_true',
                        help='If set, write also the output'
                        'burn dates to disc.')

    parser.add_argument('-r',
                        dest='recursive',
                        action='store_true',
                        help='If set, process entire folders and subfolders.')

    parser.add_argument('-v',
                        dest='verbose',
                        action='store_true',
                        help='Keep talking while processing'
                        ' – **very** verbose.')

    return parser.parse_args()


def main():
    """The main function of the program.
    """
    global config
    config = parse_command_line()

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if config.verbose else logging.INFO)

    # process whole folder
    if config.recursive:

        # get list of files
        pattern = os.path.join(config.input, '**/*' + config.file_extension)
        files = [f for f in glob.glob(pattern, recursive=True)]

        # determine number of workers
        cpus = multiprocessing.cpu_count()
        n_workers = cpus if config.n_workers > cpus else config.n_workers
        logging.info(f"Using {n_workers} workers.")

        # process files
        with multiprocessing.Pool(n_workers) as pool:
            pool.map(process_file, files)

    # process one file only
    process_file(config.input)


if __name__ == "__main__":
    main()
