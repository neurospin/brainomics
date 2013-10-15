# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-localizer postcreate script, executed at instance creation time or when
the cube is added to an existing instance.

You could setup site properties or a workflow here for example.
"""

# Example of site property change
set_property('ui.site-title', "Brainomics/Localizer")

# Remove the Card on the Brainomics project from the front page
session.execute("DELETE Card X WHERE X title 'index'")
create_entity('Card', content_format=u'text/html', title=u'index',
              content=u"""<div class="page-header"><h1>Brainomics/Localizer database</h1></div>
              <p><span class="badge badge-important">This website is still in beta. Comments are welcome!</span></p>
              <p> <strong>Feel free to play with it! Use the RQL <i>Search</i> field in the bar at the top of the page.</strong></p>""")
