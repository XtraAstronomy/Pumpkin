#--------------------------SPECTRUM EXTRACTION-----------------------------#
reg_file_prefix = reg_
num_files = 3
#--------------------------FITTING---------------------------#
#----------INPUT DATA------------#
base_dir = /home/carterrhea/Documents/NGC4636
Name =
ObsIDs = 3926
source_file = reg
output_dir = binned/
Temp_data = Temp_bin.txt
#----------FIT INFO--------------#
redshift = 0.0179
n_H = 0.137
Temp_Guess = 2.0
#----------CHOICES---------------#
extract_spectrum = False
fit_spec = True
plot = True
