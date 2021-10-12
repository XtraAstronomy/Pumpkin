"""
Train CNN
"""

import matplotlib.pyplot as plt
import numpy as np
import pickle
import os
from scipy.stats import gaussian_kde
from BayesianCNN import create_probablistic_bnn_model, run_experiment, negative_loglikelihood
import tensorflow as tf
# ------------ INPUTS -------------- #



# ----------- READ IN -----------------#
# Read in Spectral Data
spectra_data = pickle.load(open('/home/carterrhea/pCloudDrive/Research/Chandra-Response/RIM_data/spectra.pkl', 'rb'))
spectra = [spec[1][0][1][35:550] for spec in spectra_data.items()]
temperatures = [spec[1][3] for spec in spectra_data.items()]
abundances = [spec[1][4] for spec in spectra_data.items()]
# ---------- Train and Test Algorithm------------ #
# Get number of spectra
syn_num_pass = len(spectra)
train_div = int(0.7*syn_num_pass)  # Percent of synthetic data to use as training
valid_div = int(0.9*syn_num_pass)  # Percent of synthetic data used as training and validation (validation being the difference between this and train_div)
# Set training set
TrainingSet = np.array(spectra[:train_div])
TrainingSet = TrainingSet.reshape(TrainingSet.shape[0], TrainingSet.shape[1], 1)
print(TrainingSet.shape)
Training_labels = np.array((temperatures[0:train_div], abundances[0:train_div])).T
train_dataset = tf.data.Dataset.from_tensor_slices((TrainingSet, Training_labels))
# Set validation set
ValidSet = np.array(spectra[train_div:valid_div])
ValidSet = ValidSet.reshape(ValidSet.shape[0], ValidSet.shape[1], 1)
Valid_labels = np.array((temperatures[train_div:valid_div], abundances[train_div:valid_div])).T
validation_dataset = tf.data.Dataset.from_tensor_slices((ValidSet, Valid_labels))
# Set test data
TestSet = np.array(spectra[valid_div:])
TestSet = TestSet.reshape(TestSet.shape[0], TestSet.shape[1], 1)
TestSetLabels = np.array((temperatures[valid_div:], abundances[valid_div:])).T
test_dataset = tf.data.Dataset.from_tensor_slices((TestSet, TestSetLabels))

BATCH_SIZE = 16

train_dataset = train_dataset.batch(BATCH_SIZE)
validation_dataset = validation_dataset.batch(BATCH_SIZE)
test_dataset = test_dataset.batch(BATCH_SIZE)


num_epochs = 35
prob_bnn_model = create_probablistic_bnn_model(train_size=train_div, hidden_units=[128, 128], num_filters=[4,16], filter_length=[5,3])
run_experiment(prob_bnn_model, negative_loglikelihood, train_dataset, validation_dataset, test_dataset, num_epochs=num_epochs)
sample = 10
examples, targets = list(test_dataset.unbatch().shuffle(BATCH_SIZE * 10).batch(sample))[
    0
]

prediction_distribution = prob_bnn_model(examples)
prediction_mean = prediction_distribution.mean().numpy().tolist()
prediction_stdv = prediction_distribution.stddev().numpy()

# The 95% CI is computed as mean ± (1.96 * stdv)
upper = (prediction_mean + (1.96 * prediction_stdv)).tolist()
lower = (prediction_mean - (1.96 * prediction_stdv)).tolist()
prediction_stdv = prediction_stdv.tolist()

for idx in range(sample):
    print(
        f"Prediction mean: {round(prediction_mean[idx][0], 2)}, "
        f"stddev: {round(prediction_stdv[idx][0], 2)}, "
        f"95% CI: [{round(upper[idx][0], 2)} - {round(lower[idx][0], 2)}]"
        f" - Actual: {targets[idx]}"
    )

