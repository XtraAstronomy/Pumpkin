# Pumpkin
Code for Principal Component and Random Forest Classification to study Galaxy Cluster X-ray Emission

In order create the synthetic data the *ciao* software package is required. It can be found here: https://cxc.cfa.harvard.edu/ciao/

In order to create the synthetic data, update the StN150_Single.py and StN150_Double.py files with the appropriate directories. Then run the following command,
`python StN150_Single.py && python StN150_Double.py`

We then need to shuffle the data (again please update the directories in the StN150_shuffle.py file)...
Then run `python StN150_shuffle.py`

With the synthetic data created, we can now move to training and testing the algorithm. To do so open ***PCA_ML-StN150.ipynb***.


## Perseus Cluster
This repository contains all the code required to recreate the Perseus cluster map (figure 8) in our 2020 paper. There are several steps needed to recreate the map:


1. Download the ObsIDs 3209 and 4289
2. Merge the two ObsIDs using CIAO, determine region of choice in ds9, and finally use dmcopy to extract a fits image of the region (I called it source.img)
3. Update TemperatureMapPipeline/Perseus.i --> namely image\_fits and base\_dir
4. run "python Temperature\_Maps.py Perseus.i"
	- This will create a WVT map of your region and extract the spectra of each region for each ObsID (it takes a while)
	
