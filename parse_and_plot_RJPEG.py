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

# NOTE : You always need to provide a single image filepath, even if you are computing an entire directory. Just a quirk I haven't worked out yet

### TEST COMMAND LINES ###
#  python parse_and_plot_RJPEG.py ../FLIRSIRAS_CalData/20251103/20251103_135118_490_MSX_R.jpg -s --> Shows image at path
# 
#  python parse_and_plot.py  ../11_06_1900/ -a 10131106_1900_40ec_45BB_maunalFFC --> Averages over directory D, saves out array a
# 
#  python parse_and_plot.py -p ../20251106_1230/20251106_40ec_45BB_autoFFC.npy  --> plots numpy array


# Requirements below
import os
import numpy as np
import matplotlib.pyplot as plt
import argparse
from RJPEG import RJPEG


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
    """Computes the average of the image center across a directory of RJPEGs."""
    print(f"Computing averages for all images in directory: {directory}")
    averages = []

    directory = os.fsencode(directory)
    first_image_path = None

    # Loop through each RJPEG image
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith("_R.jpg"):
            file_path = os.path.join(os.fsdecode(directory), filename)
            if first_image_path is None:
                # Load first image to get shape and center
                first_src = RJPEG(file_path)
                center_y, center_x = first_src.shape[0] // 2, first_src.shape[1] // 2
                half_k = kernel_size // 2
            # Process current image
            src = RJPEG(file_path)
            patch = src.raw_counts[
                center_y - half_k:center_y + half_k,
                center_x - half_k:center_x + half_k
            ]
            averages.append(np.average(patch))

    averages = np.array(averages)
    np.save(array_name, averages)
    print(f"Saved averages to {array_name}")
    return averages


def plot_results(main_run, run2, run3, run4):
    """Plots digital count results for comparison between runs."""
    print("Plotting comparison between multiple runs...")
    averages = np.load(main_run)
    averages_2 = np.load(run2)
    averages_3 = np.load(run3)
    averages_4 = np.load(run4)

    time_minutes = np.arange(len(averages_3)) * 5 / 60

    plt.plot(time_minutes, averages[0:712], label='0930 Auto FFC run')
    plt.plot(time_minutes, averages_2[0:712], label='1900 Manual FFC run')
    plt.plot(time_minutes, averages_3, label='1230 Auto FFC run')
    plt.plot(time_minutes, averages_4[0:712], label='1530 Manual FFC run')

    plt.xlabel("Minutes")
    plt.ylabel("Digital Count")
    plt.title("Digital Count in 40°C Env, 45°C BB, averaged at center (10x10 kernel)")
    plt.grid(True)
    plt.legend()
    plt.show()
    print("Plot complete.")


def main():
    description = "Perform operations on FLIR RJPEG data (visualize, average, plot)."
    ap = argparse.ArgumentParser(description=description)

    ap.add_argument("path", nargs="?", default=None, help="Path to a FLIR radiometric JPEG or directory of images")
    ap.add_argument("-s", "--show", action="store_true", help="Show image")
    ap.add_argument("-S", "--single", action="store_true", help="Compute average digital count for one image")
    ap.add_argument("-a", "--array", help="Name of numpy array to save averages")
    ap.add_argument("-p", "--plot", help="Plot results (requires run file paths)", nargs=4)

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
