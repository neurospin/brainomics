"""
The joblib.Parallel MULM
"""
import joblib
import numpy as np
import multiprocessing as mp
import mulm.mu_corr_mapper as lmcpu
import mulm.mu_corr_mapper_cuda as lmgpu


def parallel_permuted_mulm(x, y, z, n_perm,
                    seed=0, sparsity_threshold=1e-4,
                    n_jobs=0, ratio=(4. / 5.)):
    """

    Parameters
    ----------
    x: array-like, shape=(n_samples, n_regressors)
      Explanatory variables.
    y: array-like, shape=(n_targets, n_samples)
      fMRI data.
    z: array-like, shape=(n_samples, n_covars)
      Clinical data (covariables).
    """
    if n_jobs < 1:
        n_jobs = joblib.cpu_count()
    pool = mp.Pool(processes=1)
    x_mid = x.shape[1] * ratio
    X1 = x[:, :x_mid].astype('float32')
    x = x[:, x_mid:]
    results = []
    results.append(pool.apply_async(
                lmgpu.mapper,
                args=(X1, y.astype('float32'), z.astype('float32'),
                      n_perm), ))

    sizes = np.linspace(0, x.shape[1], max(2, min(x.shape[1], n_jobs + 1))
                        ).astype(int)
    ret = joblib.Parallel(n_jobs=n_jobs)(joblib.delayed(
        lmcpu.mapper)
    (x[:, start:sizes[i + 1]], y, z, 0, 0, 1, seed, n_perm,
         sparsity_threshold=sparsity_threshold)
        for i, start in enumerate(sizes[:-1]))
    pool.close()
    pool.join()
    return results, ret
