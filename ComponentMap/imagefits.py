"""
Python Subroutine to create a fits image from the bin map labelled by the
number of underlying thermal Components
"""
from astropy.io import fits
import numpy as np
#-------------------------------------------------#
#-------------------------------------------------#
class Bin:
    def __init__(self, number):
        self.bin_number = number
        self.pixels = []
        self.temp = 0
        self.percentage = 0
        self.stat = 0
        self.abund = 0
    def add_pixel(self,pixel):
        self.pixels.append(pixel)
    def add_temp(self,temp):
        self.temp = temp
    def add_percentage(self,percentage):
        self.percentage = percentage
    def add_stat(self,stat):
        self.stat = stat
    def add_abund(self, abund):
        self.abund = abund


class Pixel:
    def __init__(self, number, pix_x, pix_y):
        self.pix_number = number
        self.pix_x = pix_x
        self.pix_y = pix_y
#-------------------------------------------------#

def read_in(bin_data,temp_data):
    bin_d = open(bin_data); next(bin_d); next(bin_d) #first two lines are header info
    temp_d = open(temp_data); next(temp_d)
    bins = []
    pixels = []
    pixel_num = 0
    #Create bins and add pixels
    for line in bin_d:
        if int(line.split(" ")[2]) not in [bin.bin_number for bin in bins]:
            bins.append(Bin(int(line.split(" ")[2])))
        pixel_ = Pixel(pixel_num,int(line.split(" ")[0]),int(line.split(" ")[1]))
        pixels.append(pixel_)
        bins[int(int(line.split(" ")[2]))].add_pixel(pixel_)
        pixel_num += 1
    #Add temperatures and Reduced Chi Squares to bins
    for line in temp_d:
        #try:
        bins[int(int(line.split(" ")[0]))].add_temp(line.split(" ")[1].strip('\n'))
        bins[int(int(line.split(" ")[0]))].add_percentage(float(line.split(" ")[2].strip('\n'))/2)
        #except:
            #print(int(int(line.split(" ")[0])))
            #break
            #pass
    temp_d.close()
    bin_d.close()
    min_x = np.min([pixel.pix_x for pixel in pixels])
    max_x = np.max([pixel.pix_x for pixel in pixels])
    min_y = np.min([pixel.pix_y for pixel in pixels])
    max_y = np.max([pixel.pix_y for pixel in pixels])
    return bins, min_x, max_x, min_y, max_y



def create_image_fits(base_dir,fits_img,outroot, bin_file, temp_file):
    """
    base_dir - Full path to cluster data
    fits_img - Fits image used to create WVT map (used for header information)
    outroot - Output directory root
    bin_file - WVT bin file
    temp_file - file containing the number of underlying thermal components
    """
    bins, min_x, max_x, min_y, max_y = read_in(base_dir+'/'+bin_file,base_dir+'/'+temp_file)
    # Create image array
    x_len = int(max_x-min_x)
    y_len = int(max_y-min_y)
    temp_array = np.zeros((x_len,y_len))
    percentage_array = np.zeros((x_len,y_len))
    for bin in bins:
        for pixel in bin.pixels:
            #print(bin.temp)
            try:
                temp_array[int(pixel.pix_x-1),int(pixel.pix_y-1)] = int(bin.temp)
                percentage_array[int(pixel.pix_x-1),int(pixel.pix_y-1)] = float(bin.percentage)
            except:
                #print(bin.temp)
                pass
    # Copy header
    fits_ = fits.open(base_dir+'/'+fits_img)
    hdr = header=fits_[0].header
    # Change image
    hdu = fits.PrimaryHDU(temp_array)
    hdul = fits.HDUList([hdu])
    fits.writeto(base_dir+'/component_bins.fits', temp_array.T, hdr, overwrite=True)
    fits.writeto(base_dir+'/percentage_bins.fits', percentage_array.T, hdr, overwrite=True)
