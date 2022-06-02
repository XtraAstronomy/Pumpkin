'''
------------------------------------------------------
GOAL:
    Step through bins (spectra) and calculate the temperature value
    of each bin using XSPEC
------------------------------------------------------
INPUTS:
    dir - Full Path to Main Directory (e.g. '/home/user/Documents/Chandra/12833/repro/binned/')
    file_name - FIlename of PI/PHA spectrum (e.g. 'imageA')
    output_file - Filename for output containing temperature information (e.g. 'Temp_bin')
    num_files - number of bins (e.g. 100)
    redshift - redshift of object (e.g. 0.659)
    n_H - Hydrogen Equivalent Column Density in units of 10^{22} atoms cm^{-2} (e.g. 3.6e-2)
    Temp_guess - Guess for Temperature value in units of KeV (e.g. 5)
------------------------------------------------------
OUTPUTS:
    A file which contains the bin number and associated
    temperature and reduced chi-squared
------------------------------------------------------
ADDITIONAL NOTES:
    Be sure to run heainit first
------------------------------------------------------
'''
#from astropy.io import fits
import os
import subprocess
from sherpa.optmethods import LevMar
from sherpa.stats import LeastSq
from sherpa.plot import DataPlot
from sherpa.astro.xspec import *
from sherpa.astro.all import *
from sherpa.astro.ui import *
from sherpa.all import *
from multiprocessing import Process, JoinableQueue
from joblib import Parallel, delayed
from tqdm import tqdm
from Classes import region
#TURN OFF ON-SCREEN OUTPUT FROM SHERPA
import logging
logger = logging.getLogger("sherpa")
logger.setLevel(logging.WARN)
logger.setLevel(logging.ERROR)
def set_log_sherpa():
    p = get_data_plot_prefs()
    p["xlog"] = True
    p["ylog"] = True
    return None

def isFloat(string):
    if string == None:
        return False
    try:
        float(string)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


#------------------------------INPUTS------------------------------------------#

#------------------------------------------------------------------------------#
#Dynamically set source for OBSID
# HERE WE DEFINE THE MODELS FOR THE FOREGROUND AND BACKGROUND
def obsid_set(src_model_dict,bkg_model_dict,obsid, bkg_spec,obs_count,redshift,nH_val,Temp_guess):
    load_pha(obs_count,obsid) #Read in
    if obs_count == 1:
        src_model_dict[obsid] = xsphabs('abs'+str(obs_count)) * xsapec('apec'+str(obs_count)) #set model and name
        # Change src model component values
        get_model_component('apec' + str(obs_count)).kT = Temp_guess
        get_model_component('apec' + str(obs_count)).redshift = redshift  # need to tie all together
        get_model_component('apec' + str(obs_count)).Abundanc = 0.3
        thaw(get_model_component('apec' + str(obs_count)).Abundanc)
        get_model_component('abs1').nH = nH_val  # change preset value
        freeze(get_model_component('abs1'))
    else:
        src_model_dict[obsid] = get_model_component('abs1') * xsapec('apec' + str(obs_count))
        get_model_component('apec'+str(obs_count)).kT = get_model_component('apec1').kT #link to first kT
        get_model_component('apec' + str(obs_count)).redshift = redshift
        get_model_component('apec' + str(obs_count)).Abundanc = get_model_component('apec1').Abundanc  # link to first kT

    bkg_model_dict[obsid] = xsapec('bkgApec'+str(obs_count))+get_model_component('abs1')*xsbremss('brem'+str(obs_count))
    set_bkg(obs_count, unpack_pha(bkg_spec))
    set_source(obs_count, src_model_dict[obsid]) #set model to source
    set_bkg_model(obs_count,bkg_model_dict[obsid])
    #Change bkg model component values
    get_model_component('bkgApec' + str(obs_count)).kT = 0.18
    freeze(get_model_component('bkgApec'+str(obs_count)).kT)
    get_model_component('brem' + str(obs_count)).kT = 40.0
    freeze(get_model_component('brem' + str(obs_count)).kT)
    return None
