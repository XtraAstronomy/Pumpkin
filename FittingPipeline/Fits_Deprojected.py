'''
65;6003;1c------------------------------------------------------
GOAL:
    Step through bins (spectra) and calculate the temperature value
    of each bin using XSPEC for DEPROJECTED quantites
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
import astropy.units as u
from sherpa.astro.xspec import *
from sherpa.astro.all import *
from sherpa.astro.ui import *
from sherpa.all import *
from LSCalc import ls_calc
import deproject
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
def obsid_set(src_model_dict,bkg_model_dict,obsid,bkg_src, obs_count,redshift,nH_val,Temp_guess):
    '''
    Function to set the source and background model for the observation
    :Params
    :src_model_dict : Dictionary of all the source models set for particular region
    :bkg_model_dict : Dido except for the background models
    :obsid : The source pha/pi file
    :bkg_src : The background pha/pi file
    :obs_count : The count of the current observation

    '''
    load_pha(obs_count,obsid,use_errors=True) #Read in
    if obs_count == 1:  # Set if this is the first
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
    set_source(obs_count, src_model_dict[obsid]) #set model to source
    set_bkg(obs_count, unpack_pha(bkg_src))
    bkg_model_dict[obsid] = xsapec('bkgApec'+str(obs_count))+get_model_component('abs1')*xsbremss('brem'+str(obs_count))
    set_bkg_model(obs_count,bkg_model_dict[obsid])
    #Change bkg model component values
    get_model_component('bkgApec' + str(obs_count)).kT = 0.18
    freeze(get_model_component('bkgApec'+str(obs_count)).kT)
    get_model_component('brem' + str(obs_count)).kT = 40.0
    freeze(get_model_component('brem' + str(obs_count)).kT)

    return None
#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
def FitXSPEC(spectrum_files,background_files,redshift,n_H,Temp_guess,grouping,spec_count,plot_dir):
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
    set_stat('chi2gehrels')
    set_method('levmar')
    hdu_number = 1  #Want evnts so hdu_number = 1
    src_model_dict = {}; bkg_model_dict = {}
    obs_count = 1
    for spec_pha in spectrum_files:
        obsid_set(src_model_dict, bkg_model_dict, spec_pha,background_files[int(obs_count-1)], obs_count, redshift, n_H, Temp_guess)
        obs_count += 1
    for ob_num in range(obs_count-1):
        if deproj == False:
            group_counts(ob_num+1,grouping)
        notice_id(ob_num+1,0.5,8.0)


    set_log_sherpa()
    set_covar_opt("sigma",1)
    covar(get_model_component('apec1').kT,get_model_component('apec1').Abundanc)
    mins = list(get_covar_results().parmins)
    maxes = list(get_covar_results().parmaxes)
    for val in range(len(mins)):
        if isFloat(mins[val]) == False:
            mins[val] = 0.0
        if isFloat(maxes[val]) == False:
            maxes[val] = 0.0
        else:
            pass
    #Get important values
    Temperature = apec1.kT.val
    Temp_min = Temperature+mins[0]
    Temp_max = Temperature+maxes[0]
    Abundance = apec1.Abundanc.val
    Ab_min = Abundance+mins[1]
    Ab_max = Abundance+maxes[1]
    #Calculate norm as average value
    Norm = 0; Norm_min = 0; Norm_max = 0
    Norm += get_model_component('apec1').norm.val #add up values
    #get errors
    covar(get_model_component('apec1').norm)
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
    Norm = Norm/len(spectrum_files)
    Norm_min = Norm+Norm_min/len(spectrum_files)
    Norm_max = Norm+Norm_max/len(spectrum_files)
    f = get_fit_results()
    reduced_chi_sq = f.rstat
    #---------Set up Flux Calculation----------#
    flux_calculation = sample_flux(get_model_component('apec1'), 0.01, 50.0, num=1000, confidence=90)[0]
    Flux = flux_calculation[0]
    Flux_min = flux_calculation[1]
    Flux_max = flux_calculation[2]
    reset(get_model())
    reset(get_source())
    clean()
    return Temperature,Temp_min,Temp_max,Abundance,Ab_min,Ab_max,Norm,Norm_min,Norm_max,reduced_chi_sq,Flux,Flux_min,Flux_max



def Fitting_Deprojected(base_directory,ObsIDs,file_name,num_files,redshift,n_H,Temp_guess,output_file, region_dir, reg_file_prefix, num_bins):
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
        temp_guess: Initial temperature guess
        output_file: Text file containing each bin's spectral fit information
        bin_spec_dir: Path to extracted spectra for each bin within an ObsID

    Return:
        None
    """
    energy_min = 0.5
    energy_max = 8.0
    grouping = 5
    plot_dir = base_directory+'/FitPlots/'
    output_file = output_file.split('.')[0]
    os.chdir(base_directory)
    if plot_dir != '':
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
    if os.path.isfile(file_name) == True:
        os.remove(file_name) #remove it
    # Non Deprojected Fits

    # Set up deprojection
    # Get region values
    region_vals = []  # First get regions in kpc
    for region_ct in range(num_bins):
        with open(region_dir+reg_file_prefix+str(region_ct)+'.reg') as reg_:
            reg_data = reg_.readlines()[3].split(')')[0].split('(')[1]
            r_in_ = ls_calc(redshift,float(reg_data.split(',')[2].strip('"')))
            #r_in.append(r_in_)
            r_out_ = ls_calc(redshift,float(reg_data.split(',')[3].strip('"')))
            if r_in_ not in region_vals:
                region_vals.append(r_in_)
            if r_out_ not in region_vals:
                region_vals.append(r_out_)
    print(region_vals)
    # Create deprojection instance
    dep = deproject.Deproject(radii=[float(x) for x in region_vals]* u.arcsec)
    # load associated datasets
    for ann in range(len(region_vals)-1):
        for obsid in ObsIDs:
            # Take pi file from obsid/repro
            dep.load_pha(obsid+'/repro/'+file_name+'%s.pi' % (str(ann)), annulus=ann)
    # Set up fit parameters
    dep.set_source('xsphabs*xsapec')
    dep.ignore(None, 0.5)
    dep.ignore(8, None)
    dep.freeze("xsphabs.nh")
    dep.set_par('xsapec.redshift', redshift)
    dep.set_par('xsphabs.nh', n_H)
    dep.set_par('xsapec.Abundanc', 0.3)
    dep.subtract()  # Subtract associated background. Read in automatically earlier
    onion = dep.fit()
    onion_errs = dep.conf()
    print(onion, onion_errs)
    for row in onion[0]:
        print(row)
    #densities = dep.get_densities()
    file_to_write = open(output_file+"_deproj.txt",'w+')
    file_to_write.write("BinNumber Temperature Temp_min Temp_max Abundance Ab_min Ab_max Norm Norm_min Norm_max ReducedChiSquare Flux Flux_min Flux_max\n")
    file_to_write.write('BinNumber r_in r_out temp norm dens \n')
    for row,row_err in enumerate(zip(onion[:], onion_errs[:])):
        #print(row, row_err)

        file_to_write.write('%i %.2E %.2E %.2E %.2E %.2E \n'%(row[0], row[1], row[2], row[-3], row[-2], row[-1]))
    file_to_write.close()
