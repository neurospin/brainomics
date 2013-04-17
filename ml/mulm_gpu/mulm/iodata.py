#########
## READ IN PYTHON
#########

import numpy as np


def read_XYZresults(gen_filename, ima_filename, covar_filename,
    permut_filename):
    ### SNPs Data -------------------------------------------------------------
    X = np.fromfile(gen_filename, dtype='int32', count=500 * 85772,
                    sep="").reshape(85772, 500).T
    ### Imaging ---------------------------------------------------------------
    fdi = open(ima_filename, mode='rb')
    lines = fdi.readlines()
    header_ima = lines[0]
    data = lines[1:]
    Y = np.asarray([[float(i) for i in l.split()] for l in data])
    ### covariates ------------------------------------------------------------
    fdi = open(covar_filename, mode='rb')
    lines = fdi.readlines()
    header_covar = lines[0]
    data = lines[1:]
    Z = np.asarray([[float(i) for i in l.split()] for l in data])

    return X, Y, Z
