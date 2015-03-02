"""
Ordinary Least Square regression models.

Author: Benoit Da Mota, sept. 2011
"""

import numpy as np
import scipy.stats as st

from utils import orthonormalize_matrix, normalize_matrix_on_axis


class _OrthoOLSRegression(object):
    """Ordinary Least Square regression in the general case.

    Parameters
    ----------
    orthonormalize_x : boolean, optional
        if true, orthonormalize x

    normalize_y : boolean, optional
        if true, normalize each target in y

    check_contiguous : boolean, optional
        check if the data are contiguous for CPU performance purpose

    Attributes
    ----------
    `beta_` : numpy array, shape (n_targets, n_features)
        Estimated coefficients for the linear regression problem.

     `x` : numpy array, shape = [n_samples, n_features]
        Design Matrix

     `y` : numpy array, shape = [n_targets, n_samples]
        Targets values

    Notes
    -----
    Only for MULMRegression internal use.
    """
    def __init__(self, orthonormalize_x=True, normalize_y=True,
                 check_contiguous=True):
        self.orthonormalize_x = orthonormalize_x
        self.normalize_y = normalize_y
        self.check_contiguous = check_contiguous
        self.beta_ = None

    def fit(self, X, Y):
        """
        fit an OLS on each line of Y with X.

        Parameters
        ----------
        X : numpy array, shape = [n_samples, n_features]
            Design Matrix
        Y : numpy array, shape = [n_targets, n_samples]
            Targets values
        """
        # store the orthonormalize version of x
        if self.orthonormalize_x:
            self.x = orthonormalize_matrix(X)
        else:
            self.x = X
        # store the normalize version of y
        if self.normalize_y:
            self.y = normalize_matrix_on_axis(Y, axis=1)
        else:
            self.y = Y
        # verify CONTIGUOUS property
        if self.check_contiguous:
            if self.y.flags['C_CONTIGUOUS'] is False:
                raise Exception('y not C_CONTIGUOUS.')
            if self.x.flags['C_CONTIGUOUS'] is False:
                raise Exception('x not C_CONTIGUOUS.')

        # compute and store beta, i.e. matrix of the coefficients
        self.beta_ = np.dot(self.y, self.x)

        return self

    def transform(self):
        """
        Returns the residuals of the regression.

        """
        if self.beta_ is None:
            raise Exception('Must call fit method first.')
        y_rx = self.y - np.dot(self.beta_, self.x.T)
        y_rx = normalize_matrix_on_axis(y_rx, axis=1)
        return y_rx.T

    def fit_transform(self, X, Y):
        """
        Fit and transform (cf. fit and transform methods).

        Parameters
        ----------
        X : numpy array, shape = [n_samples, n_features]
            Design Matrix
        Y : numpy array, shape = [n_targets, n_samples]
            Target phenotypes values
        """
        return self.fit(X, Y).transform()


