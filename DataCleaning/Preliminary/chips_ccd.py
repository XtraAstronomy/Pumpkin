'''
Create window with all ccds
'''

import os
import matplotlib.pyplot as plt
import easygui as gui
import numpy as np
from pycrates import *
#from pychips.all import *
from shutil import copyfile
from ciao_contrib.smooth import *
from ciao_contrib.runtool import *
import matplotlib.image as mpimg

from astropy.io import fits
from matplotlib.colors import LogNorm
from astropy.table import Table
from astropy.convolution import Gaussian2DKernel, convolve
#-----------------------------CLASSES----------------------------------#
class AGN:
    '''
    Class to handle potential AGN. We must contain the central point of the AGN
    and its radius. We also will have a boolean to say whether or not we have an
    AGN in the ICM.
    :param active - AGN or no AGN
    :param center - physical coordinates of AGN center
    :param radius - radius in arcseconds
    '''
    def __init__(self,active):
        self.active = active
        self.x_coord = 0
        self.y_coord = 0
        self.radius = 0
    def set_AGN(self,center_x,center_y,radius):
        self.active = True
        self.x_coord = center_x
        self.y_coord = center_y
        self.radius = radius
#--------------------------Auxilary Functions--------------------------#
def max_counts(image):
    '''Maximum counts in image'''
    dmstat.punlearn()
    dmstat.infile = image
    dmstat.centroid = True
    dmstat()
    return int(dmstat.out_max)

def max_coord(image,coord):
    '''Maximum coordinate for image'''
    dmstat.punlearn()
    dmstat.infile = image+'[cols '+coord+']'
    dmstat()
    return float(dmstat.out_max)

def min_coord(image,coord):
    '''Minimum coordinate for image'''
    dmstat.punlearn()
    dmstat.infile = image+'[cols '+coord+']'
    dmstat()
    return float(dmstat.out_min)
#--------------------------Primary Functions--------------------------#
def display_ccds(ccd_list,obsid,Merge=False):
    '''
    Display all CCDS together
    PARAMETERS:
        ccd_list - list of ccd numbers
        obsid - current Chandra observation ID
    '''
    #add_window(32,32)
    #split(2,int(len(ccd_list[obsid])/2)+1)
    if len(ccd_list[obsid])%2 == 0:
        col_num = int(len(ccd_list[obsid])/2)
    else:
        col_num = int((len(ccd_list[obsid])+1)/2)
    f, ax = plt.subplots(2,col_num)
    ccd_count = 0
    full_ccd_list = ['ccd'+i for i in ccd_list[obsid]]
    #Go through each ccd in the list
    max_val = 0 #max for scale
    for ccd in full_ccd_list:
        print('      Creating image for CCD %s'%ccd)
        if ccd_count < col_num:
            rw = 0
        else:
            rw = 1
        ccd_moded = ccd_count%col_num
        hdu_list = fits.open(ccd+'.fits', memmap=True)
        evt_data = Table(hdu_list[1].data)
        min_x = np.min(evt_data['x'])
        min_y = np.min(evt_data['y'])
        max_x = np.max(evt_data['x'])
        max_y = np.max(evt_data['y'])
        print('Getting Data')
        image_data = fits.getdata(ccd+'.img')
        #kernel = Gaussian2DKernel(x_stddev=3)
        print('Convolving')
        #astropy_conv = convolve(image_data, kernel)
        print('Plotting')
        #ax[rw,ccd_moded].imshow(np.arcsinh(astropy_conv), cmap='gist_heat', vmin=0,vmax=np.max(np.arcsinh(astropy_conv))/5)
        ax[rw,ccd_moded].imshow(np.arcsinh(image_data), cmap='gist_heat', vmin=0,vmax=np.max(np.arcsinh(image_data))/5)
        ax[rw,ccd_moded].set_xlim(min_x,max_x)
        ax[rw,ccd_moded].set_ylim(min_y,max_y)
        ax[rw,ccd_moded].text(min_x,min_y,ccd,fontsize=15,color='white')
        ax[rw,ccd_moded].set_axis_off()
        #if np.max(np.arcsinh(astropy_conv)) > max_val:
        #    max_val = np.max(np.arcsinh(astropy_conv))
        print('Next')
        ccd_count += 1
    f.subplots_adjust(hspace=0)
    outfile_name = str(obsid)+"_ccds.png"
    plt.savefig(outfile_name); plt.close()
    plt.imshow(mpimg.imread(str(obsid)+"_ccds.png")); plt.ion(); plt.show()
    msg = "Which CCD should be used for Background Flare Extraction?"
    bkg_ccd = gui.buttonbox(msg, choices=full_ccd_list)
    if Merge == False:
        msg = "Which CCD should be used for Source Centroid Extraction?"
        src_ccd = gui.buttonbox(msg, choices=full_ccd_list)
        plt.clf()
        plt.close()
        return bkg_ccd,src_ccd
    else:
        plt.clf()
        plt.close()
        return bkg_ccd



