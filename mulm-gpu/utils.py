#!/usr/bin/env python
"""
Miscellaneous functions.

Author: Benoit Da Mota, June 2013

"""
import numpy as np
from scipy import linalg

# XXX: merge in linear_model.py

def normalize_matrix_on_axis(m, axis=0, copy=True):
    """ Normalize a 2D matrix on an axis.

    Parameters
    ----------
    m : numpy 2D array,
        The matrix to normalize
    axis : integer in {0, 1}, optional
        A valid axis to normalize accross (0 by default)

    Returns
    -------
    ret : numpy array, shape = m.shape
        The normalize matrix
    """
    if axis == 0:
        ret = m / np.sqrt(np.sum(m ** 2, axis=axis))
    elif axis == 1:
        ret = normalize_matrix_on_axis(m.T).T
    else:
        raise Exception('Only for 2D array.')
    if copy:
        ret = ret.copy()
    return ret


def orthonormalize_matrix(m, tol=1.e-12):
    """ Orthonormalize a matrix.

    Parameters
    ----------
    m : numpy array,
        The matrix to orthonormalize

    Returns
    -------
    ret : numpy array, shape = m.shape
        The orthonormalize matrix
    """
    U, s, _ = linalg.svd(m, 0)
    n_eig = s[abs(s) > tol].size
    tmp = np.dot(U, np.diag(s))[:, :n_eig]
    n_null_eig = tmp.shape[1] - n_eig
    if n_null_eig > 0:
        ret = np.hstack((
            normalize_matrix_on_axis(tmp),
            np.zeros((tmp.shape[0], n_null_eig))))
    else:
        ret = normalize_matrix_on_axis(tmp)
    return ret
