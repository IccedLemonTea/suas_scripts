# Overview
The program is a desktop GUI application built with PyQt6 and PyQtGraph designed to analyze thermal video frames (RJPEG images). It allows a user to draw Regions of Interest (ROIs) on an image, calculate the thermal statistics (mean and standard deviation) within those regions, and automatically track/propagate those ROIs across subsequent moving frames using pre-calculated image registration matrices.



# Setup
> **I'm sure this is due to change for the production-grade version, not the SUAS-II version (current)**

First run:
```bash
python3 -m pip install -r requirements.txt
```

> Before running, in the notebook, ensure you manually adjust the `start_frame` and `end_frame` to match the descent portion of your flight data.

Then execute the Jupyter Notebook `ProcessVideoHowTo.ipynb` from beginning to end. 




# Execution Workflow
## Standard Method
> This is the standard execution workflow for manual annotation over all video frames

1. Launch the program launched via the Jupyter Notebook cell with paths to the image directory, calibration data, and registration matrices.

2. Create labeled polygons (ROI) over their in-situ targets on the first frame (i.e., _frame 0_).

3. Scrub through frames using the timeline slider, or `<` and `>` button, adjusting the ROIs as necessary if they drift off-of the target.

4. Click "Save Stats", which calculates the thermal statistics for every ROI in every frame and exports the data.

## Shortcut Method
>"Propagate ROIs" is basically a **"fast-forward"** button. Instead of making the user manually scrub through all frames manually, this button forces the app to instantly calculate and draw the ROIs for all future frames at the exact same time. 

1. Launch the program launched via the Jupyter Notebook cell with paths to the image directory, calibration data, and registration matrices.

2. Create labeled polygons (ROI) over their in-situ targets on the first frame (i.e., _frame 0_).

3. Right-clicks on any part of the scene, select "Propagate ROIs". This applies mathematical transformations to _automatically_ draw the adjusted ROI over the same physical object in all future frames.

4. (optional) scrub through the timeline to make any manual adjustments

5. Click "Save Stats", which calculates the thermal statistics for every ROI in every frame and exports the data.



# Architecture (if you're curious)

The code follows a modular architecture, separating data, business logic (Services), state coordination (Managers), and the graphical interface (GUI).

## Data Classes
### ROIData
Holds that data (mean, std, coordinates) of individual ROIS.

### AppConfig
Holds global application parameters e.g. filepaths, frame ranges.

## Services (Stateless Logic)
### ImageService
Loads RJPEG files and applies calibration coefficients to convert raw digital counts (DC) into calibrated radiometric data (RAD).

### RegistrationService & ROIService
Work together to compute 3x3 transformation matrices between frames and mathematically transform the polygon coordinates of an ROI so it "moves" to the correct spot in a new frame.

### ROIStatsService
Extracts the underlying pixel values within an ROI's bounding box and computes the mean and standard deviation.

### ExportService
Handles writing the final ROI coordinates to a Pickle file and the statistical data to a CSV.


## Managers (State Coordination):
### DataManager
Handles all disk I/O at startup, loading images, metadata, calibration matrices, and previously saved ROI sessions. Includes two very important variables registered_to ("Reference Frame", a specific video frame is linked to), and matrices (3x3 transformation matrices). Without these, automatic propagation cannot occur.

### ROIManager
Creates new UI ROI objects (LabeledPolyLineROI) and toggles the display mode between raw DC and calibrated RAD statistics.

### FrameManager
Tracks the current frame index and dictates the logic for propagating ROIs from a reference frame into target frames.

## The GUI (ImageViewer)
The main window that ties everything together. It houses the image canvas, frame-scrubbing slider, and control buttons. It listens for user interactions (like moving an ROI or changing a frame) and calls the appropriate Managers/Services to update the screen.


# Authors & Contributors
- (Author) **Joe Walker**
- (Contrib) **Josie Clapp**
- (Contrib) **Cooper White**
- (Contrib) **Adele Jones**
- (Contrib) **Gian-Mateo Tifone**