"""
File containing all the necessary functions to run Bayesian analysis
"""
import emcee
import numpy as np


def log_likelihood(self, theta):
    """
    Calculate log likelihood function evaluated given parameters on spectral axis

    Args:
        theta - List of parameters for all the models
    Return:
        Value of log likelihood

    """
    global model
    if self.model_type == 'apec':
        model = apec_model(self.axis_restricted, theta)
    else:
        print("We only support Apec")
    # Add constant contimuum to model
    model += theta[-1]
    sigma2 = self.noise ** 2
    return -0.5 * np.sum((self.spectrum_restricted - model) ** 2 / sigma2 + np.log(2 * np.pi * sigma2))

def log_prior(self, theta, model):
    A_min = 0  # 1e-19
    A_max = 1.1  # 1e-15
    x_min = 0  # 14700
    x_max = 1e8  # 15400
    sigma_min = 0.001
    sigma_max = 1
    for model_num in range(len(model)):
        params = theta[model_num * 3:(model_num + 1) * 3]
    within_bounds = True  # Boolean to determine if parameters are within bounds
    for ct, param in enumerate(params):
        if ct % 3 == 0:  # Amplitude parameter
            if param > A_min and param < A_max:
                pass
            else:
                within_bounds = False  # Value not in bounds
                break
        if ct % 3 == 1:  # velocity parameter
            if param > x_min and param < x_max:
                pass
            else:
                within_bounds = False  # Value not in bounds
                break
        if ct % 3 == 2:  # sigma parameter
            if param > sigma_min and param < sigma_max:
                pass
            else:
                within_bounds = False  # Value not in bounds
                break
    if within_bounds:
        return 0.0
    else:
        return -np.inf


def log_probability(self, theta, x, y, yerr, model):
    lp = log_prior(theta, model)
    if not np.isfinite(lp):
        return -np.inf
    if np.isnan(lp):
        return -np.inf
    if np.isnan(lp + log_likelihood(theta)):
        return -np.inf
    else:
        return lp + log_likelihood(theta)  # , x, y, yerr, model)


def run_bayes_fit():

    n_dim = 3
    n_walkers = 5 * n_dim + 1
    init_ = np.random.randn(n_walkers, n_dim)
    sampler = emcee.EnsembleSampler(n_walkers, n_dim, log_probability,
                                    args=(axis_restricted, spectrum_restricted, noise, lines))
    sampler.run_mcmc(init_, 2000, progress=True, skip_initial_state_check=True)
    flat_samples = sampler.get_chain(discard=200, flat=True)