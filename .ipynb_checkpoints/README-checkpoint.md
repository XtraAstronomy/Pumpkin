# Pumpkin
Code for Principal Component and Random Forest Classification to study Galaxy Cluster X-ray Emission

In order create the synthetic data the *ciao* software package is required. It can be found here: https://cxc.cfa.harvard.edu/ciao/

In order to create the synthetic data, update the StN150_Single.py and StN150_Double.py files with the appropriate directories. Then run the following command,
`python StN150_Single.py && python StN150_Double.py`

We then need to shuffle the data (again please update the directories in the StN150_shuffle.py file)...
Then run `python StN150_shuffle.py`

With the synthetic data created, we can now move to training and testing the algorithm. To do so open ***PCA_ML-StN150.ipynb***.