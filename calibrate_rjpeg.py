### Calibrate RJPEG Test File ###
# Author : Cooper White (cjw9009@g.rit.edu)
# Date : 09/30/2025
# File : Blackbody.py
######
# This file loads an individual pixel from an RJPEG image stack, 
# and performs the necessary calculations to find the 
# gain and bias term of that pixel, based on a blackbody 
# calibration run
######
import sys
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os

from LWIRImageTool.Blackbody import Blackbody
from LWIRImageTool.BlackbodyCalibrationConfig import BlackbodyCalibrationConfig
from LWIRImageTool.CalibrationDataFactory import CalibrationDataFactory
from LWIRImageTool.StackImages import stack_images
import scipy.integrate as integrate
import scipy.constants as const
import math

def plotting_bb_run(src_image, cal_array=None, frame_number=None, row=0, col=0):
    if cal_array is not None:
        print(f"The size of cal_array is {cal_array.shape}")
        calibrated_image = np.empty((cal_array.shape[0], cal_array.shape[1]))
        frame_number = int(frame_number)
        for c in range(src_image.shape[1]):
            for r in range(src_image.shape[0]):
                calibrated_image[r,c] = src_image[r,c,frame_number]*cal_array[r,c,0] + cal_array[r,c,1]

    
        fig, img_axs = plt.subplots(1,2)
        img_axs[0].imshow(src_image[:,:,frame_number])
        img_axs[0].set_title("Uncalibrated Image")
        img_axs[1].imshow(calibrated_image)
        img_axs[1].set_title("Calibrated Image")
        fig.suptitle(f"Displaying frame number {frame_number} of {src_image.shape[2]}")
        plt.show()
    else:
        individual_pixel = src_image[row,col,:] 

        ### BASICALLY CALLING THE CAL FUNCTION FOR ONE PIXEL ###
        # Averaging data to smooth 1st derivative
        chunk_size = int(individual_pixel.shape[0]*0.001)
        #print(f"The data size is {individual_pixel.shape[0]} the chunk size is {chunk_size}")
        means = []
        for i in range(0,individual_pixel.shape[0], chunk_size):
            chunk = individual_pixel[i:i+chunk_size]
            means.append(chunk.mean())

        first_derivative = np.gradient(individual_pixel)
        second_derivative = np.gradient(first_derivative)

        stdev_first_deriv = np.std(first_derivative)
        stdev_second_deriv = np.std(second_derivative)
        mean_first_deriv = np.mean(first_derivative)
        mean_second_deriv = np.mean(second_derivative)

        # print(f"The mean of the first deriv is {mean_first_deriv}, and {mean_second_deriv} for the second deriv")
        # print(f"99% Of the data lies within {3*stdev_first_deriv} for the first deriv, and {3*stdev_second_deriv} for the second deriv")


        ### CALCULATING THE REGIONS OF ASCENSION ###
        # Vector to hold all values of when the 1st derivative exceeds 3 stdevs of the mean
        # Means that the DC of the scene is changing --> new temperature being reached in the cal run 
        # e.g. ascends to a new temperature
        change_in_temp = [0]

        for i in range(first_derivative.shape[0]):
            if first_derivative[i] >= (3*stdev_first_deriv + mean_first_deriv):
                if change_in_temp is not None:
                    change_in_temp.append(i)
                else:
                    change_in_temp = []
                    change_in_temp.append(i)

        # Adding end point of derivative vector
        change_in_temp.append(first_derivative.shape[0])


        # Vector to hold all derivative values that 
        # signal the beginning and end of the temperature change 
        # portion of the blackbody run (ASCENSION)
        ascension_start = []
        ascension_end = []
        for i in range(second_derivative.shape[0]):
            if second_derivative[i] >= (3*stdev_second_deriv + mean_second_deriv):
                ascension_start.append(i)
            if second_derivative[i] <= (-3*stdev_second_deriv + mean_second_deriv):
                ascension_end.append(i)

        # Window searching 1% of the data size
        window = int(len(means))*0.01 
        ascensions = False
        # print(f"ascenscion start size{len(ascension_start)} ascenscion end size{len(ascension_end)}")
        # Finding the max and min frame counts of the ascension
        for i in range(len(change_in_temp)-1):
            temp_ascension = []
            for j in range(len(ascension_start)):
                if (change_in_temp[i] + window) >= ascension_start[j] and (change_in_temp[i] - window <= ascension_start[j]):
                    temp_ascension.append(ascension_start[j])
            for j in range(len(ascension_end)):
                if (change_in_temp[i] + window) >= ascension_end[j] and (change_in_temp[i] - window <= ascension_end[j]):
                    temp_ascension.append(ascension_end[j])

            if temp_ascension == []:
                continue
            else:
                begin_average = min(temp_ascension)
                end_average = max(temp_ascension)
                if (change_in_temp[i+1] > change_in_temp[i] + window):
                    if ascensions == False:
                        array_of_avg_coords = np.array([0, begin_average, end_average])
                        ascensions = True
                    else:
                        array_of_avg_coords = np.append(array_of_avg_coords,[begin_average,end_average])

        array_of_avg_coords = np.append(array_of_avg_coords, len(individual_pixel))
        step_averages = np.array([])
        average_x_vals = np.array([])

        # Averaging between the end of one ascension and beginning of next
        # 2nd derivative min --> 2nd derivative max
        for i in range(0, array_of_avg_coords.shape[0]-1,2):
            step_cum_sum = 0.0
            count = 0.0
            average_x_vals = np.append(average_x_vals,int((array_of_avg_coords[i] + array_of_avg_coords[i+1])/2)*chunk_size)

            for j in range(array_of_avg_coords[i],array_of_avg_coords[i+1]-1,1):
                if first_derivative[j] <= (3*stdev_first_deriv + mean_first_deriv):
                    for b in range(j*chunk_size,(j+1)*chunk_size,1):
                        step_cum_sum = step_cum_sum + individual_pixel[b]
                        count = count + 1
            if count != 0:
                step_cum_sum = float(step_cum_sum / count)   
                step_averages = np.append(step_averages,[step_cum_sum])

        ### Generating blackbody band radiances ###
                blackbody = Blackbody()
                band_radiances = []

                txt_content = np.loadtxt("/home/cjw9009/Desktop/suas_data/FLIRSIRAS_CalData/flir_boson_with_13mm_45fov.txt", skiprows=1, delimiter=',')
                wavelengths = txt_content[:, 0]
                response = txt_content[:, 1]

                for i in range(step_averages.shape[0]):
                    temp = 283 + i*5.0
                    blackbody.absolute_temperature = temp
                    band_radiances.append(blackbody.band_radiance(wavelengths, response))

                ### Applying Linear Regression to find gain and bias terms ###
                gain, bias = np.polyfit(step_averages,band_radiances,1)
        
        ### PLOTTING ###
        print("plotting ...")
        # Plot of raw data
        fig, axs = plt.subplots(2,3)
        axs[0,0].plot(individual_pixel)
        axs[0,0].set_title(f"Pixel values over time at location ({row},{col})")
        axs[0,0].set_xlabel(f"Frame number")
        axs[0,0].set_ylabel(f"Digital Count")

        axs[0,1].plot(means)
        axs[0,1].set_title(f"Pixel values over time at location ({row},{col}) over " + str(chunk_size) + " frames")
        axs[0,1].set_xlabel(f"Frame number")
        axs[0,1].set_ylabel(f"Digital Count")


        axs[1,0].plot(first_derivative)
        axs[1,0].set_title("First derivative of Pixel")
        axs[1,0].set_xlabel(f"Frame number")
        axs[1,0].set_ylabel(f"Digital Count/Frame")

        axs[1,1].plot(second_derivative)
        axs[1,1].set_title("Second derivative of Pixel")
        axs[1,1].set_xlabel(f"Frame number")
        axs[1,1].set_ylabel(f"Digital Count/Frame^2")
        
        axs[0,2].scatter(range(len(individual_pixel)),individual_pixel,c='blue',s=2,marker='o',label = 'collected data')
        axs[0,2].scatter(average_x_vals,step_averages,c='red',s=30,marker='o', label = 'averages')
        axs[0,2].set_title("Averaged step levels plotted over raw data")
        axs[0,2].legend()
        axs[0,2].set_xlabel(f"Frame number")
        axs[0,2].set_ylabel(f"Digital Count")

        # print(f"The list of regions to average over is as follows {array_of_avg_coords}")
        axs[1,2].scatter(step_averages,band_radiances, c='blue', label='Averaged Data')
        axs[1,2].plot(step_averages, gain*step_averages+bias, c='red', label ='line of best fit')
        axs[1,2].set_title("Intgerated BB radiance vs DC")
        axs[1,2].legend()
        axs[1,2].set_xlabel(f"Digital Count")
        axs[1,2].set_ylabel(f"Band Radiance [W/m^2/sr]")

        fig.tight_layout()
        plt.show()

