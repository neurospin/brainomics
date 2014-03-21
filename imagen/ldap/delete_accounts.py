#!/usr/bin/python
# -*- coding: utf-8 -*-

host = 'ldap://132.166.140.10'
host = 'ldap://imagen2i.intra.cea.fr'
BASE = 'dc=imagen2,dc=cea,dc=fr'


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
import getpass

username = 'cn=admin,' + BASE
ldapobject = ldap.initialize(host)
while True:
    password = getpass.getpass(prompt='LDAP administrator password? ')
    try:
        ldapobject.simple_bind_s(username, password)
    except ldap.INVALID_CREDENTIALS:
        continue
    else:
        break        
delete_from_ldap(ldapobject, BASE)
ldapobject.unbind_s()
