#!/usr/bin/python
# -*- coding: utf-8 -*-

BASE = 'dc=imagen2,dc=cea,dc=fr'

SKIP_LOGIN = set((
    'sesyn', 's8huth',
    'Kmueller', 'Mueller',
    'admin',
    'Imagen',
))

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
    reader = csv.reader(psqlfile,
                        delimiter='|', quoting=csv.QUOTE_NONE)
    for row in reader:
        if not row:  # skip empty lines
            continue
        # decode UTF-8 back to Unicode, cell by cell
        row = [unicode(cell, 'utf-8') for cell in row]
        login = row[0].strip()
        firstname = unescape(row[1].strip())
        lastname = unescape(row[2].strip())
        email = row[3].strip()
        primary_password = row[4].strip()
        primary_password_encrypt = row[5].strip()
        enabled = row[6].strip()
        if enabled != '0' and login not in SKIP_LOGIN:
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


def find_existing_uid_dn(people, uid, dn):
    uid_exists = False
    dn_exists = False
    for d, e in people:
        if e['uid'][0] == uid:
            uid_exists = True
            dn_exists = True
            break
        if d == dn:
            dn_exists = True
    return uid_exists, dn_exists


import ldap
import passlib.hash
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def sync_ldap(ldapobject, base, accounts):
    """Sync LDAP with accounts.

    Parameters
    ----------
    ldapobject : LDAPObject_
        A find operation must have already been performed on this object.

    base: str
        DN entry to use as root for all operations.

    accounts: iterable
        Each element in accounts should be a dictionary.

    .. _LDAPObject: http://www.python-ldap.org/doc/html/ldap.html#ldapobject-classes

    """
    UID_NUMBER = 3000  # avoid messing with UID numbers < 3000
    GID_NUMBER = 999   # group 'partners' by default

    # XNAT logins
    xnat_logins = set([x['login'] for x in accounts])

    # retrieve list of LDAP accounts
    people = ldapobject.search_s('ou=People,' + base, ldap.SCOPE_ONELEVEL)

    # find existing UID numbers
    uid_numbers = set()
    for dn, entry in people:
        uid_number = entry['uidNumber'][0]
        uid_numbers.add(uid_number)

    # discard LDAP accounts missing a matching XNAT account
    for dn, entry in people:
        login = entry['uid'][0]
        logger.debug('Check LDAP account: ' + login.decode('utf-8'))
        if login.decode('utf-8') not in xnat_logins:
            logger.warn('Delete LDAP account: ' + login.decode('utf-8'))
            ldapobject.delete_s(dn)

    # sync LDAP accounts with XNAT accounts
    for account in accounts:
        x_login = account['login'].encode('utf-8')
        logger.debug('Process XNAT account: ' + x_login.decode('utf-8'))
        x_firstname = account['firstname'].encode('utf-8')
        x_lastname = account['lastname'].upper().encode('utf-8')
        x_cn = x_firstname + ' ' + x_lastname
        x_dn = 'cn=%s,ou=People,' % x_cn + base
        x_email = account['email'].encode('utf-8')
        x_password = passlib.hash.ldap_md5.encrypt(account['password']).encode('utf-8')
        # is there an account with identical 'x_uid' or 'x_dn' in LDAP?
        uid_exists, dn_exists = find_existing_uid_dn(people, x_login, x_dn)
        # modify existing or create new LDAP account
        if uid_exists:
            logger.info('Modifying account: ' + x_login.decode('utf-8'))
            attributes = (
                # would require modrdn_s() instead
                # (ldap.MOD_REPLACE, 'cn', (x_cn,)),
                (ldap.MOD_REPLACE, 'givenName', (x_firstname,)),
                (ldap.MOD_REPLACE, 'sn', (x_lastname,)),
                (ldap.MOD_REPLACE, 'mail', (x_email,)),
                (ldap.MOD_REPLACE, 'gidNumber', (str(GID_NUMBER),)),
                (ldap.MOD_REPLACE, 'homeDirectory', ('/home/' + x_login,)),
                (ldap.MOD_REPLACE, 'userPassword', (x_password,)),
                (ldap.MOD_REPLACE, 'loginShell', ('/bin/false',)),
            )
            ldapobject.modify_s(x_dn, attributes)
        else:
            # delete existing account with identical 'dn' but different 'uid'
            if dn_exists:
                logger.error('Account already in LDAP: ' + x_dn.decode('utf-8'))
                logger.info('Deleting account: ' + x_dn.decode('utf-8'))
                ldapobject.delete_s(x_dn)
            # find a free UID number above UID_NUMBER
            uid_number = UID_NUMBER
            while uid_number in uid_numbers:
                uid_number += 1
            uid_numbers.add(uid_number)
            # create new account
            logger.info('Adding account: ' + x_login.decode('utf-8'))
            attributes = (
                ('objectClass', ('top', 'person', 'inetOrgPerson', 'posixAccount')),
                ('cn', (x_cn,)),
                ('givenName', (x_firstname,)),
                ('sn', (x_lastname,)),
                ('mail', (x_email,)),
                ('uid', (x_login,)),
                ('uidNumber', (str(uid_number),)),
                ('gidNumber', (str(GID_NUMBER),)),
                ('homeDirectory', ('/home/' + x_login,)),
                ('userPassword', (x_password,)),
                ('loginShell', ('/bin/false',)),
            )
            ldapobject.add_s(x_dn, attributes)


def write_csv(accounts):
    """Dump accounts to stdout.

    Parameters
    ----------
    accounts: iterable
        Each element in accounts should be a dictionary.

    """
    columns = {}
    for account in accounts:
        for key, value in account.items():
            columns[key] = max(columns.get(key, 0), len(value))
    formatting = u'%%(login)-%(login)ds | %%(firstname)-%(firstname)ds | %%(lastname)-%(lastname)ds | %%(email)-%(email)ds | %%(password)s' % columns
    for account in accounts:
        account = formatting % account
        print account.encode('utf-8')  # force UTF-8 for piping


import os
import sys
import getpass
import getopt

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   'f:l:d',
                                   ['file=', 'ldap=', 'dump'])
    except getopt.GetoptError as err:
        print >> sys.stderr, str(err)
        sys.exit(2)
    psqlfile = None
    ldaphost = None
    dump = None
    for o, a in opts:
        if o in ('-f', "--file"):
            psqlfile = a
        elif o in ("-l", "--ldap"):
            ldaphost = a
        elif o in ("-d", "--dump"):
            dump = True
        else:
            assert False, "unhandled option"

    accounts = None
    if psqlfile:
        with open(psqlfile, 'rb') as f:
            accounts = parse_psql_dump(f)
    else:  # read from stdin
        accounts = parse_psql_dump(sys.stdin)

    if dump:
        write_csv(accounts)
    if ldaphost:
        username = 'cn=admin,' + BASE
        ldapobject = ldap.initialize(ldaphost)
        while True:
            password = getpass.getpass(prompt='LDAP administrator password? ')
            try:
                ldapobject.simple_bind_s(username, password)
            except ldap.INVALID_CREDENTIALS:
                continue
            else:
                break
        sync_ldap(ldapobject, BASE, accounts)
        ldapobject.unbind_s()
