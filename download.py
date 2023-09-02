from astropy.io import fits
from astropy.wcs import WCS
import matplotlib.pyplot as plt
from astroquery.mast import Observations
import getpass
import os


# read the FITS file, return the data and WCS object
def read_fits(fileName):
    hdulist = fits.open(fileName)
    data = hdulist[1].data
    wcs = WCS(hdulist[1].header)
    hdulist.close()

    return data, wcs


# Get the parameter from each line of the tablea1.dat file
def get_par(line):
    obsID = line[8:17]
    ra1 = float(line[103:114])
    dec1 = float(line[115:126])
    ra2 = float(line[127:138])
    dec2 = float(line[139:150])
    return obsID, ra1, dec1, ra2, dec2


# Convert the position in the astronomy coordinate system to pixel position
def convert_world2pix(path, ra1, dec1, ra2, dec2):
    data, wcs = read_fits(path)

    x1, y1 = wcs.all_world2pix(ra1, dec1, 1)
    x2, y2 = wcs.all_world2pix(ra2, dec2, 1)

    return data, x1, y1, x2, y2


# Plot a draft of data, with red box pointing out the asteroid
def plot_data(data, obsID, num, x1, y1, x2, y2):
    plt.imshow(data, cmap='gray', vmin=0.0, vmax=0.01)
    plt.plot([x1, x2], [y1, y1], 'r')
    plt.plot([x1, x2], [y2, y2], 'r')
    plt.plot([x1, x1], [y1, y2], 'r')
    plt.plot([x2, x2], [y1, y2], 'r')
    plt.colorbar()
    plt.savefig('.\pic\{}-{}.jpg'.format(num, obsID), dpi=300)
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


if __name__ == '__main__':
    connect_session()
    with open('tablea1.dat', 'r') as file:
        num = 1
        for line in file:
            obsID, ra1, dec1, ra2, dec2 = get_par(line)
            print(obsID)
            download_file(obsID)
            path = '.\mastDownload\HST\{}\{}_drc.fits'.format(obsID, obsID)
            if os.path.isfile(path) == False:
                print('Error: No file found at obsID {}'.format(obsID))
                continue
            data, x1, y1, x2, y2 = convert_world2pix(
                path, ra1, dec1, ra2, dec2)
            plot_data(data, obsID, num, x1, y1, x2, y2)
            print('{} finished!'.format(obsID))
            if num > 5:
                break
            num += 1
    file.close()
