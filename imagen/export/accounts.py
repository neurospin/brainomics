#!/usr/bin/python
# -*- coding: utf-8 -*-

csvfile = 'PASSWORD'

import csv
import re


def _html_entity_decode(matchobj):
    return unichr(int(matchobj.group(1)))


def unescape(s):
    """Converts HTML numeric character references to their applicable
    characters.

    A `numeric character reference`_ look like &#931; and is converted
    to its applicable code point of the Universal Character Set - in
    this case Σ.

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
    with open(psqlfile, 'rb') as f:
        reader = csv.reader(f, delimiter='|', quoting=csv.QUOTE_NONE)
        for row in reader:
            login = row[0].strip()
            firstname = unescape(unicode(row[1].strip(), 'utf-8'))
            lastname = unescape(unicode(row[2].strip(), 'utf-8'))
            email = row[3].strip()
            primary_password = unicode(row[4].strip(), 'utf-8')
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


import hashlib
import base64

def _digest_md5_password(password):
    return base64.b64encode(hashlib.md5(password).digest())


def write_ldif(accounts):
    uid = 2001
    m = hashlib.md5()
    for account in accounts:
        cn = account['firstname'] + ' ' + account['lastname']
        password = account['password']
        password = base64.b64encode(hashlib.sha1(password).digest())

        print 'dn: cn=%s,ou=People,dc=imagen,dc=cea,dc=fr' % cn
        print 'objectClass: top'
        print 'objectClass: inetOrgPerson'
        print 'objectClass: posixAccount'
        print 'cn: %s' % cn
        print 'sn: %s' % account['lastname']
        print 'givenName: %s' % account['firstname']
        print 'mail: %s' % account['email']
        print 'uid: %s' % account['login']
        print 'uidNumber: %d' % uid
        print 'gidNumber: %d' % uid
        print 'homeDirectory: /home/%s' % account['login']
        print 'userPassword: {MD5}%s' % _digest_md5_password(account['password'])
        print 'loginShell: /bin/false'
        print
        uid += 1


def write_csv(accounts):
    columns = {}
    for account in accounts:
        for key, value in account.items():
            columns[key] = max(columns.get(key, 0), len(value))
    formatting = '%%(login)-%(login)ds | %%(firstname)-%(firstname)ds | %%(lastname)-%(lastname)ds | %%(email)-%(email)ds | %%(password)s' % columns
    for account in accounts:
        print formatting % account


import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

accounts = parse_psql_dump(csvfile)
write_csv(accounts)
