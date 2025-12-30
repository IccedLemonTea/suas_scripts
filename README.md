# SUAS Scripts

This repository contains Python utilities for working with FLIR RJPEG thermal imagery, for the IMGS 589 sUAS class of 2025-26. 

## Installation

Clone the repository and install the required dependencies:
* git clone https://github.com/iccedlemontea/suas_scripts.git
* cd suas_scripts

## Usage - Parse and Plot RJPEG

* python parse_and_plot_RJPEG.py /path/to/image_R.jpg --show
* python parse_and_plot_RJPEG.py /path/to/image_R.jpg --single
* python parse_and_plot_RJPEG.py /path/to/folder -a output.npy
* python parse_and_plot_RJPEG.py -p run1.npy run2.npy run3.npy run4.npy

## Usage - Calibrate RJPEG
If you would like to calibrate your FLIR SIRAS using a blackbody run as specified in the user manual, here are the commands to do so:

* python calibrate_rjpeg.py /path/to/imagestack.npy -p -r row_number -c col_number 
* python calibrate_rjpeg.py -C path/to/imagestack.npy
* python calibrate_rjpeg.py path/to/iamgestack.npy -p -a path/to/calibrationarray.npy -f frame_number


## Requirements 

* Cooper White's LWIRImageTool module
* Numpy
* Pillow
* Matplotlib
* Scipy
* Spectral