#------------------------------------------------------------------------------#
def obsid_set2(src_model_dict,bkg_model_dict,obsid, obs_count,redshift,nH_val,Temp_guess):
    '''
    Add two thermal emission models
    '''
    load_pha(obs_count,obsid) #Read in
    if obs_count == 1:
        src_model_dict[obsid] = xsphabs('abs'+str(obs_count)) * (xsapec('apec1_'+str(obs_count)) + xsapec('apec2_'+str(obs_count))) #set model and name
        # Change src model component values
        get_model_component('apec1_' + str(obs_count)).kT = 1
        get_model_component('apec1_' + str(obs_count)).redshift = redshift  # need to tie all together
        get_model_component('apec1_' + str(obs_count)).Abundanc = 0.3
        thaw(get_model_component('apec1_' + str(obs_count)).Abundanc)
        get_model_component('apec2_' + str(obs_count)).kT = 2.0
        get_model_component('apec2_' + str(obs_count)).redshift = redshift  # need to tie all together
        get_model_component('apec2_' + str(obs_count)).Abundanc = 0.3#get_model_component('apec1_1').Abundanc
        thaw(get_model_component('apec2_' + str(obs_count)).Abundanc)
        #thaw(get_model_component('apec2_' + str(obs_count)).Abundanc)
        get_model_component('abs1').nH = nH_val  # change preset value
        freeze(get_model_component('abs1'))
    else:
        src_model_dict[obsid] = get_model_component('abs1') * (xsapec('apec1_'+str(obs_count)) + xsapec('apec2_'+str(obs_count)))
        get_model_component('apec1_'+str(obs_count)).kT = get_model_component('apec1_1').kT #link to first kT
        get_model_component('apec1_' + str(obs_count)).redshift = redshift
        get_model_component('apec1_' + str(obs_count)).Abundanc = get_model_component('apec1_1').Abundanc  # link to first kT
        get_model_component('apec2_'+str(obs_count)).kT = get_model_component('apec2_1').kT #link to first kT (second thermal)
        get_model_component('apec2_' + str(obs_count)).redshift = redshift
        get_model_component('apec2_' + str(obs_count)).Abundanc = get_model_component('apec2_1').Abundanc  # link to first kT (second thermal)

    bkg_model_dict[obsid] = xsapec('bkgApec'+str(obs_count))+get_model_component('abs1')*xsbremss('brem'+str(obs_count))
    set_source(obs_count, src_model_dict[obsid]) #set model to source
    set_bkg_model(obs_count,bkg_model_dict[obsid])
    #Change bkg model component values
    get_model_component('bkgApec' + str(obs_count)).kT = 0.18
    freeze(get_model_component('bkgApec'+str(obs_count)).kT)
    get_model_component('brem' + str(obs_count)).kT = 40.0
    freeze(get_model_component('brem' + str(obs_count)).kT)
    return None
#------------------------------------------------------------------------------#
def obsid_set3(src_model_dict,bkg_model_dict,obsid, obs_count,redshift,nH_val,Temp_guess):
    '''
    Add three thermal emission models
    '''
    load_pha(obs_count,obsid) #Read in
    if obs_count == 1:
        src_model_dict[obsid] = xsphabs('abs'+str(obs_count)) * (xsapec('apec1_'+str(obs_count)) + xsapec('apec2_'+str(obs_count))+ xsapec('apec3_'+str(obs_count))) #set model and name
        # Change src model component values
        get_model_component('apec1_' + str(obs_count)).kT = 1
        get_model_component('apec1_' + str(obs_count)).redshift = redshift  # need to tie all together
        get_model_component('apec1_' + str(obs_count)).Abundanc = 0.3
        thaw(get_model_component('apec1_' + str(obs_count)).Abundanc)
        get_model_component('apec2_' + str(obs_count)).kT = 2
        get_model_component('apec2_' + str(obs_count)).redshift = redshift  # need to tie all together
        get_model_component('apec2_' + str(obs_count)).Abundanc = 0.3
        thaw(get_model_component('apec2_' + str(obs_count)).Abundanc)
        get_model_component('apec3_' + str(obs_count)).kT = 3
        get_model_component('apec3_' + str(obs_count)).redshift = redshift  # need to tie all together
        get_model_component('apec3_' + str(obs_count)).Abundanc = 0.3
        thaw(get_model_component('apec3_' + str(obs_count)).Abundanc)
        get_model_component('abs1').nH = nH_val  # change preset value
        freeze(get_model_component('abs1'))
    else:
        src_model_dict[obsid] = get_model_component('abs1') * (xsapec('apec1_'+str(obs_count)) + xsapec('apec2_'+str(obs_count))+ xsapec('apec3_'+str(obs_count)))
        get_model_component('apec1_'+str(obs_count)).kT = get_model_component('apec1_1').kT #link to first kT
        get_model_component('apec1_' + str(obs_count)).redshift = redshift
        get_model_component('apec1_' + str(obs_count)).Abundanc = get_model_component('apec1_1').Abundanc  # link to first kT
        get_model_component('apec2_'+str(obs_count)).kT = get_model_component('apec2_1').kT #link to first kT (second thermal)
        get_model_component('apec2_' + str(obs_count)).redshift = redshift
        get_model_component('apec2_' + str(obs_count)).Abundanc = get_model_component('apec2_1').Abundanc  # link to first kT (second thermal)
        get_model_component('apec3_'+str(obs_count)).kT = get_model_component('apec3_1').kT #link to first kT (third thermal)
        get_model_component('apec3_' + str(obs_count)).redshift = redshift
        get_model_component('apec3_' + str(obs_count)).Abundanc = get_model_component('apec3_1').Abundanc  # link to first kT (third thermal)

    bkg_model_dict[obsid] = xsapec('bkgApec'+str(obs_count))+get_model_component('abs1')*xsbremss('brem'+str(obs_count))
    set_source(obs_count, src_model_dict[obsid]) #set model to source
    set_bkg_model(obs_count,bkg_model_dict[obsid])
    #Change bkg model component values
    get_model_component('bkgApec' + str(obs_count)).kT = 0.18
    freeze(get_model_component('bkgApec'+str(obs_count)).kT)
    get_model_component('brem' + str(obs_count)).kT = 40.0
    freeze(get_model_component('brem' + str(obs_count)).kT)
    return None
