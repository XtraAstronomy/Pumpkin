'''
Python script to create lightcurves from the background
'''
import os
from ciao_contrib.runtool import *
#from pychips import *
#from pychips.hlui import *
from pycrates import *
from lightcurves import *
import matplotlib.pyplot as plt

def bkg_clean_srcs(bkg_ccd):
    '''
    Remove any pt sources from the background CCD
    '''
    try:
        vtpdetect.punlearn()
        vtpdetect.infile = bkg_ccd+'.fits'
        vtpdetect.outfile = bkg_ccd+'_src.fits'
        vtpdetect.regfile = bkg_ccd+'_src.reg'
        vtpdetect.clobber = True
        vtpdetect()

        dmcopy.punlearn()
        dmcopy.infile = bkg_ccd+'.fits[exclude sky=region('+bkg_ccd+'_src.reg)]'
        dmcopy.outfile = bkg_ccd+'_bkg.fits'
        dmcopy.clobber = True
        dmcopy()
    except OSError:
        dmcopy.punlearn()
        dmcopy.infile = bkg_ccd+'.fits'
        dmcopy.outfile = bkg_ccd+'_bkg.fits'
        dmcopy.clobber = True
        dmcopy()

    return None


def bkg_lightcurve(bkg_ccd,obsid):
    '''
    Create and plot background lightcurve. Then create good-time-interval file
    '''
    #Create Lightcurve
    dmextract.punlearn()
    dmextract.infile = bkg_ccd+'_bkg.fits[bin time=::200]'
    dmextract.outfile = bkg_ccd+'_bkg.lc'
    dmextract.opt = 'ltc1'
    dmextract.clobber = True
    dmextract.verbose = 0
    dmextract()
    #Plot Lightcurve using CHIPS
    '''add_window()
    make_figure(bkg_ccd+'_bkg.lc[cols dt, count_rate]')
    set_curve(["symbol.style", "none"])
    set_plot_title("Light Curve")
    set_plot_xlabel(r"\Delta T (s)")
    set_plot_ylabel("Rate (count s^{-1})")
    set_preference("export.clobber", "yes")
    print_window(bkg_ccd+'_bkg_lc.png')
    clear()
    add_window()'''
    #Clip image
    lc_sigma_clip(bkg_ccd+'_bkg.lc',bkg_ccd+'_bkg_clean.gti',plot=True,sigma=3,pattern="none",verbose=0)
    #print_window(obsid+'_Lightcurve.png')
    plt.savefig(obsid+'_Lightcurve.png')
    plt.clf()
    return None
