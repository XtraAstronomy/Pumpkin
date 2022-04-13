import tensorflow as tf
import numpy as np
import time


class RIM_Model_1D(tf.keras.Model):
    """
    Subclass model to create recurrent inference machine architecture for a 1 dimensional version
    """
    def __init__(self, conv_filters, kernel_size, rnn_units1, rnn_units2):
        super().__init__(self)
        # Define Layers of RIM
        self.conv1d_1 = tf.keras.layers.Conv1D(filters=conv_filters, kernel_size=kernel_size, strides=1,
                                               padding='same', activation='tanh')
        self.gru1 = tf.keras.layers.GRU(rnn_units1, activation='tanh', recurrent_activation='sigmoid',
                                        return_sequences=True, return_state=True)
        self.conv1d_2 = tf.keras.layers.Conv1DTranspose(filters=conv_filters, kernel_size=kernel_size, strides=1,
                                                        padding='same', activation='tanh')
        self.gru2 = tf.keras.layers.GRU(rnn_units2, activation='tanh', recurrent_activation='sigmoid',
                                        return_sequences=True, return_state=True)
        self.conv1d_3 = tf.keras.layers.Conv1D(filters=1, kernel_size=kernel_size, strides=1,
                                                        padding='same', activation='linear')


    def call(self, sol, log_L, states1=None, states2=None, return_state=True, training=False):
        """
        A single run through the recurrent inference machine
        conv2d -> gru -> conv2d_T -> gru -> conv2d
        When we go from a convolutional layer to a GRU, we need to first flatten the activation map. We then use the
        expand_dims function to make sure the input of the GRU has the correct format (batch length, feature dims, 1).
        Args:
            sol: solution at time step t (x_t)
            log_L: Gradient of log likelihood
            states1: Hidden state of gru 1
            states2: Hidden state of gru 2
            return_state: Return the hidden state boolean
            training: Boolean determining whether or not the layer acts in training or inference mode
        """
        #print(sol.shape, log_L.shape)
        x = sol + log_L  # Pass previous solution and gradient of log likelihood at previous step
        x = self.conv1d_1(x, training=training)
        if states1 is None:
            states1 = self.gru1.get_initial_state(x)
        x, states1 = self.gru1(x, initial_state=states1, training=training)
        x = self.conv1d_2(x, training=training)
        if states2 is None:
            states2 = self.gru2.get_initial_state(x)
        x, states2 = self.gru2(x, initial_state=states2, training=training)
        x = self.conv1d_3(x, training=training)
        if return_state:
            return x, states1, states2
        else:
            return x



class RIM_Model_2D(tf.keras.Model):
    """
    Subclass model to create recurrent inference machine architecture
    """
    def __init__(self):
        super().__init__(self)
        # Define Layers of RIM
        conv_filters = 1
        kernel_size = (1, 1)
        rnn_units1 = 1
        rnn_units2 = 1
        self.conv2d_1 = tf.keras.layers.Conv2D(filters=conv_filters, kernel_size=kernel_size, strides=(2,2),
                                               padding='same', activation='tanh')
        self.gru_setup1 = tf.keras.layers.Flatten()
        self.gru_setup2 = tf.keras.layers.Lambda(lambda x: tf.expand_dims(x, axis=-1))
        self.gru1 = tf.keras.layers.GRU(rnn_units1, activation='tanh', recurrent_activation='sigmoid',
                                        return_sequences=True, return_state=True)
        self.conv_setup1 = tf.keras.layers.Reshape((32, 32, rnn_units1))
        self.conv2d_2 = tf.keras.layers.Conv2DTranspose(filters=conv_filters, kernel_size=kernel_size, strides=(1, 1),
                                                        padding='same', activation='tanh')
        self.gru2 = tf.keras.layers.GRU(rnn_units2, activation='tanh', recurrent_activation='sigmoid',
                                        return_sequences=True, return_state=True)
        self.conv_setup2 = tf.keras.layers.Reshape((424, 424, rnn_units2))
        self.conv2d_3 = tf.keras.layers.Conv2D(filters=1, kernel_size=kernel_size, strides=(1, 1),
                                               padding='valid', activation='linear')

    def call(self, inputs, sol, states1=None, states2=None, return_state=True, training=False):
        """
        A single run through the recurrent inference machine
        conv2d -> gru -> conv2d_T -> gru -> conv2d
        When we go from a convolutional layer to a GRU, we need to first flatten the activation map. We then use the
        expand_dims function to make sure the input of the GRU has the correct format (batch length, feature dims, 1).
        Args:
            inputs: X_train -- used to calculate gradient
            sol: solution at time step t (x_t)
            states1: Hidden state of gru 1
            states2: Hidden state of gru 2
            return_state: Return the hidden state boolean
            training: Boolean determining whether or not the layer acts in training or inference mode
        """
        x = sol
        x = self.conv2d_1(x, training=training)
        if states1 is None:
            states1 = self.gru1.get_initial_state(x)
        x = self.gru_setup1(x)
        x = self.gru_setup2(x)
        x, states1 = self.gru1(x, initial_state=states1, training=training)
        x = self.conv_setup1(x)
        x = self.conv2d_2(x, training=training)

        if return_state:
            return x, states1, states2
        else:
            return x