#------------------------------------------------------------------------------#
def obsid_set4(src_model_dict,bkg_model_dict,obsid, obs_count,redshift,nH_val,Temp_guess):
    '''
    Add three thermal emission models
    '''
    load_pha(obs_count,obsid) #Read in
    if obs_count == 1:
        src_model_dict[obsid] = xsphabs('abs'+str(obs_count)) * (xsapec('apec1_'+str(obs_count)) + xsapec('apec2_'+str(obs_count))+ xsapec('apec3_'+str(obs_count))+ xsapec('apec4_'+str(obs_count))) #set model and name
        # Change src model component values
        get_model_component('apec1_' + str(obs_count)).kT = 1
        get_model_component('apec1_' + str(obs_count)).redshift = redshift  # need to tie all together
        get_model_component('apec1_' + str(obs_count)).Abundanc = 0.3
        thaw(get_model_component('apec1_' + str(obs_count)).Abundanc)
        get_model_component('apec2_' + str(obs_count)).kT = 2
        get_model_component('apec2_' + str(obs_count)).redshift = redshift  # need to tie all together
        get_model_component('apec2_' + str(obs_count)).Abundanc = 0.3
        thaw(get_model_component('apec2_' + str(obs_count)).Abundanc)
        get_model_component('apec3_' + str(obs_count)).kT = 3
        get_model_component('apec3_' + str(obs_count)).redshift = redshift  # need to tie all together
        get_model_component('apec3_' + str(obs_count)).Abundanc = 0.3
        thaw(get_model_component('apec3_' + str(obs_count)).Abundanc)
        get_model_component('apec4_' + str(obs_count)).kT = 3
        get_model_component('apec4_' + str(obs_count)).redshift = redshift  # need to tie all together
        get_model_component('apec4_' + str(obs_count)).Abundanc = 0.3
        thaw(get_model_component('apec4_' + str(obs_count)).Abundanc)
        get_model_component('abs1').nH = nH_val  # change preset value
        freeze(get_model_component('abs1'))
    else:
        src_model_dict[obsid] = get_model_component('abs1') * (xsapec('apec1_'+str(obs_count)) + xsapec('apec2_'+str(obs_count))+xsapec('apec3_'+str(obs_count))+ xsapec('apec4_'+str(obs_count)))
        get_model_component('apec1_'+str(obs_count)).kT = get_model_component('apec1_1').kT #link to first kT
        get_model_component('apec1_' + str(obs_count)).redshift = redshift
        get_model_component('apec1_' + str(obs_count)).Abundanc = get_model_component('apec1_1').Abundanc  # link to first kT
        get_model_component('apec2_'+str(obs_count)).kT = get_model_component('apec2_1').kT #link to first kT (second thermal)
        get_model_component('apec2_' + str(obs_count)).redshift = redshift
        get_model_component('apec2_' + str(obs_count)).Abundanc = get_model_component('apec2_1').Abundanc  # link to first kT (second thermal)
        get_model_component('apec3_'+str(obs_count)).kT = get_model_component('apec3_1').kT #link to first kT (third thermal)
        get_model_component('apec3_' + str(obs_count)).redshift = redshift
        get_model_component('apec3_' + str(obs_count)).Abundanc = get_model_component('apec3_1').Abundanc  # link to first kT (third thermal)
        get_model_component('apec4_'+str(obs_count)).kT = get_model_component('apec3_1').kT #link to first kT (fourth thermal)
        get_model_component('apec4_' + str(obs_count)).redshift = redshift
        get_model_component('apec4_' + str(obs_count)).Abundanc = get_model_component('apec3_1').Abundanc  # link to first kT (fourth thermal)

    bkg_model_dict[obsid] = xsapec('bkgApec'+str(obs_count))+get_model_component('abs1')*xsbremss('brem'+str(obs_count))
    set_source(obs_count, src_model_dict[obsid]) #set model to source
    set_bkg_model(obs_count,bkg_model_dict[obsid])
    #Change bkg model component values
    get_model_component('bkgApec' + str(obs_count)).kT = 0.18
    freeze(get_model_component('bkgApec'+str(obs_count)).kT)
    get_model_component('brem' + str(obs_count)).kT = 40.0
    freeze(get_model_component('brem' + str(obs_count)).kT)
    return None
