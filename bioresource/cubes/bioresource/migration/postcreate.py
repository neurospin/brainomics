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

"""cubicweb-ncbi postcreate script, executed at instance creation time or when
the cube is added to an existing instance.

You could setup site properties or a workflow here for example.
"""

# Example of site property change
set_property('ui.site-title', "dbSNP-eGene")

# Create cards
create_entity('Card', content_format=u'text/html', title=u'ncbi-index',
              content=u"""<div class="page-header"><h2>Genetics for Imaging</h2></div>
              <p>This DB server services some meta-information built from UCSC dump</p>
<p>This prototype was developed by D. Papadopoulos and V. Frouin</p>
<p><span class="badge badge-important">This website is in beta. Comments are welcome!</span></p>
""")