class _OLSRegressionMassVector(object):
    """ Fast univariate OLS regression.

    Parameters
    ----------
    normalize_x : boolean, optional
        if true, normalize x

    normalize_y : boolean, optional
        if true, normalize y

    check_contiguous : boolean, optional
        check if the data are contiguous for CPU performance purpose

    lost_dof : integer, optional
        previously lost degrees of freedom (ex. previous OLS)

    Attributes
    ----------
    `beta_` : numpy array, shape (n_targets, n_features)
        Estimated coefficients for the features in x.

    `alpha_` : numpy array, shape (n_targets, n_features)
        Estimated coefficients for the covariables in z.

     `x` : numpy array, shape = [n_samples, n_features]
        Design Matrix

     `y` : numpy array, shape = [n_targets, n_samples]
        Targets values

     `z` : numpy array, shape = [n_samples, n_confounds], optional
        Confounds values

    Notes
    -----
    Only for MULMRegression internal use.
    """
    def __init__(self, normalize_x=True, normalize_y=True,
                 check_contiguous=True, lost_dof=0):
        self.normalize_x = normalize_x
        self.normalize_y = normalize_y
        self.check_contiguous = check_contiguous
        self.lost_dof = lost_dof
        self.alpha_ = None
        self.beta_ = None

    def fit(self, X, Y, Z=None):
        """
        Fit OLS.

        Parameters
        ----------
        X : numpy array, shape = [n_samples, n_features]
            Design Matrix
        Y : numpy array, shape = [n_targets, n_samples]
            Targets values
        Z : numpy array, shape = [n_samples, n_confounds], optional
            array of confounds (must be orthonormalized)

        Notes
        -----
        if Z is not None, it must be orthonormalized before. This option
        is only provide for internal use with MULMRegression.
        """
        # store the normalize version of x
        if self.normalize_x:
            self.x = normalize_matrix_on_axis(X)
        else:
            self.x = X
        # store the normalize version of y
        if self.normalize_y:
            self.y = normalize_matrix_on_axis(Y, axis=1)
        else:
            self.y = Y
        self.z = Z

        # verify CONTIGUOUS property
        if self.check_contiguous:
            if self.y.flags['C_CONTIGUOUS'] is False:
                raise Exception('y not C_CONTIGUOUS.')
            if self.x.flags['C_CONTIGUOUS'] is False:
                raise Exception('x not C_CONTIGUOUS.')

        self.beta_ = np.dot(self.y, self.x)
        if Z is not None:
            self.alpha_ = np.dot(self.y, self.z)
        else:
            self.alpha_ = None

        return self

    def _raw_F_score(self):
        """
        compute and return the F_score, degrees of freedom and rank.

        Returns
        -------
        F: numpy array, shape = [n_targets, n_features]
            Array of F scores
        dof: integer
            Degrees of freedom
        """
        # dof is the degrees of freedom
        dof = self.y.shape[1] - 1 - self.lost_dof
        b_size = self.x.shape[1]
        b2 = (self.beta_ ** 2)
        # residual sum of square
        if self.alpha_ is None:
            rss = (1 - b2)
        else:
            a2 = np.sum(self.alpha_ ** 2, 1)
            a2 = a2.repeat(b_size).reshape((-1, b_size))
            rss = (1 - a2 - b2)
        F = b2 / rss
        F *= dof
        return F, dof

    def score(self):
        """
        Compute scores for the linear model w.r.t. contrast.

        Returns
        -------
        results: numpy array, shape = [n_targets, n_features]
            array of scores (F scores)
        """
        result, dof = self._raw_F_score()
        return result


class MULMRegression(object):
    """Ordinary Least Square regression in the case of a multiple
    scalar design matrix and with z and with group of regressors.

    Notes
    -----
    each group must have the same size

    Methods
    -------
    fit
        Fit the model to the training data.
    score
        Evaluate the model according to a contrast.
    """
    def fit(self, x, y, z, from_cache=False, lost_dof=0):
        """ Fit the model to the training data.

            XXX: docstring: from_cache, lost_dof
        """
        self.n_subjects = z.shape[0]
        self.lost_dof = lost_dof
        if from_cache:
            # XXX: s/z_on/z_orthonormed: + write what names mean
            self.z_on = z
            # XXX: y_res_z + write what names
            self.y_rz_n = y
            self.x_rz_on = x
        else:
            # step 1 (regression 1): extract effect of z from y
            reg_1 = _OrthoOLSRegression()
            self.y_rz_n = reg_1.fit_transform(z, y).T
            self.z_on = reg_1.x
            self.lost_dof += (self.z_on.shape[1])
            del y, reg_1

            # step 2 (regression 2): extract effect of z from x
            reg_2 = _OrthoOLSRegression(orthonormalize_x=False,
                                        check_contiguous=False)
            self.x_rz_on = reg_2.fit_transform(self.z_on, x.T).copy()
            del x, reg_2

        # step 3: original regression (3)
        self._reg = _OLSRegressionMassVector(
            normalize_x=False, normalize_y=False, lost_dof=self.lost_dof)
        self._reg.fit(self.x_rz_on, self.y_rz_n, Z=self.z_on)

        return self

    def score(self):
        """ Compute scores for the linear model
        """
        return self._reg.score()

    def get_cache(self):
        """ get cached matrices for reuse in another MULMRegression
        """
        return self.x_rz_on.copy(), self.y_rz_n, self.z_on.copy()

    # XXX Rename to 'get_threshold'?
    def threshold(self, pval):
        """ transform pval (or sparsity_threshold in the F_score scale

        Notes: requires a fit
        """
        try:
            return st.f.isf(
                pval, 1, self.n_subjects - self.lost_dof - 1)
        except:
            raise Exception("Requires a fit first")