def main():
    description = "Generate calibration coefficients for a blackbody calibration run and plot the results."
    ap = argparse.ArgumentParser(description=description)

    ap.add_argument("path", nargs="?", default=None, help="Path to a numpy array of stacked RJPEG images.")
    ap.add_argument("-C", "--calibrate",action='store_true', help="Flag for calibration")
    ap.add_argument("-p", "--plot",action='store_true', help="Plot results, requires path to calibration array if already generated")
    ap.add_argument("-f", "--frame",default = None, help="Selects the frame from the blackbody run that you would like to visualize")
    ap.add_argument("-r", "--row",default = None, help="Selects the row of the pixel you would like to plot | Column is necessary too!")
    ap.add_argument("-c", "--col",default = None, help="Selects the row of the pixel you would like to plot | Row is necessary too!")
    ap.add_argument("-a", "--array",default = None,help="name of the cal_array you would like to generate, or filepath used to plot existing array")

    args = ap.parse_args()

    if args.plot:
        if os.path.isfile(args.path):
            print(f"Detected file: {args.path}")
            if args.array is not None:
                if os.path.isfile(args.array):
                    print(f"Array of name {args.array} being used")
                    if args.frame is not None:
                        src_image = np.load(args.path)
                        cal_array = np.load(args.array)
                        plotting_bb_run(src_image, cal_array, args.frame)
                    else:
                        print(f"Please select the frame you would like to see the uncal vs cal image for")
                else:
                    print(f"Array not found")
            elif args.array == None: 
                if args.row is not None and args.col is not None:
                    print(f"Only plotting pixel of row {args.row} and col {args.col} from src image")
                    src_image = np.load(args.path)
                    plotting_bb_run(src_image, row = int(args.row), col = int(args.col))
                else:
                    print(f"Pixel coordinates not specified, please specify pixel coordinates using -r and -c")
        else:
            print(f"File not recognized {args.path}")

    if args.calibrate:
        if os.path.isdir(args.path):
            print(f"Detected dir: {args.path}")
            txt_content = np.loadtxt(
                "/home/cjw9009/Desktop/suas_data/flir_boson_with_13mm_45fov.txt",
                skiprows=1,
                delimiter=',')
            wavelengths = txt_content[:, 0]
            response = txt_content[:, 1]

            ### USER TEST CONFIG ###
            test_directory = args.path
            test_filetype = "rjpeg"
            test_rsr = "/home/cjw9009/Desktop/suas_data/flir_boson_with_13mm_45fov.txt"

            print("Starting BlackbodyCalibration test...")

            # Build validated config
            config = BlackbodyCalibrationConfig(
                directory=test_directory,
                filetype=test_filetype,
                blackbody_temperature=283.15,  # K
                temperature_step=5.0,  # K
                rsr=test_rsr,
                progress_cb=None)
            print("Config Validated")
            # Create calibration via factory
            calib = CalibrationDataFactory.create(config)

            print("Calibration object created successfully.")
            print(f"Image stack shape: {calib.image_stack.shape}")
            print(f"Coefficient array shape: {calib.coefficients.shape}")

            # Save coefficients
            np.save(f"{args.array}_coefficients.npy", calib.coefficients)

            stack = calib.image_stack
            array_of_avg_coords = calib.find_ascensions(stack, 3, 0.001, [])
            # multiply DC by gain, add bias to get per pixel radiance


            # NEDT Calculation ### ADD CODE HERE
            print(array_of_avg_coords.shape[0])
            print(array_of_avg_coords)
            temps = [
                283.15, 288.15, 293.15, 298.15, 303.15, 308.15, 313.15, 318.15, 323.15,
                328.15, 333.15, 338.15, 343.15
            ]
            NEDT_array = np.empty((stack.shape[0], stack.shape[1], len(temps)))
            plancks_constant = const.h  # 6.62607015e-34 [Joules*Seconds]
            speed_of_light_constant = const.c  # 299792458.0 [Meters/Second]
            boltzmann_constant = const.k  # 1.380649e-23 [Joules/Kelvin]

            wavelengths = wavelengths * 0.000001
            numerator = 2 * plancks_constant * speed_of_light_constant * speed_of_light_constant

            # Precompute wavelength-only constants (done ONCE)
            wl = wavelengths
            wl5 = wl**5
            resp = response

            hc_over_k = plancks_constant * speed_of_light_constant / boltzmann_constant

            for r in range(stack.shape[0]):
                for c in range(stack.shape[1]):

                    individual_pixel = stack[r, c, :]
                    individual_pixel_rad = individual_pixel * calib.coefficients[
                        r, c, 0] + calib.coefficients[r, c, 1]
                    pixel_rad = individual_pixel_rad  # alias (faster lookup)

                    for i, To in enumerate(temps):

                        start = array_of_avg_coords[2 * i]
                        stop = array_of_avg_coords[2 * i + 1]

                        diffs = np.diff(pixel_rad[start:stop])

                        avg_diff = np.mean(diffs)
                        sigma_diff = np.std(diffs, ddof=0)
                        sigma = sigma_diff / np.sqrt(2)

                        # Vectorized Planck derivative
                        Xo = hc_over_k / (wl * To)
                        expX = np.exp(Xo)

                        numerator_dL = numerator * expX * Xo
                        denominator = wl5 * (expX - 1)**2 * To

                        dLdT = (numerator_dL / denominator) * resp

                        int_dLdT = integrate.simpson(dLdT, wavelengths)

                        NEDT_array[r, c, i] = sigma / int_dLdT

            print(f"{NEDT_array.shape}")

            np.save(f"{args.array}_NEDT_array.npy", NEDT_array)
            mean_NEDT = np.mean(NEDT_array, axis=(0, 1))
            print(f"Size of mean_NEDT{mean_NEDT.shape}")
            plt.scatter(range(10, 71, 5), mean_NEDT)
            plt.title("Average NEDT at each step")
            plt.xlabel("Temperature in Kelvin (Step Temperature)")
            plt.ylabel("Mean NEDT")
            plt.savefig("Plot of updated NEDT")
            plt.show()

if __name__ == "__main__":
    main()