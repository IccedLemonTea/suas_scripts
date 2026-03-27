import numpy as np
import LWIRImageTool as lit
import matplotlib.pyplot as plt


# Read in sensor radiance from ROI statisics

# Placeholder values
roi_1 = 7.0 # [W/m^s/sr/micron]
roi_2 = 4.1 # [W/m^s/sr/micron]
roi_3 = 10 # [W/m^s/sr/micron]

# Read in transmission and upwelling determined by the collect

# Placeholders
tau = 0.90
upwelling = 1.0 # [W/m^s/sr/micron]

# Determine ground leaving radiance after collection

ground_rad_1 = (roi_1-upwelling)/tau
ground_rad_2 = (roi_2-upwelling)/tau
ground_rad_3 = (roi_3-upwelling)/tau

# Read in emissivity data

emissivity = [0.05, 0.1, 0.2, 0.5, 1.0, 1.0, 1.0, 1.0, 0.9, 0.6, 0.2, 0.1, 0.05]
wavelengths = [8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12, 12.5, 13, 13.5, 14.0]

rsr = np.loadtxt("/home/cjw9009/Desktop/suas_scripts/updated_flir_boson_with_13mm_45fov.txt", delimiter=',')
print(rsr.shape)