import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
import matplotlib.pyplot as plt
from astroquery.mast import Observations
import getpass
import os
import shutil


# read the FITS file, return the data and WCS object
def read_fits(fileName):
    hdulist = fits.open(fileName)
    data = hdulist[1].data
    wcs = WCS(hdulist[1].header)
    hdulist.close()

    return data, wcs


# Get the parameter from each line of the tablea1.dat file
def get_par(line, index):
    obsID = line[8:17]
    ra1 = float(line[103:114])
    dec1 = float(line[115:126])
    ra2 = float(line[127:138])
    dec2 = float(line[139:150])

    print('{}-{}'.format(index, obsID))
    return obsID, ra1, dec1, ra2, dec2


# Convert the position in the astronomy coordinate system to pixel position
def convert_world2pix(path, ra1, dec1, ra2, dec2):
    data, wcs = read_fits(path)

    x1, y1 = wcs.all_world2pix(ra1, dec1, 1)
    x2, y2 = wcs.all_world2pix(ra2, dec2, 1)

    return data, x1, y1, x2, y2


# Plot a draft of data, with red box pointing out the asteroid
def plot_data(data, obsID, index, x1, y1, x2, y2):
    plt.imshow(data, cmap='gray', vmin=0.0, vmax=0.01)
    plt.plot([x1, x2], [y1, y1], 'r')
    plt.plot([x1, x2], [y2, y2], 'r')
    plt.plot([x1, x1], [y1, y2], 'r')
    plt.plot([x2, x2], [y1, y2], 'r')
    plt.colorbar()
    plt.savefig('.\pic\{}-{}.jpg'.format(index, obsID), dpi=300)
    plt.clf()


# Connect the session to MAST API. Type in your token.
def connect_session():
    token = getpass.getpass('Enter your token:')
    my_session = Observations.login(token=token)


# Download file from MAST database
def download_file(obsID):
    single_obs = Observations.query_criteria(obs_id=obsID)
    data_products = Observations.get_product_list(single_obs)
    manifest = Observations.download_products(data_products,
                                              obs_id=obsID,
                                              productSubGroupDescription='DRC',
                                              obs_collection='HST')

    # Generate the path for the FITS file
    path = '.\mastDownload\HST\{}'.format(obsID)
    fileName = os.listdir(path)[0]
    path = '{}\{}'.format(path, fileName)

    return path


# Save the data and asteroid position into a npz file
def save_data(obsID, index, data, x1, y1, x2, y2):
    matrix2 = np.array([x1, y1, x2, y2])
    dataPath = '.\data\{}-{}'.format(index, obsID)
    np.savez(dataPath, matrix1=data, matrix2=matrix2)
    print('Successfully save data for {}-{}'.format(index, obsID))


# Sometimes there may be multiple asteroids in the same FITS file,
# so we'd love to delete the FITS file several iterations after
# the inital download.
class FileManager:
    def __init__(self, capacity):
        self.list = []
        self.capacity = capacity

    def update_list(self, nextID):
        self.list.append(nextID)
        if len(self.list) <= self.capacity:
            return 0
        else:
            return self.list.pop(0)

    def get_list(self):
        print(self.list)


# Delete the unwanted directory, if the directory still exists
def delete_dir(fileNameDelete):
    directory_path = '.\mastDownload\HST\{}'.format(fileNameDelete)
    print('Preparing to delete {}'.format(directory_path))

    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
        print("{} is deleted!".format(directory_path))
    else:
        print("Warning: {} has already been deleted".format(directory_path))


if __name__ == '__main__':
    connect_session()

    with open('tablea1.dat', 'r') as file:
        lines = file.readlines()
    file.close()

    # Generate a FileManager object, and configure the number of FITS file
    # you want to store at one time on your disk
    manager = FileManager(8)

    # Configure the number of start line (which is the index for file names)
    index = 122
    lines = lines[index:]

    for line in lines:
        # Get the parameter (obsID and asteroid position)
        obsID, ra1, dec1, ra2, dec2 = get_par(line, index)

        # Check which file to delete in this iteration
        fileNameDelete = manager.update_list(obsID)

        # Delete the directory if expected
        if fileNameDelete != 0:
            delete_dir(fileNameDelete)

        # Download FITS file, and get the path
        path = download_file(obsID)

        # Check if the FITS file exists
        if os.path.isfile(path) == False:
            print('Error: No file found for {}-{}'.format(index, obsID))
            index += 1
            continue

        # Acquire the data, and convert the coordinate system for asteroid position
        data, x1, y1, x2, y2 = convert_world2pix(path, ra1, dec1, ra2, dec2)

        # Save the data and position to .npz file
        save_data(obsID, index, data, x1, y1, x2, y2)

        # Plot the data and save the figure to a jpg file
        plot_data(data, obsID, index, x1, y1, x2, y2)

        # Finished!
        print('{}-{} finished!'.format(index, obsID))

        # Increase the index by one
        index += 1

        # Stop the code
        if index > 200:
            break
