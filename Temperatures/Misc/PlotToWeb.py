'''
A simple file to collect all the images we want for the website and move them
to the website directory
'''

import os
import shutil


def plots_to_web(dir,obsids,name,web_dir):
    #Move individual obsid images
    if not os.path.exists(web_dir):
        os.mkdir(web_dir)
    for obsid in obsids:
        os.chdir(dir+'/'+obsid+'/Background')
        shutil.copyfile(obsid+'_ccds.png',web_dir+'/'+obsid+'_ccds.png')
        shutil.copyfile(obsid+'_Lightcurve.png',web_dir+'/'+obsid+'_Lightcurve.png')
    #Cluster images
    os.chdir(dir+'/'+name)
    shutil.copyfile('bkgsub_exp.png',web_dir+'/'+'bkgsub_exp.png')
    #Spectroscopic info
    os.chdir(dir+'/'+name+'/Fits/Plots')
    plts = ['Abundance','Density','Entropy','Pressure','T_Cool','Temperature']
    for plt_ in plts:
        shutil.copyfile(plt_+'_profile.png',web_dir+'/'+plt_+'_profile.png')
    #Photometric info
    os.chdir(dir+'/'+name+'/SurfaceBrightness')
    shutil.copyfile('Single_Beta.png',web_dir+'/'+'Single_Beta.png')
    shutil.copyfile('Double_Beta.png',web_dir+'/'+'Double_Beta.png')
    return None
