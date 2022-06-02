'''
Creation of several auxilary plots that aren't created during the normal execution
of the pipeline for the sake of expediency. However, we think these plots are useful.
'''
#------------------------IMPORTS-----------------------------#
import os
import numpy as np
from astropy.io import fits
from astropy.table import Table
import matplotlib.pyplot as plt
from ciao_contrib.runtool import *
from astropy.convolution import Gaussian2DKernel, convolve
#------------------------------------------------------------#
def bkg_image(directory,image,bkg_reg,filenames):
    '''
    Create an image of the chosen background region
    param: directory - main directory to save image
    param: image - image fits file. Cleaned and background subtracted
    param: bkg_reg - .reg file containing background region selection
    '''
    f, ax = plt.subplots()

    image_data = fits.getdata(image)
    kernel = Gaussian2DKernel(x_stddev=3)
    astropy_conv = convolve(image_data, kernel)
    #get background info
    bkg_cntr = []; bkg_rad = 0;
    with open(bkg_reg,'r') as bkg_file:
        bkg_data = bkg_file.readlines()[-1].split(',')
        bkg_cntr.append(float(bkg_data[0].split('(')[1]))
        bkg_cntr.append(float(bkg_data[1]))
        bkg_rad = float(bkg_data[2].split(")")[0])

    ax.imshow(np.arcsinh(astropy_conv), cmap='gist_heat',vmax=np.max(np.arcsinh(astropy_conv))/10)

    circle = plt.Circle((bkg_cntr[0], bkg_cntr[1]), bkg_rad, color='green', fill=False)
    ax.add_artist(circle)
    scale = 5
    ax.set_xlim(bkg_cntr[0]-scale*bkg_rad,bkg_cntr[0]+scale*bkg_rad)
    ax.set_ylim(bkg_cntr[1]-scale*bkg_rad,bkg_cntr[1]+scale*bkg_rad)
    ax.set_axis_off()
    plt.savefig(directory+'/bkg_region.png',bbox_inches='tight')
