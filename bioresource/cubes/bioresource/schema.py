# -*- coding: utf-8 -*-
# copyright 2013 Vincent Frouin, all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-ncbi schema"""

from yams.buildobjs import (EntityType, RelationDefinition,
                            SubjectRelation, String, RichString,
                            BigInt, Int, Float, Boolean)
#
#from cubes.genomics.schema import GenomicPlatform
#from cubes.genomics.schema import Snp
#from cubes.genomics.schema import Gene
#from cubes.medicalexp.schema import Assessment
#from cubes.medicalexp.schema import concerned_by
# from cubes.medicalexp.schema import GenomicMeasure
#from cubes.medicalexp.schema import Assessment
#from cubes.medicalexp.schema import ProcessingRun
#from cubes.medicalexp.schema import ScoreDefinition
#from cubes.medicalexp.schema import ScoreValue

# Remove identifier and add name
#GenomicPlatform.add_relation(String(maxsize=64, fulltextindexed=True),
#                             name='name')
#GenomicPlatform.remove_relation(name="identifier")

# Snp.remove_relation(name="gene")
# Gene.add_relation(SubjectRelation('Snp', cardinality='**'), name='genes')

# One gene could have several genes, 
# and one chromosome could have serveral genes
# Don't change them
#Gene.remove_relation(name="chromosomes")
## change SubjectRelation('Chromosome', cardinality='?*').cardinality to "**"
#Gene.add_relation(SubjectRelation('Chromosome', cardinality='?*'),
#                  name='chromosome')

## It doesn't work
# GenomicMeasure.remove_relation(name='concerns')
# GenomicMeasure.add_relation(SubjectRelation('SubjectGroup', cardinality='?*'), name='concerns')



#GenomicPlatform.add_relation(String(maxsize=64, fulltextindexed=True),
#                             name='name')
#GenomicPlatform.remove_relation(name="identifier")
#
#Snp.remove_relation(name="gene")
#
#Gene.add_relation(SubjectRelation('Snp', cardinality='**'), name='snps_genes')
#
#Gene.remove_relation(name="chromosomes")
#Gene.add_relation(SubjectRelation('Chromosome', cardinality='?*'),
#                  name='chromosome')
#
#Assessment.remove_relation(name='related_study')
#Assessment.add_relation(SubjectRelation('Study', cardinality='?*'),
#                        name='related_study')
#
#concerned_by.cardinality = "**"



# Todo: Change cardinality of Snp
# Todo: add relation from gene to snp (?*), the name of relation is snps