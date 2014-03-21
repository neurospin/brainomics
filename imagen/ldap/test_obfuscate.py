#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

password = raw_input('password: ')
password = password.decode(sys.stdin.encoding)

prime = 273  # seems completely useless since x < 256
g = 2
obfuscated = u''.join([unichr(g ^ (ord(x) % 273)) for x in password])
print obfuscated.encode(sys.stdout.encoding)
