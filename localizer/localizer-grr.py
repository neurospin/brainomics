#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Print patient NIP, inclusion date and inclusion ID for all
# inclusions in the GRR database.
#

import MySQLdb

database = MySQLdb.connect(host = 'mysql.lixium.fr',
                           port=3306,
                           user = 'XXXXX',
                           passwd = 'XXXXXXXX',
                           db = 'ifr49',
                           charset = 'latin1')
                           
cursor = database.cursor()
cursor.execute('SELECT grr_add_vol.nip,grr_add_inclusion.date,grr_add_inclusion.ref_aq FROM grr_add_inclusion LEFT JOIN grr_add_vol ON grr_add_inclusion.id_vol = grr_add_vol.id_vol;')
row = cursor.fetchone()
while row is not None:
	nip    = row[0]
	date   = row[1]
	ref_aq = row[2]
	print nip, date, ref_aq
	row = cursor.fetchone()
cursor.close()

database.close()
