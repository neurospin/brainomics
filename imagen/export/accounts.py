#!/usr/bin/python
# -*- coding: utf-8 -*-

csvfile = 'PASSWORD'

import csv
import re

def _html_entity_decode(matchobj):
    return unichr(int(matchobj.group(1)))

def unescape(s):
    return re.sub(r'&#(\d+);', _html_entity_decode, s)

def deobfuscate(password):
    g = 2
    plain_text = ''.join([unichr(g ^ ord(x)) for x in password])
    return plain_text

accounts = []
with open(csvfile, 'r') as f:
    reader = csv.reader(f, delimiter='|', quoting=csv.QUOTE_NONE)
    for row in reader:
        login = row[0].strip()
        firstname = unescape(unicode(row[1].strip(), 'utf-8'))
        lastname = unescape(unicode(row[2].strip(), 'utf-8'))
        email = row[3].strip()
        primary_password = unicode(row[4].strip(), 'utf-8')
        primary_password_encrypt = row[5].strip()
        enabled = row[6].strip()
        if primary_password_encrypt == '0':
            plain_text = primary_password
        else:
            plain_text = deobfuscate(primary_password)
        if enabled != '0':
            accounts.append((login, firstname, lastname, email, plain_text))

columns = [max(len(x) for x in column) for column in zip(*accounts)]
formatting = '%%-%ds | %%-%ds | %%-%ds | %%-%ds | %%s' % tuple(columns[:4])
for account in accounts:
    print formatting % account
