floodfill
=========

.. image:: https://travis-ci.com/tibroc/floodfill.svg?branch=master
    :target: https://travis-ci.com/tibroc/floodfill

This is an implementation of the floodfill algorithm for fire event detection as described in:

    | Archibald, Sally & Roy, David. (2009).
    | Identifying individual fires from satellite-derived burned area data.
    | III-160 . 10.1109/IGARSS.2009.5417974.


Installation
------------

To install this python package you need to download the repository,
navigate to the root folder of it and install it using the ``setup.py``:

.. code-block:: bash

    python setup.py install


Usage
-----

The program can be executed as a python module:

.. code-block:: bash

    python -m floodfill -h

The program provides some command line parameters that let you define its behavior.
The ``-h`` flag will give you an overview over the options and how to use it.

A simple test run can be done like this:

.. code-block:: bash

    mkdir output
    python -m floodfill --input=tests/test_data.tif --output-folder=output -b
