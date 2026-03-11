import os
import numpy as np
import glob
import math

import flir
import imreg_dft as ird

import traceback

def register_video(datadir, outpath, metadatapath, start_frame=0, end_frame=None, ref_every=1):
    if end_frame is None:
        end_frame = len(image_files) - 1

    # Load location data
    metadata = np.load(metadatapath)
    metadata = metadata[start_frame:end_frame+1]
    altitude_abs = metadata[:,0]
    
    # ----- Unused metadata -----
    # altitude_rel = metadata[:,1]
    # gimbal_roll = metadata[:,2]
    # gimbal_yaw = metadata[:,3]
    # gimbal_pitch = metadata[:,4]
    # flight_roll = metadata[:,5]
    # flight_yaw = metadata[:,6]
    # flight_pitch = metadata[:,7]

    # Find video frames
    image_files = sorted(glob.glob(os.path.join(datadir, "*.jpg")))
    image_files = image_files[start_frame:end_frame+1]

    sort_idxs = (-altitude_abs).argsort() # Sort descending (literally)
    metadata = metadata[sort_idxs]
    image_files = [image_files[i] for i in sort_idxs]

    ref_img_i = 0
    ref_img = flir.RJPEG(image_files[ref_img_i]).raw_counts

    transform_matrices = np.zeros((len(image_files), 3, 3), dtype=np.float64)
    registered_to = np.zeros((len(image_files),), dtype=np.uint64)
    for i, image_file in enumerate(image_files):
        if i == ref_img_i:
            continue # Skip first reference image

        rjpeg = flir.RJPEG(image_file)
        img = rjpeg.raw_counts

        try:
            result = ird.imreg._similarity(
                ref_img,
                img,
                numiter=3,
                order=3,
                constraints=None,
                filter_pcorr=0,
                exponent="inf",
                bgval=None,
                reports=None,
            )
            scale = result["scale"]
            angle = result["angle"]
            vector = result["tvec"]
            m_scale = np.diag([scale, scale, 1.0])
            m_rot = np.identity(3)
            angle = math.radians(angle)
            m_rot[0, 0] = math.cos(angle)
            m_rot[1, 1] = math.cos(angle)
            m_rot[0, 1] = -math.sin(angle)
            m_rot[1, 0] = math.sin(angle)
            m_transl = np.identity(3)
            m_transl[:2, 2] = vector
            m_transform = np.dot(m_transl, np.dot(m_rot, m_scale))
            success = result["success"]
        except Exception as e:
            traceback.print_exc(e)
            print("Error registering frame", image_file, "to frame", image_files[ref_img_i])
            continue

        transform_matrices[i] = m_transform
        registered_to[i] = ref_img_i
        
        print(f"{i}/{len(image_files)}, Success={success}")

        if not i % ref_every:
            if success < 0.25:
                print("URGENT WARNING: There was a bad frame used as a reference, adjust registration strategy.")
            ref_img = img
            ref_img_i = i
            print(f"New reference frame: {i}")

    np.savez(outpath, transform_matrices=transform_matrices, registered_to=registered_to)
    print("Saved registration transform matrices to", outpath)

# Debug / Test script
if __name__ == "__main__":
    datadir = "/home/star/data/high_gain_flight7/"
    metadatapath = "metadata.npy"
    outpath = "registration_data_flight7_every10.npz"
    start_frame = 0
    end_frame = 80
    ref_every = 10
    register_video(datadir, outpath, metadatapath, start_frame, end_frame, ref_every)
