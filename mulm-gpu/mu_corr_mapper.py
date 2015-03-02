#!/usr/bin/env python
"""
The mapper for MULM

Author: Benoit Da Mota, Feb. 2012

"""
import sys
import time
import numpy as np
import scipy.stats as st

import mulm.linear_model as lm


def dense_to_sparse_recarray(res, threshold, y_offset, z_offset):
    """Sparsify result into sparse recarray and sort.
    """
    # we only store float32 to save space
    res = res.astype('float32')
    # we sparsify the matrix wrt. threshold
    # dense to coordinate list
    res_row, res_col = (res >= threshold).nonzero()
    res_data = res[res_row, res_col]
    # coordinate to recarray
    res_rec = np.empty(res_data.shape, dtype=[('snp', np.int32),
                        ('vox', np.int32), ('data', np.float32)])
    res_rec['snp'][:] = res_col + z_offset
    res_rec['vox'][:] = res_row + y_offset
    res_rec['data'][:] = res_data

    return (res_rec, res_data.shape[0])


def list_to_recarray(perm, n_perm):
    """ store the 3D recarray in a bigger 4D recarray.
    """
    perm, sizes = zip(*perm)
    shape = (sum(sizes))
    res_rec = np.empty(shape, dtype=[('perm', np.int32),
            ('snp', np.int32), ('vox', np.int32), ('data', np.float32)])
    cursor = 0
    for i in range(n_perm + 1):
        res_rec[cursor:cursor + sizes[i]]['snp'][:] = \
                perm[i]['snp'][:]
        res_rec[cursor:cursor + sizes[i]]['vox'][:] = \
                perm[i]['vox'][:]
        res_rec[cursor:cursor + sizes[i]]['data'][:] = \
                perm[i]['data'][:]
        res_rec[cursor:cursor + sizes[i]]['perm'][:] = i
        cursor += sizes[i]
    return res_rec, np.array(sizes)


def mapper(x, y, z, x_offset, y_offset, group_x_by, seed, n_perm,
           sparsity_threshold=1e-4, summary=False):
    """

    /!\ caveat: set numpy's seed globally. Check the behavior of subsequent
        use of numpy within your script after calling this method.

    Parameters
    ----------
    x: array-like, shape=(n_covars, n_samples)
      Clinical data.
    y: array-like, shape=(n_targets, n_samples)
      fMRI data.
    z: array-like, shape=(n_regressors, n_samples)
      Explanatory variables.
    x_offset:
    y_offset:
    group_x_by:
    seed: int,
      Seed for random number generator, to have the same permutations
      in each computing units.
      /!\ caveat: set numpy's seed globally. Check the behavior of subsequent
          use of numpy within your script after calling this method.
    n_perm: int,
      Number of permutations
    sparsity_threshold: float,
      Threshold under the which the OLS f-value of a given voxel is not kept
      because likely not to be the max.
    summary: bool,
      Write a summary or not.

    """
    # initialize the seed of the random generator
    rg = np.random.RandomState(seed)

    # perm will store al the permutations, each element of this list
    # is a sparse matrix of shape = [n_phenotype, n_snp]
    perm = list()

    # OLS regression on original data
    reg = lm.MULMRegression()
    res1 = reg.fit(x, y, z).score()
    samples = x.shape[0]
    lost_dof = reg.lost_dof

    # we sparsify the matrix:
    # we keep F score for which p values are < sparsity_threshold
    threshold = st.f.isf(sparsity_threshold, 1,
                         samples - z.shape[1] - 1)
    perm.append(dense_to_sparse_recarray(res1, threshold, y_offset, x_offset))

    # end of original computation
    original_time = time.time()

    # construct matrices with cached results
    x_r, y_r, z_on = reg.get_cache()

    # construct the fancy-indexing vector that we will permute
    pidx = np.arange(0, x.shape[0])

    # do the permutations:
    # same seed between all mappers
    for i in range(0, n_perm):
        # shuffle data: for the computational cost, we choose to shuffle
        # x_r and z_on instead of y_r
        rg.shuffle(pidx)
        x_r_ = x_r[pidx]
        z_on_ = z_on[pidx]

        # create the regression, fit and score on shuffled data
        reg = lm.MULMRegression()
        reg.fit(x_r_, y_r, z_on_, from_cache=True,
                lost_dof=lost_dof)
        cur_res = reg.score()

        # we sparsify the matrix and
        # create the corresponding sparse matrix, which support
        # indexing and fast access by SNP, then by voxel
        perm.append(dense_to_sparse_recarray(cur_res, threshold, y_offset,
                                             x_offset))
    # Transform list of (recarray (3D), size) in recarray 4D + list of sizes
    perm, sizes = list_to_recarray(perm, n_perm)
    return perm, sizes, lost_dof, threshold, original_time


