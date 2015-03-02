
#!/usr/bin/env python
"""
The mapper for MULM

Author: Benoit Da Mota, Oct. 2013

"""
import sys
import time
import numpy as np
import joblib
import scipy.stats as st

import mulm.build.linear_model as lm
import linear_model as lmcpu
import mulm.build.linear_model_ols as lmols

GPU_LINE_SIZE = 128  # size in bytes
SIZE_OF_ELEM = 4  # size in bytes


def _projections_of_data(x, y, z):
    """
    """
    # step 1 (regression 1): extract effect of z from y
    reg_1 = lmcpu._OrthoOLSRegression()
    y = reg_1.fit_transform(z, y)
    z = reg_1.x

    # step 2 (regression 2): extract effect of z from x
    reg_2 = lmcpu._OrthoOLSRegression(orthonormalize_x=False,
                                      check_contiguous=False)
    x = reg_2.fit_transform(z, x.T).copy()
    del reg_1, reg_2
    return x, y, z


def _compute_padded_size(n_samples, n_perm, n_y):
    """
    """
    # Padding n_samples
    n_samples += 1     # need 1 junk sample
    elements_per_line = (GPU_LINE_SIZE / SIZE_OF_ELEM)
    n_samples_padded = ((n_samples / elements_per_line) * elements_per_line +
        (elements_per_line if (n_samples % elements_per_line)
         else 0))

    # Padding n_perm
    n_perm_t = n_perm + 1
    permutations_per_block = (lm.get_bsize() / lm.get_block_sizey()
                              * lm.get_nb_permut_per_th())
    n_perm_padded = ((n_perm_t / permutations_per_block)
                     * permutations_per_block +
        (permutations_per_block if (n_perm_t % permutations_per_block)
         else 0))

    # padding Y
    n_y_padded = ((n_y / lm.get_block_sizey()) * lm.get_block_sizey() +
        (lm.get_block_sizey() if (n_y % lm.get_block_sizey())
         else 0))

    return n_samples_padded, n_perm_padded, n_y_padded


def _compute_alphas(y, z, P, n_perm, n_samples, final_shape):
    alphas = np.zeros(final_shape)
    for i in xrange(0, n_perm + 1):
        start = n_samples * i
        zp = z[P[i]]
        alpha = np.dot(y.T, zp)
        alphas[i, :y.shape[1]] = np.sum(alpha ** 2, 1).ravel()
    alphas = alphas.astype('float32')
    return alphas


def _array_padding(array, new_shape,
                   fill_with=0):
    new_array = np.zeros(new_shape, dtype=array.dtype)
    new_array[:array.shape[0], :array.shape[1]] = array
    if fill_with != 0:
        new_array[:, array.shape[1]:] = fill_with
        new_array[array.shape[0]:, :] = fill_with
    return new_array


def _get_permutations(n_perm, n_samples, rg):
    indx = np.arange(0, n_samples)
    P = np.empty((n_perm + 1, n_samples), dtype='int32')
    for i in xrange(0, n_perm + 1):
        P[i] = indx
        rg.shuffle(indx)
    return P


def _print_res(res_rec, sizes):
    p0 = res_rec[:sizes[0]]
    p0_ind = np.argsort(p0, order=('y_id', 'x_id'))
    for a, b, c, d in p0[p0_ind][:10]:
        print "%.8f\t%d\t%d\t%d" % (d, b, c, a)
    print "..."
    p_end = res_rec[np.sum(sizes[:-1]):]
    p_end_ind = np.argsort(p_end, order=('y_id', 'x_id'))
    for a, b, c, d in p_end[p_end_ind][-10:]:
        print "%.8f\t%d\t%d\t%d" % (d, b, c, a)


def _construct_sizes(perm, n_perm):
    if np.sum(np.unique(perm) + 1) == np.sum(np.arange(1, n_perm + 2)):
        sizes = np.where((perm[1:] - perm[:-1]) > 0)[0]
        end = len(perm) - 1 - sizes[-1]
        sizes[1:] = sizes[1:] - sizes[:-1]
        sizes = np.hstack((sizes, [end]))
        sizes[0] += 1
    else:  # slow method
        print "Warning: Threshold is too high."
        sizes = np.array([(perm == p_id).sum() for p_id in range(n_perm + 1)])
    return sizes


def _construct_results(beta, sizeret, n_perm, threshold,
                       x_offset, y_offset, beta_size):
    beta.shape = (beta_size / 4, 4)
    # data, vox , snp, perm
    # pos_mask = (beta[:, 0] >= threshold)
    res_rec = np.empty(sizeret, dtype=[('perm_id', np.int32),
             ('x_id', np.int32), ('y_id', np.int32), ('score', np.float32)])
    tmp_perm = beta[:sizeret, 3]
    perm_findex = np.argsort(tmp_perm)
    res_rec['perm_id'] = tmp_perm[perm_findex]
    res_rec['x_id'] = beta[:sizeret, 1][perm_findex]
    res_rec['y_id'] = beta[:sizeret, 2][perm_findex]
    res_rec['score'] = beta[:sizeret, 0][perm_findex]
    #  y_offset, x_offset
    res_rec['y_id'] += y_offset
    res_rec['x_id'] += x_offset

    sizes = _construct_sizes(res_rec['perm_id'], n_perm)
    return res_rec, sizes


