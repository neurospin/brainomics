# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 09:47:59 2014

@author: jl237561
"""

import re
import os.path as osp

def is_useful_chromosome(chromosome_name):
    '''
    >>> is_useful_chromosome(u'chr6_apd_hap1')
    True
    >>> is_useful_chromosome(u'chr9_gl000198_random')
    False
    >>> is_useful_chromosome(u'chrX')
    True
    >>> is_useful_chromosome(u'chr1')
    True
    >>> is_useful_chromosome(u'chr11')
    True
    >>> is_useful_chromosome(u'chrUn_gl000229')
    False
    >>> is_useful_chromosome(u'chr6_dbb_hap3')
    True
    >>> is_useful_chromosome(u'chrUn_gl000225')
    False
    '''
    not_useful_patterns = [u"ch(.*)_random",
                           u"chrUn_(.*)"]
    for nu_pattern in not_useful_patterns:
        res = re.search(nu_pattern, chromosome_name)
        if res is not None:
            return False
    return True


if __name__ == "__main__":
    root_path = "/neurospin/brainomics/2014_bioresource"
    snps_data_path = osp.join(root_path,
                              "data/snps/snp138Common.txt")
    cleaned_snps_data_path = osp.join(root_path,
                                      "data/snps/cleaned_snp138Common.txt")
    num_snps = 0
    snps_names = set()
    with open(cleaned_snps_data_path, "w+") as outfile:
        with open(snps_data_path) as infile:
            for line in infile:
                words = line.split("\t")
                if len(words) > 0:
                    ch_name = unicode(words[1])
                    is_chr = is_useful_chromosome(ch_name)
                    if is_chr:
                        num_snps = num_snps + 1
                        snp_id = unicode(words[4])
                        if snp_id not in snps_names:
                            snps_names.add(snp_id)
                            outfile.write(line)
    print num_snps
    print "unique snp names=", len(snps_names)
