'''
Python file to create radial profiles
'''
import numpy as np
#import pandas as pd
import matplotlib.pyplot as plt
from Misc.LSCalc import ls_calc

def all_profiles(mydb,mycursor,data_folder,output_folder,redshift,cluster_id):
    '''
    Define the properties that we want a profile for along with their units
    PARAMETERS:
        data_folder - location of csv files containing data and errors
        output_folder - output directory of plots
        redshift - redshift of object
    '''
    properties = {"Temperature":[['Temp','Temp_min','Temp_max'],'keV'],'Abundance':[['Abundance','Ab_min','Ab_max'],'$Z/Z_{\odot}$'],'Density':[['Density','Dens_min','Dens_max'],'$cm^{-3}$'],'Pressure':[['Pressure','Press_min','Press_max'],'$erg cm^{-3}$'],'Entropy':[['Entropy','Entropy_min','Entropy_max'],'$keV cm^{2}$'],'T_Cool':[['T_cool','T_cool_min','T_cool_max'],'Gyr']}
    for key,val in properties.items():
        profile(mydb,mycursor,data_folder,output_folder,redshift,cluster_id,key,val)
    return None


def profile(mydb,mycursor,data_folder,output_folder,redshift,cluster_id,property,units):
    '''
    Create radial profiles for several parameters
    PARAMETERS:
        data_folder - location of csv files containing data and errors
        output_folder - output directory of plots
        redshift - redshift of object
        property - Name of the property
        units - Units of property
    '''
    #Read in data and errors
    props = ''
    for prop in units[0]:
        props += prop+','
    sql_select_Query = "select "+props+"AGN,R_in,R_out from Region WHERE idCluster=%s ORDER BY idRegion"%(cluster_id)
    mycursor.execute(sql_select_Query)
    records = mycursor.fetchall()
    data = []; min_ = []; max_ = []; agn_bool = []; r_in = []; r_out = [];
    for row in records:
        if row[0] != None:
            data.append(float(row[0]))
            min_.append(float(row[1]))
            max_.append(float(row[2]))
            agn_bool.append(float(row[3]))
            r_in.append(float(row[4]))
            r_out.append(float(row[5]))
    regions = []
    regions_err = []
    #arcsec_to_kpc = ls_calc(redshift,1)#arcsec to kpc conversion factor
    #Grab region info
    for region_ct in range(len(r_in)):
        mid_point = float((float(r_in[region_ct])+float(r_out[region_ct])))/2
        error_reg = r_out[region_ct]-mid_point
        regions.append(mid_point)#*arcsec_to_kpc)
        regions_err.append(error_reg)#*arcsec_to_kpc)
    #Pick out AGN vs Non-AGN
    AGN_regions = []; NonAGN_regions = []
    AGN_data = []; NonAGN_data = []
    AGN_min = []; NonAGN_min = []
    AGN_max = []; NonAGN_max = []
    AGN_reg_err = []; NonAGN_reg_err = []
    for count in range(len(agn_bool)):
        if agn_bool[count] == 1:
            AGN_regions.append(regions[count])
            AGN_data.append(data[count])
            AGN_min.append(min_[count])
            AGN_max.append(max_[count])
            AGN_reg_err.append(regions_err[count])
        if agn_bool[count] == 0:
            NonAGN_regions.append(regions[count])
            NonAGN_data.append(data[count])
            NonAGN_min.append(min_[count])
            NonAGN_max.append(max_[count])
            NonAGN_reg_err.append(regions_err[count])
    #now get errors
    err_min = [AGN_data[i]-AGN_min[i] for i in range(len(AGN_min))]
    err_max = [AGN_max[i]-AGN_data[i] for i in range(len(AGN_max))]
    AGN_errors = np.array([err_min,err_max])
    err_min = [NonAGN_data[i]-NonAGN_min[i] for i in range(len(NonAGN_min))]
    err_max = [NonAGN_max[i]-NonAGN_data[i] for i in range(len(NonAGN_max))]
    NonAGN_errors = np.array([err_min,err_max])
    AGN_xerrs = np.array([AGN_reg_err,AGN_reg_err])
    NonAGN_xerrs = np.array([NonAGN_reg_err,NonAGN_reg_err])
    #plotting
    fig = plt.figure()
    fig.subplots_adjust(bottom=0.2,left=0.2)
    ax = fig.add_subplot(111)
    ax.errorbar(NonAGN_regions,NonAGN_data,xerr=NonAGN_xerrs,yerr=NonAGN_errors,lw=0,elinewidth=1,fmt='o',ecolor='coral',color='coral',markersize=4,label='ICM')
    #ax.errorbar(AGN_regions,AGN_data,xerr=AGN_xerrs,yerr=AGN_errors,lw=0,elinewidth=1,fmt='o',ecolor='C0',color='C0',markersize=4,label='AGN+ICM')

    #plt.title(property+" Profile")
    plt.xlabel(r'$R$ (kpc)')
    plt.ylabel(property+' ('+units[1]+')')
    plt.xscale('log')
    # Log y
    if property == 'Abundance' or property == 'Temperature':
        pass
    else:
        plt.yscale('log')
    #Add lines for temp and abundance
    if property == 'Abundance':
        ax.plot(np.linspace(0,1.1*np.max(NonAGN_regions),10),[0.3 for i in range(10)],label='Standard Cluster Abundance')
    if property == 'T_Cool':
        ax.plot(np.linspace(0,1.1*np.max(NonAGN_regions),10),[1 for i in range(10)],label=r'$T_{cool} = 1$ Gyr')
    ax.yaxis.label.set_fontsize(12)
    ax.xaxis.label.set_fontsize(12)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_folder+"/"+property+"_profile.png")
