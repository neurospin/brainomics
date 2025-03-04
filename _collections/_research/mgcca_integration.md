---
layout: page
title: Multiway Generalized Canonical Correlation Analysis (MGCCA)
cat: methodology
subcat: integration
teasing: Regularized Generalized Canonical Correlation Analysis (RGCCA) is a general multiblock data analysis framework that encompasses several important multivariate analysis methods such as principal component analysis, partial least squares regression and several versions of generalized canonical correlation analysis.  RGCCA was extended to the case where at least one block has a tensor structure. This method is called Multiway Generalized Canonical Correlation Analysis (MGCCA).
contact: Arnaud.Gloaguen@supelec.fr, cathy.philippe@cea.fr, vincent.frouin@cea.fr
icon: mgcca_integration.png
added: 2019
---

![image-title-here]({{site.url}}/{{site.baseurl}}/images/research/{{page.icon}}){:class="image"}

&#169; NeuroSpin/CEA.


Multidisciplinary approaches are now common in scientific research and provide multiple and heterogeneous sources of measures of a given phenomenon. These sources can be viewed as a collection of interconnected datasets. The statistical analysis of multi-sources datasets introduces new degrees of freedom, which raise questions beyond those related to exploiting each source separately. In addition of this global multi-source structure, each source can have a specific structure represented in the form of higher-order tensors or matrices. Dedicated modelling algorithms able to cope with the inherent structural properties of such multi-source datasets are therefore mandatory for harnessing their complexity and provide relevant and robust information.

This issue has been already studied in the literature and yields many emerging fields called "learning from multimodal data", "data integration", "data fusion". The need to analyze conjointly the data by taking into account explicitly the global multi-source structure as well as the multiplicity of the orders of each source appears to be essential but requires the development of new statistical techniques.

Canonical Correlation Analysis (CCA) is one of the earliest model developed to capture relationships between two sets of variables. Several generalizations of CCA to more than two sets of variables have been proposed and different types of regularizations have been added for more consistent estimations of the CCA parameters in high dimensional settings. More recently, Regularized Generalized Canonical Correlation Analysis (RGCCA) has been proposed and subsumes many multiblock component methods as special cases.

Multiway Generalized Canonical Correlation Analysis (MGCCA) was developed in order to extend RGCCA to higher-order tensors.
