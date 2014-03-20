#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

obfuscated = raw_input('obfuscated password: ')
obfuscated = obfuscated.decode(sys.stdin.encoding)

g = 2
password = ''.join([unichr(g ^ ord(x)) for x in obfuscated])
print password.encode(sys.stdout.encoding)