def mapper_file(samples, seed, permutations, z_file, y_file, x_file,
                result_file, sparsity_threshold=1e-4, summary=False,
                out_format='joblib', group_x_by=1):
    """The mapper function: OLS on a tile of data.
    """
    if summary:
        start_time = time.time()

    # read the data
    z_data = np.load(z_file)      # Covariates data (or only a constant column)
    y_arr = np.load(y_file)
    y_data = y_arr['data']          # phenotypes data
    y_offset = y_arr['offset']      # offset of y_data respectively to
                                    # original indexes
    y_max = y_arr['max'].tolist()   # total number of phenotypes
    x_arr = np.load(x_file)
    x_data = x_arr['data']          # regressors data
    x_offset = x_arr['offset']      # offset of x_data respectively to
                                    # original indexes
    x_max = x_arr['max'].tolist()   # total number of regressors

    res_shape = {'max_snp': x_max, 'max_vox': y_max}

    sample_1 = x_data.shape[0]
    sample_2 = z_data.shape[0]
    sample_3 = y_data.shape[1]

    # check dataset sanity
    if sample_1 != samples:
        # exception prevent reducer failure after many mapper computation
        raise Exception('Number of samples erroneous.')
    if sample_1 != sample_2 or sample_1 != sample_3:
        raise Exception('Matrix have not the same number of observations.')

    if summary:
        n_asso = y_data.shape[0] * x_data.shape[1] * (1 + permutations)\
            / 1000000

    # lauch mapper on data
    perm, sizes, lost_dof, threshold, original_time = \
        mapper(x_data, y_data, z_data, x_offset, y_offset, group_x_by, seed,
               permutations,
               sparsity_threshold=sparsity_threshold, summary=summary)
    # compute degrees of freedom
    dof = samples - group_x_by - lost_dof

    # save the result_file (file for the Reducer)
    if out_format == 'hdf5':
        try:
            import h5py
        except:
            out_format = 'joblib'
            if summary:
                print 'Warning: h5py not found, switch to numpy.savez'
    if out_format == 'joblib':
        import gstat.data.result_file as gdr
        f_obj = gdr.ResultFileJoblib(result_file + '.joblib')
        f_obj.save_result({'shape': res_shape, 'threshold': threshold,
                           'perm': perm, 'rk2': group_x_by, 'dof': dof,
                           'sizes': sizes})
    elif out_format == 'hdf5':
        # result = h5py.File(result_file + '.hdf5', mode='w')
        # result.create_group('perm')
        # for i in range(0, len(perm)):
        #     snp_dataset = '%d_snp' % i
        #     vox_dataset = '%d_vox' % i
        #     data_dataset = '%d_data' % i
        #     h = perm[i]
        #     if len(perm[i]) > 0:
        #         result['perm'].create_dataset(vox_dataset, data=h['vox'])
        #         result['perm'].create_dataset(snp_dataset, data=h['snp'])
        #         result['perm'].create_dataset(data_dataset, data=h['data'])
        # result.attrs['threshold'] = threshold
        # result.attrs['max_snp'] = res_shape['max_snp']
        # result.attrs['max_vox'] = res_shape['max_vox']
        pass
        # result.close()

    # print a summary
    if summary:
        tot_time = time.time() - start_time
        print '\nScore(s) better than the threshold: %f (p_value = %.15f)' % \
                   (threshold, st.f.sf(threshold, group_x_by, dof))
        print '  (vox, snp)\tF score'
        print '  ----------\t-------'
        print perm
        print '\nSize of groups: %d' % group_x_by
        print 'Execution time\t: %.6f sec' % (tot_time)
        print 'First reg. time\t: %.6f sec' % (original_time - start_time)
        if permutations > 0:
            print ('time per perm. \t: %.6f sec'
            % ((tot_time - (original_time - start_time))
               / float(permutations)))
        print 'Estimated speed\t: %.2f.e6 associations/sec'\
            % (n_asso / tot_time)
        print 'Results wrote in %s out_format is %s' % \
            (result_file + '.' + out_format, out_format)


if __name__ == '__main__':
    """
    EXAMPLE of a job launch:

python mulm_mapper.py \
1835 1 19 clinical.npy vox_chunk_6.npz snp_chunk_1.npz res_6_1.npz \
joblib 0.0001 2
    """
    summary = True

    # basic arg parse
    samples = int(sys.argv[1])       # number of subjects
    seed = int(sys.argv[2])          # seed for random
    permutations = int(sys.argv[3])  # number of permutations
    z_file = sys.argv[4]             # covariables (clinical)
    y_file = sys.argv[5]             # voxel data (fmri)
    x_file = sys.argv[6]             # genetic data (SNP)
    result_file = sys.argv[7]        # output files

    # optional output format ('joblib' or 'hdf5')
    try:
        out_format = sys.argv[8]
    except:
        out_format = 'joblib'
    # optional sparsity threshold (tweaks the amount of collected data)
    try:
        sparsity_threshold = float(sys.argv[9])
    except:
        sparsity_threshold = 1e-4
    try:
        group_x_by = int(sys.argv[10])  # number of categories for these chunks
    except:
        group_x_by = 1
    # call the mapper with parameters
    mapper_file(samples, seed, permutations, z_file, y_file, x_file,
           result_file, sparsity_threshold=sparsity_threshold, summary=summary,
           out_format=out_format, group_x_by=group_x_by)
