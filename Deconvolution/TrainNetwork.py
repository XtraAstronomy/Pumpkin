"""
Train CNN
"""

import matplotlib.pyplot as plt
import numpy as np
import pickle
import os
from scipy.stats import gaussian_kde
from BayesianCNN import create_probablistic_bnn_model, run_experiment, negative_loglikelihood

# ------------ INPUTS -------------- #



# ----------- READ IN -----------------#
# Read in Spectral Data
spectra_data = pickle.load(open('/home/carterrhea/pCloudDrive/Research/Chandra-Response/RIM_data/spectra.pkl', 'rb'))
spectra = [spec[0] for spec in spectra_data]
temperatures = [spec[3] for spec in spectra_data]
abundances = [spec[4] for spec in spectra_data]


# ---------- Train and Test Algorithm------------ #
# Get number of spectra
syn_num_pass = len(spectra)
train_div = int(0.7*syn_num_pass)  # Percent of synthetic data to use as training
valid_div = int(0.9*syn_num_pass)  # Percent of synthetic data used as training and validation (validation being the difference between this and train_div)
# Set training set
TrainingSet = np.array(spectra[:train_div])
#TraningSet = TraningSet.reshape(TraningSet.shape[0], TraningSet.shape[1], 1)
Training_labels = np.array((temperatures[0:train_div], abundances[0:train_div])).T
train_dataset = (TrainingSet, Training_labels)
# Set validation set
ValidSet = np.array(spectra[train_div:valid_div])
#ValidSet = ValidSet.reshape(ValidSet.shape[0], ValidSet.shape[1], 1)
Valid_labels = np.array((temperatures[train_div:valid_div], abundances[train_div:valid_div])).T
validation_set = (ValidSet, Valid_labels)
# Set test data
TestSet = np.array(spectra[valid_div:])
#TestSet = TestSet.reshape(TestSet.shape[0], TestSet.shape[1], 1)
TestSetLabels = np.array((temperatures[valid_div:], abundances[valid_div:])).T
test_dataset = (TestSet, TestSetLabels)
num_epochs = 100
prob_bnn_model = create_probablistic_bnn_model(hidden_units=[128, 128])
run_experiment(prob_bnn_model, negative_loglikelihood, train_dataset, validation_set, test_dataset, num_epochs=num_epochs)

