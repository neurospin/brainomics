#! /usr/bin/env python
import numpy as np
import time
import sys

from mulm.mu_corr_mapper_cuda import mapper

if __name__ == '__main__':
    x_files = sys.argv[1]
    y_files = sys.argv[2]
    z_files = sys.argv[3]
    n_perm = int(sys.argv[4])

    X = np.load(x_files)['data']
    X = X[:, :]
    Y = np.load(y_files)['data']
    Y = Y[:, :]
    Z = np.load(z_files)

    X = X.astype('float32')
    Y = Y.astype('float32')
    Z = Z.astype('float32')

    print "Starting computation..."
    t0 = time.time()
    _res = mapper(X, Y, Z, n_perm - 1, sparsity_threshold=1e-4,
                  x_offset=0, y_offset=0)
    t1 = time.time()
    print "%s - Execution time: %.2f sec." % ("GPU", (t1 - t0))