def display_entire(home_dir,OBSID,repro_img):
    '''
    Display normal image from reprocessed Chandra data
    PARAMETERS:
        home_dir - directory containing Chandra data
        OBSID - current Chandra observation ID
        repro_evt - name of the reprocessed event
    '''
    #plot image file
    point_srcs = True
    add_window(32,32)
    cr = read_file(repro_img)
    img = copy_piximgvals(cr)
    set_piximgvals(cr, gsmooth(img, 3)) #smooth
    pvalues = get_piximgvals(cr)
    add_image(np.arcsinh(pvalues)) #scale
    set_image(["threshold", [0, np.max(np.arcsinh(pvalues))/3]])
    set_image(["colormap", "cool"])
    #Actively choose diffuse emission
    msg = "Please pick the extent of the diffuse emission..."
    gui.ccbox(msg)
    coords = get_pick()


    #find any point sources contaminating the diffuse emission
    ptsrc_file = open('pt_srcs.reg','w+')
    ptsrc_file.write("# Region file format: DS9 version 4.1 \n")
    ptsrc_file.write("image \n")
    #Also see if it is the central AGN
    agn_ = AGN(False)
    agn_file = open('AGN.reg','w+')
    agn_file.write("# Region file format: DS9 version 4.1 \n")
    agn_file.write("image \n")
    pt_srcs_num = 0
    while point_srcs == True:
        if pt_srcs_num == 0:
            msg = "Are there any point sources in the src CCD?"
        else:
            msg = "Are there any other point sources in the src CCD?"
        point_srcs = gui.ynbox(msg)
        if point_srcs == True:
            msg = "Please pick the point source and then the extent of the source after pressing continue..."
            gui.ccbox(msg)
            pt_src_coord = get_pick() #in logical
            add_point(pt_src_coord[0], pt_src_coord[1], ["style", "cross", "color", "green"])
            pt_src_edge = get_pick()
            add_point(pt_src_edge[0], pt_src_edge[1], ["style", "cross", "color", "green"])
            #Get physical Coordinates
            dmcoords.punlearn()
            dmcoords.infile = repro_img # OBSID+'_broad_thresh.img'
            dmcoords.option = 'logical'
            dmcoords.logicalx = pt_src_coord[0][0]
            dmcoords.logicaly = pt_src_coord[1][0]
            dmcoords()
            pt_src_coord_ra = dmcoords.ra
            pt_src_coord_dec = dmcoords.dec
            #Calculate the radius in physical units
            pt_src_coord_x = dmcoords.x
            pt_src_coord_y = dmcoords.y
            dmcoords.punlearn()
            dmcoords.infile = repro_img # OBSID+'_broad_thresh.img'
            dmcoords.option = 'logical'
            dmcoords.logicalx = pt_src_edge[0][0]
            dmcoords.logicaly = pt_src_edge[1][0]
            dmcoords()
            pt_src_edge_x = dmcoords.x
            pt_src_edge_y = dmcoords.y
            radius = np.sqrt((float(pt_src_coord_x)-float(pt_src_edge_x))**2+(float(pt_src_coord_y)-float(pt_src_edge_y))**2)
            radius = 0.492*radius #physical to arcsec
            ptsrc_file.write('circle(%s,%s,%.2f) \n'%(pt_src_coord_ra,pt_src_coord_dec,radius))
            pt_srcs_num += 1
            #msg = "Is the point src the central AGN?"
            #AGN_msg = gui.ynbox(msg)
            #if AGN_msg == True:
            #    agn_file.write('circle(%s,%s,%.2f) \n'%(pt_src_coord[0][0],pt_src_coord[1][0],radius))
            #    agn_.set_AGN(pt_src_coord[0][0],pt_src_coord[1][0],radius)
    agn_file.close()
    ptsrc_file.close()
    #move to background directory for later
    copyfile('pt_srcs.reg',home_dir+'/'+OBSID+'/Background/pt_srcs.reg')
    set_plot_title("")
    #print_window(home_dir+'/'+OBSID+'/bkg.png', ['clobber', 'yes'])
    clear()
    return coords[0][0],coords[1][0],agn_


