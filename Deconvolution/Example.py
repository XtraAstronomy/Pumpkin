"""
Deconvolution of X-ray Spectrum

In this notebook we will show how to use our trained RIM (Recurrent Inference Machine) to deconvolve an X-ray spectrum.

## Why deconvolve X-ray spectrum?
We choose to deconvolve X-ray spectrum so that we can pass the true (or intrinstic) recovered spectrum to
a machine learning algorithm that will estimate the posterior distributions of the temperature and metallicity component.
This is useful because we can then pass those as priors to an MCMC fit. These mechanics of the methodology
is hashed out in this series of notebooks.
"""
import sys
sys.path.append('/home/carterrhea/pCloudDrive/Research/Chandra-Response/RIM')
## Step 1: Inputs & Read Spectrum
from astropy.io import fits
import matplotlib.pyplot as plt
import scipy.stats as sps
import tensorflow as tf
import numpy as np
from BayesianCNN import create_probablistic_bnn_model
import bxa.sherpa as bxa
from RIM_sequence_V1 import RIM
from sherpa.astro.ui import set_model, load_pha, set_stat, ignore, notice, load_rmf, load_arf, thaw, get_model_plot, get_data
from sherpa.astro.io import read_arf, read_rmf, read_pha

from sherpa.astro import xspec


plt.rcParams['axes.facecolor'] = 'white'

spectrum = fits.open("../Data/test_spectrum.pha")
spectrum = spectrum[1].data
spectrum_axis = [s1[0] for s1 in spectrum[35:175]]
spectrum_counts = [np.array([s1[1] for s1 in spectrum[35:175]])]
# Load combined response matrix
response = fits.open("../Chandra_acis/acisi_aimpt_cy21_rsp.img")
response = response[0].data
response = [response[35:175, 35:175]]

print(spectrum_counts)

## Step 2: Apply RIM to deconvolve spectrum
#input_data = [spectrum_counts, response]
input_data = tf.data.Dataset.from_tensor_slices((spectrum_counts, response))
input_data = input_data.batch(1)  # Batch size 1

RIM_model = RIM(rnn_units1=128, rnn_units2=128, input_size=140, dimensions=1, t_steps=1)
RIM_model.built = True
RIM_model.load_weights('weights_512nodes_20epochs/weights')
deconvolved_spectrum = RIM_model(input_data, training=False)
plt.plot(spectrum_axis, deconvolved_spectrum)
plt.savefig('deconvolved_test.png')
plt.clf()

## Step 3: Apply probabilistic Bayesian Convolutional Neural Network to extract Posterior on parameters

bcnn = create_probablistic_bnn_model(hidden_units=[128, 256], num_filters=[4,16], filter_length=[5,3])
bcnn.load_weights('PUMPKIN-I')
spectrum_counts_input = spectrum_counts.reshape(1, spectrum_counts.shape[0], 1)
prediction_distribution = bcnn(tf.convert_to_tensor(spectrum_counts_input))
prediction_mean = prediction_distribution.mean().numpy().tolist()
prediction_stdv = prediction_distribution.stddev().numpy()

print(prediction_mean, prediction_stdv)

## Step 4: Run MCMC to obtain parameters using CNN posteriors as priors
load_pha('../Data/test_spectrum.pha')
load_arf('../Chandra_acis/acisi_aimpt_cy21.arf')
load_rmf('../Chandra_acis/acisi_aimpt_cy21.rmf')
set_stat('chi2gehrels')
ignore(None, 0.2)
ignore(8, None)
notice(0.2, 8.0)
mdl = xspec.XSapec('apec1')#get_model()
thaw(mdl.Abundanc)
# Set bouunds for uniform prior on norm
mdl.norm.min = 0  # Set min for norm
mdl.norm.max = 11  # Set max for norm
# three parameters we want to vary
param1 = mdl.kT
param2 = mdl.Abundanc
param3 = mdl.norm
set_model(mdl)
# list of parameters
parameters = [param1, param2, param3]
# list of prior transforms
priors = [
   bxa.create_gaussian_prior_for(param1, prediction_mean[0][0], prediction_stdv[0][0]),
   bxa.create_gaussian_prior_for(param2, prediction_mean[0][1], prediction_stdv[0][1]),
   bxa.create_uniform_prior_for(param3)
]

# make a single function:
priorfunction = bxa.create_prior_function(priors)

solver = bxa.BXASolver(prior=priorfunction, parameters=parameters,
             outputfiles_basename = "myoutputs/")

print(solver)
print(get_data())
results = solver.run()
solver.set_best_fit()
x_ = get_model_plot().xlo
y_ = get_model_plot().y
plt.plot(x_,y_, label='model')
plt.plot(get_data().x, get_data().y, label='observation')
plt.legend()
plt.show()