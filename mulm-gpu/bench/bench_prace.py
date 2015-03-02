#! /usr/bin/env python
import numpy as np
import time
import sys


def mulm_gpu_bioproj(X, Y, Z, n_perm):
    from mulm.mu_corr_mapper_cuda import mapper
    X = X.astype('float32')
    Y = Y.astype('float32')
    Z = Z.astype('float32')
    _res = mapper(X, Y, Z, n_perm, sparsity_threshold=1e-4)
    return


def mulm_gpu_hybrid_bioproj(X, Y, Z, n_perm):
    from mulm.mu_corr_mapper_hybrid import parallel_permuted_mulm
    res_ = parallel_permuted_mulm(X.astype('float64'), Y, Z,
                                  n_perm, n_jobs=4)
    return


def test(X, Y, Z, n_perm):
    import mulm.mu_corr_mapper as lmcpu
    from mulm.mu_corr_mapper_cuda import mapper
    import scipy.sparse as ss

    res1, sizes1, _, th1, _ = lmcpu.mapper(
        X, Y, Z, 0, 0, 1, 0, n_perm, sparsity_threshold=1e-4)
    X = X.astype('float32')
    Y = Y.astype('float32')
    Z = Z.astype('float32')
    res2, sizes2, _, th = mapper(X, Y, Z, n_perm, sparsity_threshold=1e-4)
    i1 = np.argsort(res1, order=('data'))
    i2 = np.argsort(res2, order=('score'))
    end = min(len(res1), len(res2))
    res1_ = res1[i1[::-1]][:end]
    res2_ = res2[i2[::-1]][:end]
    np.testing.assert_almost_equal(res1_['data'], res2_['score'], decimal=3)
    s1 = s2 = 0
    d_shape = (X.shape[1], Y.shape[0])
    for perm_id in range(0, n_perm):
        e1 = s1 + sizes1[perm_id]
        e2 = s2 + sizes2[perm_id]
        r1 = res1[s1:e1]
        r2 = res2[s2:e2]
        d1 = ss.coo_matrix((r1['data'], (r1['snp'], r1['vox'])),
                           dtype='float32', shape=d_shape).todense()
        d2 = ss.coo_matrix((r2['score'], (r2['x_id'], r2['y_id'])),
                           dtype='float32', shape=d_shape).todense()
        mask = ((d1 - th) < 1e-4)
        mask += ((d2 - th) < 1e-4)
        mask &= (np.abs(d1 - d2) > 1e-4)
        if mask.sum() > 0:
            print ("perm_id %d (th: %f) : %s, %s" %
                   (perm_id, th, d1[mask], d2[mask]))
        np.testing.assert_almost_equal(d1[~mask], d2[~mask], decimal=3)
        s1 = e1
        s2 = e2
    print "### TEST successfull ###"
    return


if __name__ == '__main__':
    x_files = sys.argv[1]
    y_files = sys.argv[2]
    z_files = sys.argv[3]
    n_perm = int(sys.argv[4])
    algo = sys.argv[5]

    if algo == "GPU":
        func_call = mulm_gpu_bioproj
    elif algo == "HYBRID":
        func_call = mulm_gpu_hybrid_bioproj
    elif algo == "TEST":
        func_call = test
    else:
        print "unknown procedure"
        exit(42)

    X = np.load(x_files)['data']
    Y = np.load(y_files)['data']
    Z = np.load(z_files)

    print "Starting computation..."
    t0 = time.time()
    func_call(X, Y, Z, n_perm - 1)
    t1 = time.time()
    print "%s - Execution time: %.2f sec." % (algo, (t1 - t0))
