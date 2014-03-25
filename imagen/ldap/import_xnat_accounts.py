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


import ldap
import passlib.hash
import logging
logger = logging.getLogger(__name__)


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
    uid = 3000  # attempt to avoid messing with existing accounts
    gid = 100  # group "users" by default

    # XNAT logins
    xnat_logins = set([x['login'] for x in accounts])

    # retrieve list of LDAP accounts
    people = ldapobject.search_s('ou=People,' + base, ldap.SCOPE_ONELEVEL)
    # retrieve members of LDAP group "partners"
    dn_partners = 'cn=partners,ou=Groups,' + base
    partners = ldapobject.search_s(dn_partners, ldap.SCOPE_BASE)[0][1]
    if 'memberUid' in partners:
        partners = partners['memberUid']
    else:
        partners = None

    # discard LDAP accounts missing from XNAT accounts
    for dn, entry in people:
        login = entry['uid'][0]
        logger.debug('Check LDAP account: ' + login.decode('utf-8'))
        if login.decode('utf-8') not in xnat_logins:
            logger.warn('Delete LDAP account: ' + login.decode('utf-8'))
            ldapobject.delete_s(dn)
            if login in partners:
                attributes = (ldap.MOD_DELETE,'memberUid',login)
                ldapobject.modify_s(dn_partners, (attributes,))
        elif login not in partners:
            logger.error('LDAP account missing from LDAP group "partners": '
                         + login.decode('utf-8'))
            attributes = (ldap.MOD_ADD, 'memberUid', login)
            ldapobject.modify_s(dn_partners, (attributes,))

    # sync LDAP accounts with XNAT accounts
    for account in accounts:
        login = account['login'].encode('utf-8')
        logger.debug('Process XNAT account: ' + login.decode('utf-8'))
        uid += 1
        # add account to the restricted "partners" group
        if partners and login in partners:
            logger.debug('Account already in "partners": ' + login.decode('utf-8'))
        else:
            logger.info('Account will be added to "partners": ' + login.decode('utf-8'))
            attributes = (ldap.MOD_ADD, 'memberUid', login)
            ldapobject.modify_s(dn_groups, (attributes,))
        # create or update LDAP account
        if login in [entry['uid'][0] for dn, entry in people]:
            logger.debug('XNAT account already in LDAP: ' + login.decode('utf-8'))
        else:
            logger.info('Account will be added to LDAP: ' + login.decode('utf-8'))
            firstname = account['firstname'].encode('utf-8')
            lastname = account['lastname'].upper().encode('utf-8')
            cn = firstname + ' ' + lastname
            dn = 'cn=%s,ou=People,' % cn + base

            if dn in [dn for dn, entry in people]:
                logger.error('XNAT account already in LDAP: ' + cn.decode('utf-8'))


            email = account['email'].encode('utf-8')
            password = passlib.hash.ldap_md5.encrypt(account['password']).encode('utf-8')
            attributes = (
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
            )
            ldapobject.add_s(dn, attributes)


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