def display_merge(merged_dir,merged_img):
    '''
    Display normal image from reprocessed Chandra data after merge
    PARAMETERS:
        merged_dir - directory containing merged Chandra data
        merged_evt - merged event file name
    '''
    os.chdir(merged_dir)
    point_srcs = True
    '''merged_img = merged_evt.split('.')[0]+'.img'
    #Create merged image
    dmcopy.punlearn()
    dmcopy.infile = merged_evt
    dmcopy.outfile = merged_img
    dmcopy.option = 'image'
    dmcopy.clobber = True
    dmcopy()'''
    #Plot and such
    add_window(32,32)
    #max_cts = max_counts(merged_img)
    cr = read_file(merged_img)
    img = copy_piximgvals(cr)
    set_piximgvals(cr, gsmooth(img, 3)) #smooth
    pvalues = get_piximgvals(cr)
    add_image(np.sqrt(pvalues)) #scale
    set_image(["threshold", [0, np.sqrt(np.max(pvalues))/2]])
    set_image(["colormap", "cool"])
    #Actively choose diffuse emission
    msg = "Please pick the extent of the diffuse emission..."
    gui.ccbox(msg)
    coords_edge = get_pick()


    #add source region to image
    add_point(coords_edge[0], coords_edge[1], ["style", "cross", "color", "red"])

    #check for contaminating pt srcs in diffuse emission and log them
    ptsrc_file = open('pt_srcs.reg','w+')
    ptsrc_file.write("# Region file format: DS9 version 4.1 \n")
    ptsrc_file.write("image \n")
    #Also see if it is the central AGN
    agn_ = AGN(False)
    agn_file = open('AGN.reg','w+')
    agn_file.write("# Region file format: DS9 version 4.1 \n")
    agn_file.write("image \n")
    pt_srcs_num = 0
    while point_srcs == True:
        if pt_srcs_num == 0:
            msg = "Are there any point sources in the src CCD?"
        else:
            msg = "Are there any other point sources in the src CCD?"
        point_srcs = gui.ynbox(msg)
        if point_srcs == True:
            msg = "Please pick the point source and then the extent of the source after pressing continue..."
            gui.ccbox(msg)
            pt_src_coord = get_pick()
            add_point(pt_src_coord[0], pt_src_coord[1], ["style", "cross", "color", "green"])
            pt_src_edge = get_pick()
            add_point(pt_src_edge[0], pt_src_edge[1], ["style", "cross", "color", "green"])
            #Get physical Coordinates
            dmcoords.punlearn()
            dmcoords.infile = merged_img # OBSID+'_broad_thresh.img'
            dmcoords.option = 'logical'
            dmcoords.logicalx = pt_src_coord[0][0]
            dmcoords.logicaly = pt_src_coord[1][0]
            dmcoords()
            pt_src_coord_ra = dmcoords.ra
            pt_src_coord_dec = dmcoords.dec
            #Calculate the radius in physical units
            pt_src_coord_x = dmcoords.x
            pt_src_coord_y = dmcoords.y
            dmcoords.punlearn()
            dmcoords.infile = merged_img # OBSID+'_broad_thresh.img'
            dmcoords.option = 'logical'
            dmcoords.logicalx = pt_src_edge[0][0]
            dmcoords.logicaly = pt_src_edge[1][0]
            dmcoords()
            pt_src_edge_x = dmcoords.x
            pt_src_edge_y = dmcoords.y
            radius = np.sqrt((float(pt_src_coord_x)-float(pt_src_edge_x))**2+(float(pt_src_coord_y)-float(pt_src_edge_y))**2)
            radius = 0.492*radius #physical to arcsec
            ptsrc_file.write('annulus(%s,%s,0.0,%f) \n'%(pt_src_coord_ra,pt_src_coord_dec,radius))
            pt_srcs_num += 1
    agn_file.close()
    ptsrc_file.close()
    dmcoords.punlearn()
    dmcoords.infile = merged_img # OBSID+'_broad_thresh.img'
    dmcoords.option = 'logical'
    dmcoords.logicalx = coords_edge[0][0]
    dmcoords.logicaly = coords_edge[1][0]
    dmcoords()
    pt_src_coord_ra = dmcoords.ra
    pt_src_coord_dec = dmcoords.dec
    clear()
    return pt_src_coord_ra,pt_src_coord_dec,agn_
