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
    'user': '$6$rounds=28507$FlW1OmppMNL5Nuds$HpXbSdLQoGO2ZH95Z7QRaXIHHw1D/j1jRQhOJhIf8M8Nycn.1DGFeq2qC0WCpzKctDATwj8TaXH9SQIm5VMKP/',
    'demo': '$6$rounds=28877$NgCSpnfClU7/Kury$WOF6dw7Ni31Q3q1H038q0pm7IipJFb9RS5PdctuBu1IrXEvFNWAgYqUOZJOIBOEA1KJBHxUcBW2ucGZT9dSv50',
}
from cubicweb import Binary
for login, upassword in users.items():
    rset = rql("INSERT CWUser X: X login '%s', X upassword '%s'" %
               (unicode(login), Binary(upassword)))
    user_eid = rset[0][0]
    rset = rql("SET U in_group G WHERE U eid %d, G name 'users'" % user_eid)