def mapper(x, y, z, n_perm, x_offset=0, y_offset=0, seed=0,
           sparsity_threshold=1e-4, summary=False, dev=0):
    """
    """
    n_y = y.shape[0]
    n_x = x.shape[1]
    n_z = z.shape[1]
    print "Arguments : "
    print "num_vector_X : %d" % n_x
    print "num_vector_Y : %d" % n_y
    print "num_vector_Z : %d" % n_z
    print "num_permut : %d" % (n_perm + 1)
    print "VectorSize : %d" % x.shape[0]
    # initialize the seed of the random generator
    rg = np.random.RandomState(seed)

    # perm will store al the permutations, each element of this list
    # is a sparse matrix of shape = [n_phenotype, n_snp]
    n_samples = x.shape[0]

    # we keep F score for which p values are < sparsity_threshold
    threshold = st.f.isf(sparsity_threshold, 1,
                         n_samples - n_z - 1)
    print "Threshold : %f" % threshold
    t_r0 = time.time()
    # array of permutations
    P = _get_permutations(n_perm, n_samples, rg)
    t_r1 = time.time()

    # projection of the data
    x, y, z = _projections_of_data(x, y, z)

    # compute size of arrays with padding
    n_samples_padded, n_perm_padded, n_y_padded = (
        _compute_padded_size(n_samples, n_perm, n_y))

    y = y.T
    # padding
    x = _array_padding(x, (n_samples_padded, n_x))
    z = _array_padding(z, (n_samples_padded, n_z))
    P = _array_padding(P, (n_perm_padded, n_samples_padded),
                       fill_with=n_samples)
    y = _array_padding(y, (n_y_padded, n_samples_padded))

    t_pre1_ = time.time()

    # alphas (correction of the bias with covariables)
    beta_size = int(n_y_padded * n_perm_padded)
    [sizeret, alphas] = lmols.OLSRegression(
        z.T.ravel().copy(), y.T.ravel(), P.ravel(),
        beta_size, n_samples_padded, dev)
    alphas = alphas.reshape((n_perm_padded, n_y_padded)
                            ).astype('float32')  # [:n_perm + 1, :n_y]

    t_pre1 = time.time()

    # kernel CUDA
    divide = max(int(2 * sparsity_threshold * n_perm), 1) + 1
    beta_size = int(4 * x.shape[1] * y.shape[0] * divide)
    [sizeret, beta] = lm.MULMRegression(
        x.T.ravel().copy(), y.T.ravel(),
        alphas.ravel(), P.ravel(),
        beta_size,  z.size, n_samples_padded, n_samples,
        divide, threshold, dev)
    t0 = time.time()

    # construct Results
    res_rec, sizes = _construct_results(beta, sizeret, n_perm, threshold,
                                        x_offset, y_offset, beta_size)
    t_end = time.time()

    print
    _print_res(res_rec, sizes)
    print "\nnumber of CUDA   returned values: %d" % sizeret
    print "Rand Python: %.2f sec." % (t_r1 - t_r0)
    print "Pre  Python: %.2f sec." % (t_pre1_ - t_r1)
    print "kernel CUDA alpha: %.2f sec." % (t_pre1 - t_pre1_)
    print "kernel CUDA  beta: %.2f sec." % (t0 - t_pre1)
    return res_rec, sizes, n_z, threshold


def mapper_file(samples, permutations, z_file, y_file, x_file,
                result_file, sparsity_threshold=1e-4,
                out_format='joblib', dev=0):
    """The mapper function: OLS on a tile of data.
    """

    start_time = time.time()

    # read the data
    z_data = np.load(z_file).astype('float32')      # Covariates data
    y_arr = np.load(y_file)
    y_data = y_arr['data'].astype('float32')          # phenotypes data
    y_offset = y_arr['offset']      # offset of y_data respectively to
                                    # original indexes

    x_arr = np.load(x_file)
    x_data = x_arr['data'].astype('float32')          # regressors data
    x_offset = x_arr['offset']      # offset of x_data respectively to
                                    # original indexes

    sample_1 = x_data.shape[0]
    sample_2 = z_data.shape[0]
    sample_3 = y_data.shape[1]

    # check dataset sanity
    if sample_1 != samples:
        # exception prevent reducer failure after many mapper computation
        raise Exception('Number of samples erroneous.')
    if sample_1 != sample_2 or sample_1 != sample_3:
        raise Exception('Matrix have not the same number of observations.')

    # lauch mapper on data
    raw_res, sizes, lost_dof, threshold = mapper(
        x_data, y_data, z_data, permutations,
        x_offset=x_offset, y_offset=y_offset, seed=seed,
        sparsity_threshold=sparsity_threshold,
        dev=dev)
    # compute degrees of freedom
    dof = samples - 1 - lost_dof

    # save the result_file
    res_dic = {'threshold': threshold,
               'sparse_results': raw_res, 'rk2': 1, 'dof': dof,
               'n_results_per_perm': sizes}
    joblib.dump(res_dic, result_file, compress=1, cache_size=100)

    print ('Results wrote in %s' % (result_file))


if __name__ == '__main__':

    # basic arg parse
    samples = int(sys.argv[1])       # number of subjects
    seed = int(sys.argv[2])          # seed for random
    permutations = int(sys.argv[3])  # number of permutations
    z_file = sys.argv[4]             # covariables (clinical)
    y_file = sys.argv[5]             # voxel data (fmri)
    x_file = sys.argv[6]             # genetic data (SNP)
    result_file = sys.argv[7]        # output files

    # optional sparsity threshold (tweaks the amount of collected data)
    try:
        sparsity_threshold = float(sys.argv[8])
    except:
        sparsity_threshold = 1e-4

    import os
    try:
        dev_ = int(os.environ['SLURM_PROCID']) % 2
        print '### ID device CPU/GPU =', dev_
    except:
        dev_ = 0
    # call the mapper with parameters
    mapper_file(samples, permutations - 1, z_file, y_file, x_file,
           result_file, sparsity_threshold=sparsity_threshold,
           dev=dev_)
