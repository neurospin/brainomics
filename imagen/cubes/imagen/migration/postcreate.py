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

"""cubicweb-imagen postcreate script, executed at instance creation time or when
the cube is added to an existing instance.

You could setup site properties or a workflow here for example.
"""

# Example of site property change
set_property('ui.site-title', "Imagen V2")

# Create CWusers from an existing list
# Taken from the catidb sources - thank you CATI!
users = {
    'user': '$6$rounds=31799$CBhboTW3sz8ZUlui$IRJB2i7qIN5ERK6IjpPYj3sUMLGZmy0efTDWKr0GaZETrM9gvMSth7g4VglOow7mQL4gLztYD27W12uiq9j2I/',
    'demo': '$6$rounds=27714$5Ddzu1eWvcJRGF8s$OVZJV8II9nBR8MUwl1qpECuMuyI0KwUYDvaTB.uii4RRTOlBrzoYTJysVJjw6XiZRHoh7N6PlJ.bbugh1yXks1',
}
from cubicweb import Binary
for login, upassword in users.items():
    rset = rql("INSERT CWUser X: X login '%s', X upassword '%s'" %
               (unicode(login), Binary(upassword)))
    user_eid = rset[0][0]
    rset = rql("SET U in_group G WHERE U eid %d, G name 'users'" % user_eid)
