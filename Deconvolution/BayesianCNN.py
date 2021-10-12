"""
File containing the definitions required to train our Bayesian CNN
The functions are taken from https://keras.io/examples/keras_recipes/bayesian_neural_networks/#probabilistic-bayesian-neural-networks
"""
import tensorflow as tf
import tensorflow.keras as keras
import tensorflow_probability as tfp

def run_experiment(model, loss, train_dataset, valid_dataset, test_dataset, num_epochs):
    learning_rate = 0.001
    model.compile(
        optimizer=keras.optimizers.RMSprop(learning_rate=learning_rate),
        loss=loss,
        metrics=[keras.metrics.RootMeanSquaredError()],
    )

    print("Start training the model...")
    model.fit(train_dataset, epochs=num_epochs, validation_data=valid_dataset)
    print("Model training finished.")
    _, rmse = model.evaluate(train_dataset, verbose=0)
    print(f"Train RMSE: {round(rmse, 3)}")

    print("Evaluating model performance...")
    _, rmse = model.evaluate(test_dataset, verbose=0)
    print(f"Test RMSE: {round(rmse, 3)}")

# Define the prior weight distribution as Normal of mean=0 and stddev=1.
# Note that, in this example, the we prior distribution is not trainable,
# as we fix its parameters.
def prior(kernel_size, bias_size, dtype=None):
    n = kernel_size + bias_size
    print(n)
    prior_model = keras.Sequential(
        [
            tfp.layers.DistributionLambda(
                lambda t: tfp.distributions.MultivariateNormalDiag(
                    loc=tf.zeros(n), scale_diag=tf.ones(n)
                )
            )
        ]
    )
    return prior_model


# Define variational posterior weight distribution as multivariate Gaussian.
# Note that the learnable parameters for this distribution are the means,
# variances, and covariances.
def posterior(kernel_size, bias_size, dtype=None):
    n = kernel_size + bias_size
    posterior_model = keras.Sequential(
        [
            tfp.layers.VariableLayer(
                tfp.layers.MultivariateNormalTriL.params_size(n), dtype=dtype
            ),
            tfp.layers.MultivariateNormalTriL(n),
        ]
    )
    return posterior_model


def create_probablistic_bnn_model(train_size,hidden_units, num_filters, filter_length):
    """

    Args:
        train_size:
        hidden_units: Number of hidden nodes in each hidden layer (e.x. [128, 128] will make two layers with 128 nodes each)
        num_filters: Number of filters in the convolutional layer
        filter_length: Length of each individual filter

    Return:
        Probabilistic Bayesian Neural Network
    """
    # Define input which is a vector with 515 elements representing the spectra
    inputs = keras.Input(shape=(515,1))#keras.layers.concatenate(list(inputs.values()))

    features = keras.layers.BatchNormalization()(inputs)
    # Create hidden layers with weight uncertainty using the DenseVariational layer.
    #print(features)
    #features = keras.layers.Flatten()(features)
    for filter_, length_ in zip(num_filters, filter_length):
        features = keras.layers.Conv1D(filters=filter_, kernel_size=length_, padding='same', activation='relu')(features)
    features = keras.layers.MaxPooling1D(pool_size=2)(features)
    features = keras.layers.Flatten()(features)
    features = keras.layers.Dropout(0.2)(features)
    for units in hidden_units:
        '''features = tfp.layers.DenseVariational(
            units=units,
            make_prior_fn=prior,
            make_posterior_fn=posterior,
            kl_weight=1 / train_size,
            activation="sigmoid",
        )(features)'''
        features = keras.layers.Dense(units, activation="relu")(features)

    # Create a probabilisticå output (Normal distribution), and use the `Dense` layer
    # to produce the parameters of the distribution.
    # We set units=2 to learn both the mean and the variance of the Normal distribution.
    distribution_params = keras.layers.Dense(units=4)(features)
    outputs = tfp.layers.IndependentNormal(2)(distribution_params)
    model = keras.Model(inputs=inputs, outputs=outputs)
    return model


def negative_loglikelihood(targets, estimated_distribution):
    return -estimated_distribution.log_prob(targets)