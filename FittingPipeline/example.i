#--------------------------SPECTRUM EXTRACTION-----------------------------#
# Region file prefix -- no need to change this
reg_file_prefix = reg_
# Number of annuli to make
num_files = 3
#--------------------------FITTING---------------------------#
#----------INPUT DATA------------#
base_dir = /home/carterrhea/Documents/NGC4636
Name = NAME
ObsIDs = 3926
source_file = reg
output_dir = binned/
Temp_data = Temp_bin.txt
#----------FIT INFO--------------#
# Set redshift of object
redshift = 0.0179
# Set column density
n_H = 0.137
Temp_Guess = 2.0
#----------CHOICES---------------#
extract_spectrum = True
fit_spec = True
plot = True
