import sys
import os
import glob
import json
import subprocess
import numpy as np

def metadata_to_np(datadir, outputfile):
    rjpeg_file_paths = sorted(glob.glob(os.path.join(datadir, "*.jpg")))
    keys_of_interest = (
        "AbsoluteAltitude",
        "RelativeAltitude",
        "GimbalRollDegree",
        "GimbalYawDegree",
        "GimbalPitchDegree",
        "FlightRollDegree",
        "FlightYawDegree",
        "FlightPitchDegree",
    )
    out = np.zeros((len(rjpeg_file_paths), len(keys_of_interest)), dtype=np.float64)
    for i, fpath in enumerate(rjpeg_file_paths):
        # Get metadata from file with exiftool, make sure it's installed on
        # your system!
        cmd = ["exiftool", "-j", "-n", fpath]
        result = subprocess.run(
                    cmd, 
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=True)
        metadata = json.loads(result.stdout)[0]

        # Write the metadata of interest to the array
        out[i, :] = [float(metadata[key]) for key in keys_of_interest]
        
        print(f"{i+1}/{len(rjpeg_file_paths)}")

    # Save the array to a file
    np.save(outputfile, out)

if __name__=="__main__":
    if len(sys.argv) == 1:
        print("Use this program to convert RJPEG metadata in a number of files to a numpy binary file.\nUsage: python metadata_to_np.py --data <data directory> --output <output file name, default metadata.npy>")
        quit()
    try:
        datadir = sys.argv[sys.argv.index("--data")+1]
    except:
        raise Exception("Data directory not provided, use --data <RJPEG data directory>")
    try:
        if "--output" in sys.argv:
            outputfile = sys.argv[sys.argv.index("--output")+1]
        else:
            outputfile = "metadata.npy"
    except:
        raise Exception("Error reading provided output directory from argument.")

    metadata_to_np(datadir, outputfile)