#------------------------------------------------------------------------------#
def FitXSPEC(spectrum_files,background_files,redshift,n_H,Temp_guess,grouping,spec_count,plot_dir,region, file_to_write, file_min, file_max):
    """
    Function to fit spectra using sherpa and XSPEC
    Args:
        spectrum_files: List of spectrum files for each ObsID
        background_files: List of background files for each ObsID
        redshift: Redshift of cluster
        n_H: Column density
        temp_guess: Initial temperature guess
        grouping: Number of counts to bin in sherpa fit
        spec_count: Bin number
        plot_dir: Path to plot directory
    Return:
        Spectral fit parameters and their errors
    """
    #FIX HEADER
    set_stat('chi2gehrels')
    set_method('levmar')
    hdu_number = 1  #Want evnts so hdu_number = 1
    src_model_dict = {}; bkg_model_dict = {}
    obs_count = 1
    for spec_pha in spectrum_files:
        obsid_set(src_model_dict, bkg_model_dict, spec_pha, background_files[int(obs_count-1)], obs_count, redshift, n_H, Temp_guess)
        obs_count += 1
    for ob_num in range(obs_count-1):
        group_counts(ob_num+1,grouping)
        notice_id(ob_num+1,0.5,8.0)
    fit()
    #Get important values
    Temperature = apec1.kT.val
    Temp_min = Temperature+mins[0]
    Temp_max = Temperature+maxes[0]
    Abundance = apec1.Abundanc.val;
    Ab_min = Abundance+mins[1];
    Ab_max = Abundance+maxes[1]
    #Calculate norm as average value
    Norm = 0; Norm_min = 0; Norm_max = 0
    for id_ in src_ids:
        Norm += get_model_component('apec'+str(id_)).norm.val #add up values
        #get errors
        covar(get_model_component('apec'+str(id_)).norm)
        mins = list(get_covar_results().parmins)
        maxes = list(get_covar_results().parmaxes)
        for val in range(len(mins)):
            if isFloat(mins[val]) == False:
                mins[val] = 0.0
            if isFloat(maxes[val]) == False:
                maxes[val] = 0.0
            else:
                pass
        Norm_min += mins[0]
        Norm_max += maxes[0]
    Norm = Norm/len(src_ids)
    Norm_min = Norm+Norm_min/len(src_ids)
    Norm_max = Norm+Norm_max/len(src_ids)
    # Flux Calculations
    flux_calculation = sample_flux(get_model_component('apec1'), 0.01, 50.0, num=1000, confidence=90)[0]
    Flux = flux_calculation[0]
    Flux_min = flux_calculation[1]
    Flux_max = flux_calculation[2]
    f = get_fit_results()
    reduced_chi_sq = f.rstat
    # Add to class instance
    region.add_fit_data(Temperature,Temp_min,Temp_max,Abundance,Ab_min,Ab_max,Norm,Norm_min,Norm_max,reduced_chi_sq,redshift)
    file_to_write_total.write(spec_count, Temperature, Abundance, reigon.dens[1], region.press[1], region.entropy[1])
    file_min.write(spec_count, Temp_min, Ab_min, reigon.dens[0], region.press[0], region.entropy[0])
    file_max.write(spec_count, Temp_max, Ab_max, reigon.dens[2], region.press[2], region.entropy[2])
    reset(get_model())
    reset(get_source())
    clean()

    return Temperature,Abundance,reduced_chi_sq

