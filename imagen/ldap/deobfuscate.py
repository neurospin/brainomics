#!/usr/bin/python
# -*- coding: utf-8 -*-

password = raw_input('obfuscated password: ')
g =2
print ''.join([unichr(g ^ ord(x)) for x in password])
