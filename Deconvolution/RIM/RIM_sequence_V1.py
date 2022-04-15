"""
Code that calls RIM model and actually trains the RIM
"""
import numpy as np
import tensorflow as tf
import time
from RIM_model_V1 import RIM_Model_1D
from RIM_physical_V1 import calc_grad


class RIM(tf.keras.Model):
    """
    Subclass model to create recurrent inference machine
    If the problem is 2D, we assume the input is square
    """
    def __init__(self, rnn_units1, rnn_units2, input_size, dimensions, t_steps):
        super().__init__(self)
        # Define Optimization Function, Loss Function, and Metrics
        self.optimizer = tf.keras.optimizers.Adam()
        self.loss_fn = tf.keras.losses.MeanSquaredError()
        self.train_acc_metric = tf.keras.metrics.MeanSquaredError()
        self.val_acc_metric = tf.keras.metrics.MeanSquaredError()
        self.rnn_units1 = rnn_units1
        self.rnn_units2 = rnn_units2
        self.conv_filters = 8
        self.kernel_size = 3
        self.size_ = input_size  # Size of input for either spectrum or 2D image
        self.dimensions = dimensions  # Number of dimensions in problem
        self.t_steps = t_steps  # Number of time steps (number of times the RIM is run)
        self.model = RIM_Model_1D(self.conv_filters, self.kernel_size, self.rnn_units1, self.rnn_units2)  # Initialize Model
        self.batch_size = 1  # Intialize batch size -- will be overwritten in fit function

    def init_states(self, batch_size):
        """
        Initialize hidden state1 and hidden state2.

        Args:
            batch_size: Number of spectra in batch
        """
        h_1 = None
        h_2 = None
        if self.dimensions == 1:
            h_1 = tf.zeros(shape=(batch_size, self.rnn_units1))
            h_2 = tf.zeros(shape=(batch_size, self.rnn_units2))
        elif self.dimensions == 2:
            h_1 = tf.zeros(shape=(batch_size, self.rnn_units1, self.rnn_units1))
            h_2 = tf.zeros(shape=(batch_size, self.rnn_units2, self.rnn_units2))
        else:
            print('Please enter a valid dimension size (1 or 2)')
        return h_1, h_2

    def init_sol(self, batch_size):
        """
        Initialize solution

        Args:
            batch_size: Number of spectra in batch
        """
        y_init = None
        if self.dimensions == 1:
            y_init = tf.ones(shape=(batch_size, self.size_, 1))
        elif self.dimensions == 2:
            y_init = tf.ones(shape=(batch_size, self.size_, self.size_, 1))
        else:
            print('Please enter a valid dimension size (1 or 2)')
        return y_init

    @tf.function
    def mean_mse(self, y_true, x_sol):
        """
        Calculate mean squared error (mse) over all time steps

        Args:
            y_true: True solution
            x_sol: Final updated solution from RIM

        Return: mse value
        """
        x_sol = tf.cast(x_sol, tf.float32)
        y_true = tf.cast(y_true, tf.float32)
        return tf.math.reduce_mean(tf.math.square(y_true-x_sol))

    @tf.function
    def train_step(self, step, x, y, model, A, batch_size):
        """
        Test network on training data 


        Args:
            step: Current time step
            x: Batched true spectra for training set
            y: Batched observed spectra for training set
            model: RIM_model instance
            A: Batched response matrix for training set
            batch_size: Number of spectra in a batch
        
        Return:
            train_loss_fun: Loss function vald for training set batch
        """
        # Initialize States
        state1, state2 = self.init_states(batch_size)
        # Initialize Solution
        sol_t = self.init_sol(batch_size)
        # start the scope of gradient
        with tf.GradientTape(persistent=True) as tape:
            # We run this for the number of time steps in the RIM
            for t_step in range(self.t_steps):
                # Calculate the gradient of the log likelihood function
                log_L = calc_grad(y, A, np.eye(len(y)), sol_t)
                logits, state1, state2 = model(sol_t, log_L, states1=state1, states2=state2, training=True, return_state=True)  # forward pass
                sol_t = sol_t + logits  # Update Solution where x_t = del_x + x_(t-1). del_x == logits; x_(t-1) == sol_t

            train_loss_value = self.loss_fn(x, sol_t)  # compute loss on updated solution
            # compute gradient
            grads = tape.gradient(train_loss_value, model.trainable_weights)
            # Clip by norm each layer
            grads = [tf.clip_by_norm(grad, 10.) for grad in grads]
            # update weights
            self.optimizer.apply_gradients(zip(grads, model.trainable_weights))
            # update metrics
            self.train_acc_metric.update_state(x, sol_t)
        # Done looping through time.
        del tape
        return train_loss_value


    @tf.function
    def valid_step(self, step, x, y, model, A, batch_size, return_state=True):
        """
        Test network on validation data  (no training)


        Args:
            step: Current time step
            x: Batched true spectra for validation set
            y: Batched observed spectra for validation set
            model: RIM_model instance
            A: Batched response matrix for validation set
            batch_size: Number of spectra in a batch
        
        Return:
            val_loss_fun: Loss function vald for validation set batch
            sol_t: Updated solution given the validation step
        """
        # Initialize States
        state1, state2 = self.init_states(batch_size)
        # Initialize Solution
        sol_t = self.init_sol(batch_size)
        # forward pass, no backprop, inference mode
        # We run this for the number of time steps in the RIM
        for t_step in range(self.t_steps):
            log_L = calc_grad(y, A, np.eye(len(y)), sol_t)
            val_logits, state1, state2 = model(sol_t, log_L, states1=state1, states2=state2, training=False)
            sol_t = sol_t + val_logits
        # Compute the loss value
        val_loss_value = self.loss_fn(x, sol_t)
        # Update val metrics
        self.val_acc_metric.update_state(x, sol_t)
        return val_loss_value, sol_t
    
    @tf.function
    def test_step(self, step, y, model, A, batch_size, return_state=True):
        """
        input: x, y <- typically batches
        input: step <- batch step
        return: loss value
        """
        # Initialize States
        state1, state2 = self.init_states(batch_size)
        # Initialize Solution
        sol_t = self.init_sol(batch_size)
        # forward pass, no backprop, inference mode
        # We run this for the number of time steps in the RIM
        for t_step in range(self.t_steps):
            log_L = calc_grad(y, A, np.eye(len(y)), sol_t)
            val_logits, state1, state2 = model(sol_t, log_L, states1=state1, states2=state2, training=False)
            sol_t = sol_t + val_logits
            #pickle.dump(sol_t, open('solution_time_%i'%t_step, 'wb'))
        # Compute the loss value
        #val_loss_value = self.loss_fn(x, sol_t)
        # Update val metrics
        #self.val_acc_metric.update_state(x, sol_t)
        return sol_t

    def fit(self, batch_size, epochs, train_dataset, val_dataset):
        """
        A full training and validation algorithm
        Args:
            batch_size: number of batches (int)
            epochs: number of epochs (int)
            train_dataset: batched training set (X_train, Y_train, A_train)
            val_dataset: batched validation set (X_valid, Y_valid, A_valid)
        """
        # custom training loop
        self.batch_size = batch_size
        global train_loss_value, val_loss_value
        for epoch in range(epochs):  # Step through algorithm for each epoch
            t = time.time()
            # Iterate over the batches of the train dataset.
            for train_batch_step, (x_batch_train, y_batch_train, a_train_batch) in enumerate(train_dataset):
                train_batch_step = tf.convert_to_tensor(train_batch_step, dtype=tf.int64)
                train_loss_value = self.train_step(train_batch_step, x_batch_train,
                                                             y_batch_train,
                                                             self.model, a_train_batch, batch_size=batch_size)
                # y += y_update
            # evaluation on validation set -- Run a validation loop at the end of each epoch.
            for val_batch_step, (x_batch_val, y_batch_val, a_batch_val) in enumerate(val_dataset):
                val_batch_step = tf.convert_to_tensor(val_batch_step, dtype=tf.int64)
                val_loss_value, ysol = self.valid_step(val_batch_step, x_batch_val, y_batch_val, self.model, a_batch_val, batch_size=batch_size)
            template = 'ETA: {} - epoch: {} loss: {}  mse: {} val loss: {} val mse: {}\n'
            print(template.format(
                round((time.time() - t) / 60, 2), epoch + 1,
                train_loss_value, float(self.train_acc_metric.result()),
                val_loss_value, float(self.val_acc_metric.result())
            ))
            # Reset metrics at the end of each epoch
            self.train_acc_metric.reset_states()
            self.val_acc_metric.reset_states()
        return ysol

    def call(self, test_dataset, training=False):
        """
        A single run through the recurrent inference machine for prediction purposes

        Args:
            test_dataset: batch test set (X_test, Y_test, A_test)

        """
        sols = []
        #y_test = test_dataset[0]
        #a_test = test_dataset[1]
        #for ct_ in range(y_test.shape[0]):
        for test_batch_step, (y_batch_test, a_batch_test) in enumerate(test_dataset):
            test_batch_step = tf.convert_to_tensor(test_batch_step, dtype=tf.int64)
            sol_t = self.test_step(test_batch_step, y_batch_test, self.model, a_batch_test, batch_size=self.batch_size)
            sols.append(sol_t)
        return sols
