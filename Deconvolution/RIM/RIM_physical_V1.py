"""
Gradient calculations
"""
import tensorflow as tf
import numpy as np


def calc_grad(Y, A, C_N, x):
    """
    Calculate gradient of log likelihood function
    Args:
        Y - True "unconvolved" model
        A - Convolution matrix
        C_N - Covariance Matrix of Noise
        x - Current solution calculated from RIM
    """
    #print(Y)
    #print(A)
    #print(x)
    x = tf.cast(x, tf.float32)
    A = tf.cast(A, tf.float32)
    Y = tf.cast(Y, tf.float32)
    C_N = tf.cast(C_N, tf.float32)
    #print(A.shape)
    #print(x.shape)
    conv_sol = tf.math.multiply(A, x)
    #print(conv_sol.shape)
    resid = tf.math.subtract(Y,conv_sol)
    #print(resid.shape)
    resid_T = tf.transpose(resid, perm=[0,2,1])
    C_N_inv = tf.linalg.inv(C_N)
    #print(C_N.shape)
    res_CN = tf.math.multiply(resid_T, C_N_inv)
    return tf.math.multiply(res_CN, A)
