#!/usr/bin/python
# -*- coding: utf-8 -*-

def delete_from_ldap(ldapobject, base):
    # delete all accounts
    dn = 'ou=People,' + base
    filterstr = '(objectClass=inetOrgPerson)'
    for dn, attrs in ldapobject.search_s(dn, ldap.SCOPE_ONELEVEL, filterstr, []):
        ldapobject.delete_s(dn)
    # remove all accounts from the restricted "partners" group
    dn = 'cn=partners,ou=Group,' + base
    attributes = [(ldap.MOD_DELETE, 'memberUid', None)]
    ldapobject.modify_s(dn, attributes)

import ldap

host = 'ldap://132.166.140.10'
host = 'ldap://imagen2i.intra.cea.fr'
BASE = 'dc=imagen2,dc=cea,dc=fr'
BASE = 'dc=example,dc=com'
username = 'cn=admin,' + BASE
password = 'kelbordel'
ldapobject = ldap.initialize(host)
ldapobject.simple_bind_s(username, password)
delete_from_ldap(ldapobject, BASE)
