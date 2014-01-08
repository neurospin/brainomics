# -*- coding: utf-8 -*-

rset = rql('Any X WHERE X is CWUser')
for cwuser in rset.entities():
    print cwuser.login, cwuser.upassword.getvalue()
