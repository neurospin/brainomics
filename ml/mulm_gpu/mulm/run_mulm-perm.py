#! /usr/bin/env python

#from __future__ import division
import swig.linear_model as lm
import os.path
import iodata
from os.path import join, split
import numpy as np

data_dir = "../data"

gen_filename = os.path.join(data_dir,
    "500-simu_gen-85772snps_min-allele-dosage-coding_MAF-5%_reordered.raw")
ima_filename = os.path.join(data_dir,
    "500-simu_ima-34rois_geneeffect.csv")
covar_filename = os.path.join(data_dir,
    "500-simu_covariates.csv")
results_fstat_filename = os.path.join(data_dir,
    "500-simu_results-mulm_fscores_ima=gen+covariates.txt")
permut_filename = os.path.join(data_dir,"permutations.txt");


X, Y, Z = iodata.read_XYZresults(gen_filename, ima_filename,
    covar_filename, permut_filename)

dev=0
VectorSize = 500
num_vector_X = 85772
num_vector_Y = 34
num_vector_Z = 3
num_permut = 2048
TRESHOLD = 10

cut = 90
divide = 4 * (int(num_permut*((100.0-cut)/100.0))+1)
print divide
Beta_Size=long(num_vector_X*num_vector_Y*divide)
print Beta_Size
X=(X.T).reshape(num_vector_X*VectorSize)
X=X.astype('float32')

Y=(Y.T).reshape(num_vector_Y*VectorSize)
Y=Y.astype('float32')

Z=np.append(Z,np.ones(VectorSize))
Z=(Z.T).reshape(num_vector_Z*VectorSize)
Z=Z.astype('float32')

indx=np.arange(VectorSize)
P=np.append([],indx)
for i in range(num_permut-1):
	np.random.shuffle(indx)
	P=np.append(P,indx)
P=P.astype('int32')
#Beta = lm.create_array(Beta_Size)
values , Beta = lm.MULMRegression(X, Y, Z, P,Beta_Size, VectorSize, divide, TRESHOLD, dev)

print values
Beta=np.resize(Beta,values*4)
Beta=np.reshape(Beta,(values,4))
print Beta

#print values
#np.savetxt('beta.txt', Beta)

