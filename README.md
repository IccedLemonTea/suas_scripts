# SUAS Scripts

This repository contains Python utilities for working with FLIR RJPEG thermal imagery, for the IMGS 589 sUAS class of 2025-26. 

## Installation

Clone the repository and install the required dependencies:
* git clone https://github.com/iccedlemontea/suas_scripts.git
* cd suas_scripts

## Usage

* python rjpeg_analysis.py /path/to/image_R.jpg --show
* python rjpeg_analysis.py /path/to/image_R.jpg --single
* python rjpeg_analysis.py /path/to/folder -a output.npy
* python rjpeg_analysis.py -p run1.npy run2.npy run3.npy run4.npy

## Requirements 

* Carl Salvaggio's RJPEG class
* Numpy
* Pillow
* Matplotlib
