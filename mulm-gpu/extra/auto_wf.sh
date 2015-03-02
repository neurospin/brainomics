#!/bin/bash
generate_workflow=/ccc/work/cont003/dsv/lijpeng/brainomics/git/brainomics/ml/mulm_gpu/mulm/extra/generate_workflow.py
mapper=/ccc/work/cont003/dsv/lijpeng/brainomics/git/brainomics/ml/mulm_gpu/mulm/mu_corr_mapper_cuda.py
threshold=0.0001
seed=0
perm=10000
subj=1292
x_start=0
x_end=39
last_chunk_size=26
wf_name=mu_corr_cuda

for i in {1..17}; do 
    mkdir wf_${i};
    python $generate_workflow $PWD $x_start $x_end \
`expr \( ${i} - 1 \) \* 50` `expr ${i}  \* 50 - 1` \
$subj $mapper $perm $threshold $seed wf_${i};
    mv ${wf_name}_${x_start}_${x_end}_`expr \( ${i} - 1 \) \* 50`_`expr ${i}  \* 50 - 1`.json wf_${i}/
done;

i=`expr $i + 1`
mkdir wf_${i}
python $generate_workflow $PWD 0 39 \
`expr \( ${i} - 1 \) \* 50` `expr \( ${i} - 1 \) \* 50 + ${last_chunk_size}` \
$subj $mapper $perm $threshold $seed wf_${i};
mv ${wf_name}_${x_start}_${x_end}_`expr \( ${i} - 1 \) \* 50`_`expr \( ${i} - 1 \) \* 50 + ${last_chunk_size}`.json wf_${i}/