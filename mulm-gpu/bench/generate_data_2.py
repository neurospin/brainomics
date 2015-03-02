#! /usr/bin/env python
"""
Random gaussian iid data without effect.
"""
import numpy as np
import sys

if __name__ == '__main__':
    n_vector_Z = 10
    n_subj = 1534
    arch = sys.argv[1]
    if arch == 'HYBRID':
        n_vector_Y = 2560 / 10
        n_vector_X = 1600 * 10 / 8 * 2
    if arch == 'CPU':
        n_vector_Y = 2560
        n_vector_X = 1600 / 8
    if arch == 'GPU':
        n_vector_Y = 2560 / 10 / 8   # 32
        n_vector_X = 1600 * 10  # 16000
    if arch == 'EPAC':
        n_vector_Y = 2560 * 20
        n_vector_X = 1600 / 20  # 80

    rg = np.random.RandomState()
    rg.seed(42)

    Z = np.hstack((rg.randn(n_subj, n_vector_Z),
                   np.ones((n_subj, 1)).astype('float64')))
    Y = rg.randn(n_vector_Y, n_subj)
    X = np.abs(rg.randn(n_subj, n_vector_X) * 1.5).astype('uint8')
    X[X > 2] = 0
    X_size = float(X.shape[0] * X.shape[1])
    print ("Class distribution: %.2f, %.2f,  %.2f " %
           ((X == 0).sum() / X_size,
            (X == 1).sum() / X_size,
            (X == 2).sum() / X_size)),
    print X.shape

    np.save('z2.npy', Z)
    np.savez('x2.npz', X)
    np.savez('y2.npz', Y)
