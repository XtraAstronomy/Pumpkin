"""
Deconvolution of X-ray Spectrum

In this notebook we will show how to use our trained RIM (Recurrent Inference Machine) to deconvolve an X-ray spectrum.

## Why deconvolve X-ray spectrum?
We choose to deconvolve X-ray spectrum so that we can pass the true (or intrinstic) recovered spectrum to
a machine learning algorithm that will estimate the posterior distributions of the temperature and metallicity component.
This is useful because we can then pass those as priors to an MCMC fit. These mechanics of the methodology
is hashed out in this series of notebooks.
"""
## Step 1: Inputs & Read Spectrum

from astropy.io import fits
import matplotlib.pyplot as plt
import scipy.stats as sps
import tensorflow as tf
import numpy as np
from BayesianCNN import create_probablistic_bnn_model
import bxa.sherpa as bxa

from sherpa.astro.ui import set_model, load_pha, set_stat, ignore, notice, load_rmf, load_arf, thaw, get_model_plot, get_data
from sherpa.astro.io import read_arf, read_rmf, read_pha
from sherpa.astro import xspec

import corner

plt.rcParams['axes.facecolor'] = 'white'



## Step 4: Run MCMC to obtain parameters using CNN posteriors as priors
load_pha('../Data/test_spectrum.pha')  # Temp = 2.0 ; Abundance = 0.3
#rmf1=unpack_rmf(rmf)
load_arf('../Chandra_acis/acisi_aimpt_cy21.arf')
load_rmf('../Chandra_acis/acisi_aimpt_cy21.rmf')
#data.set_arf(read_arf(arf))
#data.set_rmf(read_rmf(rmf))
set_stat('cstat')
ignore(None, 0.2)
ignore(8, None)
notice(0.2, 8.0)
#apec1 = xspec.XSapec()
#set_model(xspec.XSapec('apec1'))
mdl = xspec.XSapec('apec1')#get_model()
thaw(mdl.Abundanc)
# Set bouunds for uniform prior on norm
mdl.norm.min = 0  # Set min for norm
mdl.norm.max = 110  # Set max for norm
# three parameters we want to vary
param1 = mdl.kT
param2 = mdl.Abundanc
param3 = mdl.norm
set_model(mdl)
# list of parameters
parameters = [param1, param2, param3]
# list of prior transforms
priors = [
   bxa.create_uniform_prior_for(param1),
   bxa.create_uniform_prior_for(param2),
   bxa.create_uniform_prior_for(param3)
   #bxa.create_loguniform_prior_for(param3, 1e-15, 1e-10),
]

# make a single function:
priorfunction = bxa.create_prior_function(priors)

solver = bxa.BXASolver(prior=priorfunction, parameters=parameters,
             outputfiles_basename = "myoutputs_basic/")
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

corner.corner(results["samples"])
