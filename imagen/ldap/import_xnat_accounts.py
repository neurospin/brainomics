#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import re


def _html_entity_decode(matchobj):
    return unichr(int(matchobj.group(1)))


def unescape(s):
    """Converts HTML numeric character references to their applicable
    characters.

    A `numeric character reference`_ looks like &#931; and is converted
    to its applicable code point of the Universal Character Set - in
    the case of &#931; the applicable character is Σ.

    Parameters
    ----------
    s : str
        String with numeric character references to convert.

    Returns
    -------
    unicode
        Converted string, with numeric character references replaced by
        their applicable characters.

    .. _numeric character reference: http://en.wikipedia.org/wiki/Numeric_character_reference

    """
    if isinstance(s, str):
        s = unicode(s, 'utf-8')
    return re.sub(r'&#(\d+);', _html_entity_decode, s)


def deobfuscate(password):
    """Decode obfuscated XNAT passwords.

    Up to XNAT 1.5.3, passwords where stored in plain-text or obfuscated
    form. See `Encrypt Stored Passwords`_ in the XNAT documentation. The
    obfuscation code is in `ObfuscatedPasswordEncoder.java`_ and mainly
    invloves a `XOR cipher`_ which is easily decrypted by merely
    reapplying the XOR function.

    Parameters
    ----------
    password : unicode
        Obfuscated password.

    Returns
    -------
    unicode
        Plain text password.

    .. _Encrypt Stored Passwords: https://wiki.xnat.org/display/XNAT16/Encrypt+Stored+Passwords
    .. _ObfuscatedPasswordEncoder.java: http://hg.xnat.org/xdat_1_6dev/src/d788dd4e62d5852f14038968258454bf96c5484d/src/main/java/org/nrg/xdat/security/ObfuscatedPasswordEncoder.java
    .. _XOR cipher: http://en.wikipedia.org/wiki/XOR_cipher

    """
    g = 2
    plain_text = ''.join([unichr(g ^ ord(x)) for x in password])
    return plain_text


def parse_psql_dump(psqlfile):
    """Parse XNAT accounts as dumped by the ``psql`` command.

    To output a list of accounts in the expected format::

        psql -t -c 'SELECT login, firstname, lastname, email, primary_password, primary_password_encrypt, enabled FROM xdat_user;'

    Parameters
    ----------
    psqlfile : str
        Name of the file containing the ``psql`` output.

    Returns
    -------
    iterable
        List of accounts. Each account is a dictionnary with the following keys:

        - login
        - firstname
        - lastname
        - email
        - password

    .. _Encrypt Stored Passwords: https://wiki.xnat.org/display/XNAT16/Encrypt+Stored+Passwords
    .. _ObfuscatedPasswordEncoder.java: http://hg.xnat.org/xdat_1_6dev/src/d788dd4e62d5852f14038968258454bf96c5484d/src/main/java/org/nrg/xdat/security/ObfuscatedPasswordEncoder.java
    .. _XOR cipher: http://en.wikipedia.org/wiki/XOR_cipher

    """
    accounts = []
    reader = csv.reader(psqlfile, delimiter='|', quoting=csv.QUOTE_NONE)
    for row in reader:
        login = row[0].strip()
        firstname = unescape(row[1].strip())
        lastname = unescape(row[2].strip())
        email = row[3].strip()
        primary_password = row[4].strip()
        primary_password_encrypt = row[5].strip()
        enabled = row[6].strip()
        if enabled != '0':
            if primary_password_encrypt != '0':
                plain_text = deobfuscate(primary_password)
            else:
                plain_text = primary_password
            account = {
                'login': login,
                'firstname': firstname,
                'lastname': lastname,
                'email': email,
                'password': plain_text,
            }
            accounts.append(account)
    return accounts


import ldap
import passlib.hash

def add_to_ldap(ldapobject, accounts):
    uid = 3000
    gid = 100  # group "users" by default
    for account in accounts:
        uid += 1
        BASE = 'dc=imagen,dc=cea,dc=fr'
        BASE = 'dc=example,dc=com'
        # add account to the restricted "partners" group
        dn = 'cn=partners,ou=Group,' + BASE
        attributes = [(ldap.MOD_ADD, 'memberUid', account['login'])]
        ldapobject.modify_s(dn, attributes)
        # create account
        login = account['login']
        firstname = account['firstname'].encode('utf-8')
        lastname = account['lastname'].upper().encode('utf-8')
        cn = firstname + ' ' + lastname
        dn = 'cn=%s,ou=People,' % cn + BASE
        email = account['email'].encode('utf-8')
        password = passlib.hash.ldap_md5.encrypt(account['password'])
        attributes = [
            ('objectClass', ('top', 'person', 'inetOrgPerson', 'posixAccount')),
            ('cn', (cn,)),
            ('givenName', (firstname,)),
            ('sn', (lastname,)),
            ('mail', (email,)),
            ('uid', (login,)),
            ('uidNumber', (str(uid),)),
            ('gidNumber', (str(gid),)),
            ('homeDirectory', ('/home/' + login,)),
            ('userPassword', (password,)),
            ('loginShell', ('/bin/false',)),
        ]
        ldapobject.add_s(dn, attributes)


def write_csv(accounts):
    columns = {}
    for account in accounts:
        for key, value in account.items():
            columns[key] = max(columns.get(key, 0), len(value))
    formatting = '%%(login)-%(login)ds | %%(firstname)-%(firstname)ds | %%(lastname)-%(lastname)ds | %%(email)-%(email)ds | %%(password)s' % columns
    for account in accounts:
        print formatting % account


import os
import sys
import codecs

if len(sys.argv) > 2:
    sys.exit('Usage: %s [PSQLDUMPFILE]' % os.path.basename(sys.argv[0]))
elif len(sys.argv) < 2:
    accounts = parse_psql_dump(sys.stdin)
elif not os.path.isfile(sys.argv[1]):
    sys.exit('File not found: %s' % sys.argv[1])
else:
    with open(sys.argv[1], 'rb') as psqlfile:
        accounts = parse_psql_dump(psqlfile)

host = 'ldap://127.0.0.1'
username = 'cn=admin,dc=example,dc=com'
password = 'XXXXXXXX'
ldapobject = ldap.initialize(host)
ldapobject.simple_bind_s(username, password)
add_to_ldap(ldapobject, accounts)
