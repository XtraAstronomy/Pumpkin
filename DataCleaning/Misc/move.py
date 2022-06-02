'''
Move necessary files from individual observation to the merged(though not merged) folder
'''
import shutil
def move_files(out_dir,filenames):
    shutil.copy(filenames['evt2_repro_uncontam'],out_dir)
    shutil.copy(filenames['evt2_repro'],out_dir)
    shutil.copy(filenames['evt_bkgsub_img'],out_dir)
    shutil.copy(filenames['evt_uncontam_img'],out_dir)
    #shutil.copy(filenames['exp_corr'],out_dir)
    #shutil.copy('bkg.reg',out_dir)
    shutil.copy('pt_srcs.reg',out_dir)
    shutil.copy('AGN.reg',out_dir)
    #shutil.copy('bkg_cel.reg',out_dir)
    #shutil.copy('bkgsub_exp.png',out_dir)
