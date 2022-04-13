"""
Train CNN using the deconvolved spectra (i.e. true spectra)
"""

import matplotlib.pyplot as plt
import numpy as np
import pickle
import os
from scipy.stats import gaussian_kde
from BayesianCNN import create_probablistic_bnn_model, run_experiment, negative_loglikelihood
import tensorflow as tf
from RIM_sequence_V1 import RIM
# ------------ INPUTS -------------- #



# ----------- READ IN -----------------#
# Read in Spectral Data & Response matrices
# TODO: UPDATE TO HAVE DECONVOLVED DATA!!!!
spectra_data = pickle.load(open('/home/carterrhea/pCloudDrive/Research/Chandra-Response/RIM_data/spectra.pkl', 'rb'))
true_spectra = pickle.load(open('/home/carterrhea/pCloudDrive/Research/Chandra-Response/RIM_data/true_spectra.pkl', 'rb'))
responses_data = pickle.load(open('/home/carterrhea/pCloudDrive/Research/Chandra-Response/RIM_data/rmfs.pkl', 'rb'))
# Pull out spectra
min_ = 35
max_ = 175
num_ = 10000
#print([spec for spec in spectra_data.items()][0])
#spectra = [spec[1][0][1][35:550] for spec in spectra_data.items()]
temperatures = [round(spec[1][3], 2) for spec in spectra_data.items()]
abundances = [round(spec[1][4], 2) for spec in spectra_data.items()]
spectra = [spec[1][1][min_:max_] for spec in true_spectra.items()]  # use True spectrum
spectra_response = [data[1][1] for data in spectra_data.items()]
responses = [responses_data[val][min_:max_,min_:max_] for val in spectra_response][:num_]
# ---------- Deconvolve Spectra using RIM ------- #
input_data = tf.data.Dataset.from_tensor_slices((spectra, responses))
input_data = input_data.batch(1)  # Batch size 1
RIM_model = RIM(rnn_units1=100, rnn_units2=100, input_size=140, dimensions=1, t_steps=10)
RIM_model.load_weights('RIM-Model/RIM_apec_small')
test = RIM_model(tf.data.Dataset.from_tensor_slices((spectra[0], responses[0])))
print(RIM_model.summary())
deconvolved_spectrum = RIM_model(input_data)
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
print(TestSet.shape)
TestSet = TestSet.reshape(TestSet.shape[0], TestSet.shape[1], 1)
TestSetLabels = np.array((temperatures[valid_div:], abundances[valid_div:])).T
test_dataset = tf.data.Dataset.from_tensor_slices((TestSet, TestSetLabels))

BATCH_SIZE = 8

train_dataset = train_dataset.batch(BATCH_SIZE)
validation_dataset = validation_dataset.batch(BATCH_SIZE)
test_dataset = test_dataset.batch(BATCH_SIZE)

train_size = train_div
num_epochs = 20
# Train Algorithm
prob_bnn_model = create_probablistic_bnn_model(hidden_units=[128, 256], num_filters=[4,16], filter_length=[5,3])
run_experiment(prob_bnn_model, negative_loglikelihood, train_dataset, validation_dataset, test_dataset, num_epochs=num_epochs, outputname='PUMPKIN-I')



# Obtain results on a sample
sample = 50
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

temperature_preds = [pred[0] for pred in prediction_mean]
temperature_stds = [pred[0] for pred in prediction_stdv]

metallicty_preds = [pred[1] for pred in prediction_mean]
metallicity_stds = [pred[1] for pred in prediction_stdv]

for idx in range(sample):
    print("Temperature")
    print(
        f"Prediction mean: {round(prediction_mean[idx][0], 2)}, "
        f"stddev: {round(prediction_stdv[idx][0], 2)}, "
        f"95% CI: [{round(upper[idx][0], 2)} - {round(lower[idx][0], 2)}]"
        f" - Actual: {targets[idx][0]}"
    )
    print("Metallicity")
    print(
        f"Prediction mean: {round(prediction_mean[idx][1], 2)}, "
        f"stddev: {round(prediction_stdv[idx][1], 2)}, "
        f"95% CI: [{round(upper[idx][1], 2)} - {round(lower[idx][1], 2)}]"
        f" - Actual: {targets[idx][1]}"
    )

target_x = [targ[0] for targ in targets]
plt.errorbar(target_x, temperature_preds, yerr=temperature_stds,
             fmt='o', ecolor='g', capthick=2, label='predictions')
plt.plot(target_x, target_x, label='perfect prediction')
plt.xlabel('True Temperature (keV)', fontweight='bold')
plt.ylabel('Predicted Temperature (keV)', fontweight='bold')
plt.legend()
plt.savefig('temperature_residuals.png')
plt.clf()

target_x = [targ[1] for targ in targets]
plt.errorbar(target_x, metallicty_preds, yerr=metallicity_stds,
             fmt='o', ecolor='g', capthick=2, label='predictions')
plt.plot(target_x, target_x, label='perfect prediction')
plt.xlabel(r'True Metallicity (Z$_\odot$)', fontweight='bold')
plt.ylabel(r'Predicted Metallicity (Z$_\odot$)', fontweight='bold')
plt.legend()
plt.savefig('metallicity_residuals.png')


pickle.dump(prediction_distribution, open('prediction_distribution.pkl', 'wb'))