def FitXSPEC_double(spectrum_files,background_files,redshift,n_H,Temp_guess,grouping,spec_count):
    #FIX HEADER
    set_stat('chi2gehrels')
    set_method('levmar')
    hdu_number = 1  #Want evnts so hdu_number = 1
    src_model_dict = {}; bkg_model_dict = {}
    obs_count = 1
    for spec_pha in spectrum_files:
        obsid_set2(src_model_dict, bkg_model_dict, spec_pha, obs_count, redshift, n_H, Temp_guess)
        obs_count += 1
    for ob_num in range(obs_count-1):
        group_counts(ob_num+1,grouping)
        notice_id(ob_num+1,0.5,8.0)
    fit()
    Temperature1 = apec1_1.kT.val
    Temperature2 = apec2_1.kT.val
    Abundance1 = apec1_1.Abundanc.val
    Abundance2 = apec2_1.Abundanc.val
    f = get_fit_results()
    reduced_chi_sq = f.rstat
    reset(get_model())
    reset(get_source())
    clean()
    return Temperature1,Temperature2,Abundance1,Abundance2,reduced_chi_sq

def FitXSPEC_triple(spectrum_files,background_files,redshift,n_H,Temp_guess,grouping,spec_count):
    #FIX HEADER
    set_stat('chi2gehrels')
    set_method('levmar')
    hdu_number = 1  #Want evnts so hdu_number = 1
    src_model_dict = {}; bkg_model_dict = {}
    obs_count = 1
    for spec_pha in spectrum_files:
        obsid_set3(src_model_dict, bkg_model_dict, spec_pha, obs_count, redshift, n_H, Temp_guess)
        obs_count += 1
    for ob_num in range(obs_count-1):
        group_counts(ob_num+1,grouping)
        notice_id(ob_num+1,0.5,8.0)
    fit()
    Temperature1 = apec1_1.kT.val
    Temperature2 = apec2_1.kT.val
    Temperature3 = apec3_1.kT.val
    Abundance1 = apec1_1.Abundanc.val
    Abundance2 = apec2_1.Abundanc.val
    Abundance3 = apec3_1.Abundanc.val
    f = get_fit_results()
    reduced_chi_sq = f.rstat
    reset(get_model())
    reset(get_source())
    clean()
    return Temperature1,Temperature2,Temperature3,Abundance1,Abundance2,Abundance3,reduced_chi_sq

def FitXSPEC_quad(spectrum_files,background_files,redshift,n_H,Temp_guess,grouping,spec_count):
    #FIX HEADER
    set_stat('chi2gehrels')
    set_method('levmar')
    hdu_number = 1  #Want evnts so hdu_number = 1
    src_model_dict = {}; bkg_model_dict = {}
    obs_count = 1
    for spec_pha in spectrum_files:
        obsid_set4(src_model_dict, bkg_model_dict, spec_pha, obs_count, redshift, n_H, Temp_guess)
        obs_count += 1
    for ob_num in range(obs_count-1):
        group_counts(ob_num+1,grouping)
        notice_id(ob_num+1,0.5,8.0)
    fit()
    Temperature1 = apec1_1.kT.val
    Temperature2 = apec2_1.kT.val
    Temperature3 = apec3_1.kT.val
    Temperature4 = apec4_1.kT.val
    Abundance1 = apec1_1.Abundanc.val
    Abundance2 = apec2_1.Abundanc.val
    Abundance3 = apec3_1.Abundanc.val
    Abundance4 = apec4_1.Abundanc.val
    f = get_fit_results()
    reduced_chi_sq = f.rstat
    reset(get_model())
    reset(get_source())
    clean()
    return Temperature1,Temperature2,Temperature3,Temperature4,Abundance1,Abundance2,Abundance3,Abundance4,reduced_chi_sq

