### INFO ###
# Author : Cooper White (cjw9009@g.rit.edu)
# Filename : parse_and_plot_RJPEG.py
# Date : 11/08/2025
# This file takes in an individual file, to plot within matplot lib
# OR 
# An entire directory, which each image in the directory is then averaged over a 10x10 kernel, centered at the image center
# Once averaged, it is saved to the array name that the user gives
# OR 
# The numpy array created by this file can be read in and plotted

import os
import numpy as np
import matplotlib.pyplot as plt
import argparse
import sys

# Add the path to the flir directory

from LWIRImageTool.RJPEG import RJPEG
from LWIRImageTool.StackImages import stack_images



def show_image(src: RJPEG):
    """Displays the raw counts image with matplotlib."""
    print("Showing image...")
    plt.imshow(src.raw_counts, cmap="gray")
    plt.colorbar()
    plt.show()
    print("Image shown.")


def compute_single_average(src: RJPEG):
    """Computes and prints the average digital count of an image."""
    print("Computing single image average...")
    average = np.average(src.raw_counts)
    print(f"The average for the image is {average:.3f}")
    return np.array([average])


def compute_directory_average(directory: str, array_name: str, kernel_size: int = 10):

    stack = stack_images(directory, "rjpeg")
    np.save(array_name, stack)
    print(f"Saved stack to {array_name}")
    return stack


def plot_results(main_run):
    """Plots digital count results for comparison between runs."""
    print("Plotting ...")
    averages = np.load(main_run)
    averages = np.mean(averages, axis = (0,1))

    temperatures = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
    #averages_2 = np.load(run2)
    #averages_3 = np.load(run3)
    # averages_4 = np.load(run4)
    
    #averages = np.concatenate([averages[0:320], averages[370:]])
    time_minutes = np.arange(len(averages)) * 3 / 60
    # print(f"{averages.shape} {averages_2.shape} {averages_3.shape}")
    # plt.plot(time_minutes, averages, label="02/10")
    #plt.plot(time_minutes, averages_2[0:1805], label="01/30/26")
    #plt.plot(time_minutes, averages_3[0:2050], label="12/06_1200")
    # lt.plot(time_minutes, averages_4[0:712], label='1530 Manual FFC run')
    
    fig, ax1 = plt.subplots()

    ax1.plot(time_minutes, averages, label="02/10")
    ax1.set_xlabel("Minutes")
    ax1.set_ylabel("Digital Count")
    ax1.grid(True)

    # ---- SECOND Y AXIS ----
    ax2 = ax1.twinx()
    ax2.set_ylabel("Temperature [C]")   # <-- change this text to include degrees
    ax2.set_ylim([10, 70])
    # ax2.scatter(time_minutes[indices], temperatures)
    plt.title("10 Environmental Chamber BB Runs")
    ax1.legend()

    plt.show()


def main():
    description = "Perform operations on FLIR RJPEG data (visualize, average, plot)."
    ap = argparse.ArgumentParser(description=description)

    ap.add_argument("path", nargs="?", default=None, help="Path to a FLIR radiometric JPEG or directory of images")
    ap.add_argument("-s", "--show", action="store_true", help="Show image")
    ap.add_argument("-S", "--single", action="store_true", help="Compute average digital count for one image")
    ap.add_argument("-a", "--array", help="Name of numpy array to save averages")
    ap.add_argument("-p", "--plot", help="Plot results (requires run file paths)", nargs=1)

    args = ap.parse_args()

    if args.path:
        if os.path.isdir(args.path):
            print(f"Detected directory: {args.path}")
            if args.array:
                compute_directory_average(args.path, args.array)
            else:
                print("No output array name provided (-a). Use -a to save results.")
        elif os.path.isfile(args.path):
            src = RJPEG(args.path)
            if args.show:
                show_image(src)
            if args.single:
                compute_single_average(src)
        else:
            print(f"Invalid path: {args.path}")

    if args.plot:
        plot_results(*args.plot)


if __name__ == "__main__":
    main()
