# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

def radial_profile(data, center=(0,0)):
    y,x = np.indices((data.shape)) # first determine radii of all pixels
    r = np.sqrt((x-center[0])**2+(y-center[1])**2)

    ind = np.argsort(r.flat) # get sorted indices

    sr = r.flat[ind] # sorted radii

    sim = data.flat[ind] # image values sorted by radii

    ri = sr.astype(np.int32) # integer part of radii (bin size = 1)

    # determining distance between changes
    deltar = ri[1:] - ri[:-1] # assume all radii represented

    rind = np.where(deltar)[0] # location of changed radius

    nr = rind[1:] - rind[:-1] # number in radius bin

    csim = np.cumsum(sim, dtype=np.float64) # cumulative sum to figure out sums for each radii bin

    tbin = csim[rind[1:]] - csim[rind[:-1]] # sum for image values in radius bins
    radialprofile = tbin/nr # the answer

    return radialprofile

def mean_function(image, center=None):
    # create array of radii
    #x, y = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
    y,x = np.indices((image.shape)) # first determine radii of all pixels


    #i, j = np.meshgrid(range(image.shape[0]), range(image.shape[1]), indexing='ij')
    #y, x = (i-image.shape[0]//2, j-image.shape[1]//2)

    if center is not None:
        R = np.sqrt((x-center[0])**2+(y-center[1])**2)
    else:
        R = np.sqrt(x**2+y**2)

    ind = np.argsort(R.flat) # get sorted indices

    sr = R.flat[ind] # sorted radii

    ri = sr.astype(np.int32) # integer part of radii (bin size = 1)

    ri = np.array(list(set(ri)))

    # calculate the mean
    #f = lambda r: image[(R >= r - .5) & (R < r + .5)].mean()
    f = lambda r: np.nanmedian(image[(R >= r - 2.5) & (R < r + 2.5)])

    mean = np.vectorize(f)(ri)

    return ri, mean


def radial_symetry(background, rs=None, is_fft_shifted=True):
    if rs is None:
        i = np.fft.fftfreq(background.shape[0]) * background.shape[0]
        j = np.fft.fftfreq(background.shape[1]) * background.shape[1]
        k = np.fft.fftfreq(background.shape[2]) * background.shape[2]
        i, j, k = np.meshgrid(i, j, k, indexing='ij')
        rs = np.sqrt(i ** 2 + j ** 2 + k ** 2).astype(np.int16)

        if is_fft_shifted is False:
            rs = np.fft.fftshift(rs)
        rs = rs.ravel()

    ########### Find the radial average
    # get the r histogram
    r_hist = np.bincount(rs)
    # get the radial total
    r_av = np.bincount(rs, background.ravel())
    # prevent divide by zero
    nonzero = np.where(r_hist != 0)
    zero = np.where(r_hist == 0)
    # get the average
    r_av[nonzero] = r_av[nonzero] / r_hist[nonzero].astype(r_av.dtype)
    r_av[zero] = 0

    ########### Make a large background filled with the radial average
    background = r_av[rs].reshape(background.shape)
    return background, rs, r_av

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    import h5py as h5

    h = h5.File('LA93-r0014-CxiDs1-darkcal.h5', 'r')
    img = h['data/data'][:]
    #img = plt.imread('load2sam5lev1_scan_001.tif', 0)
    print(img.shape, type(img))

    #rad = radial_profile(img)

    #plt.plot(rad[:])
    #plt.show()

    #r, rad2 = mean_function(img)

    y, x = np.indices((img.shape))
    rs = np.rint(np.sqrt(x**2+y**2)).astype(np.int).ravel()
    background, rs, r_av = radial_symetry(img, rs)

    print(r_av.shape)

    plt.plot(r_av)
    plt.show()