#--------------------------------------------------------------------#
#--------------------------------------------------------------------#
def Fitting(base_directory,dir,file_name,num_files,redshift,n_H,Temp_guess, component_map, output_dir):
    """
    Fit each region's spectra and create a text file containing the spectral
    fit information for each bin
    Args:
        base_directory: Path to main Directory
        dir: ObsID
        file_name: Root name of PI/PHA file
        num_files: Number of spatial bins
        redshift: Redshift of cluster
        n_H: Column density
        Temp_guess: Initial temperature guess
        component_map: Name of file containing number of components in each bin
        output_file: Text file containing each bin's spectral fit information

    Return:
        None
    """
    energy_min = 0.5
    energy_max = 7.0
    grouping = 50
    plot_dir = base_directory+'/FitPlots/'
    os.chdir(base_directory)
    # Set output file
    file_to_write = open('final_temperature_fits.csv', 'w+')
    file_to_write.write('Bin, Components, Temperature1, Temperature2, Temperature3, Temperature4, Rchi2\n')
    file_to_write_total = open('Thermo_fits.csv', 'w+')
    file_to_write_total.write('Bin, Temperature, Abundance, Density, Pressure, Entropy\n')
    file_min = open('Thermo_min_fits.csv', 'w+')
    file_min.write('Bin, Temperature, Abundance, Density, Pressure, Entropy\n')
    file_max = open('Thermo_max_fits.csv', 'w+')
    file_max.write('Bin, Temperature, Abundance, Density, Pressure, Entropy\n')
    # Read component map to get dictionary {bin: number of components}
    comp_map = open(component_map, 'r'); next(comp_map)
    components = {}
    for line in comp_map.readlines():
        content = line.split(' ')
        components[int(content[0])] = int(content[1])+1 # Have to add one because of how the values are indexed (07-17-2020)
    if plot_dir != '':
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
    if os.path.isfile(file_name) == True:
        os.remove(file_name) #remove it
    regions_ = []
    for bin_i in range(0,num_files):
        print("Fitting model to region "+str(bin_i+1))
        region_ = region(bin_i)
        spectrum_files = []
        background_files = []
        # Get pha files and background files
        for directory in dir:
            if os.path.exists(directory+'/repro/'+output_dir+file_name+"_"+str(bin_i)+".pi") and os.path.exists(directory+'/repro/'+output_dir+file_name+"_"+str(bin_i)+"_bkg.pi"):
                spectrum_files.append(directory+'/repro/'+output_dir+file_name+"_"+str(bin_i)+".pi")
                background_files.append(directory+'/repro/'+output_dir+file_name+"_"+str(bin_i)+"_bkg.pi")
        try:
            # Determine how many fits based on the number of underlying components
            num_components = components[bin_i]
            if num_components == 1:
                Temperature,Abundance,reduced_chi_sq = FitXSPEC(spectrum_files,background_files,redshift,n_H,Temp_guess,grouping,bin_i,plot_dir,region, file_to_write_total, file_min, file_max)
                file_to_write.write("%i,%i,%.2E,%.2E,%.2E,%.2E,%.2E\n"%(bin_i,num_components,Temperature,0.0,0.0,0.0,reduced_chi_sq))
            elif num_components == 2:
                Temperature1,Temperature2,Abundance1,Abundance2,reduced_chi_sq = FitXSPEC_double(spectrum_files,background_files,redshift,n_H,Temp_guess,grouping,bin_i)
                file_to_write.write("%i,%i,%.2E,%.2E,%.2E,%.2E,%.2E\n"%(bin_i,num_components,Temperature1,Temperature2,0.0,0.0,reduced_chi_sq))
            elif num_components == 3:
                Temperature1,Temperature2,Temperature3,Abundance1,Abundance2,Abundance3,reduced_chi_sq = FitXSPEC_triple(spectrum_files,background_files,redshift,n_H,Temp_guess,grouping,bin_i)
                file_to_write.write("%i,%i,%.2E,%.2E,%.2E,%.2E,%.2E\n"%(bin_i,num_components,Temperature1,Temperature2,Temperature3,0.0,reduced_chi_sq))
            elif num_components == 4:
                Temperature1,Temperature2,Temperature3,Temperature4,Abundance1,Abundance2,Abundance3,Abundance4,reduced_chi_sq = FitXSPEC_quad(spectrum_files,background_files,redshift,n_H,Temp_guess,grouping,bin_i)
                file_to_write.write("%i,%i,%.2E,%.2E,%.2E,%.2E,%.2E\n"%(bin_i,num_components,Temperature1,Temperature2,Temperature3,Temperature4,reduced_chi_sq))
            else:
                print('More than 4 components in the spectrum!')
        except:
            print(" No spectra was fit")


    file_to_write.close()
    file_to_write_total.close()
    file_min.close()
    file_max.close()
