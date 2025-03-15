#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import struct
import loadObjectFile

def getString(data,offset):
	s = ''
	while offset < len(data):
		ch = data[offset]
		offset += 1
		if ch == 0x9B: # EOL
			break
		elif ch == 0x22:
			ch = '“'
		elif ch == 0x3B:
			ch = '”'
		elif ch == 0x3C:
			ch = 'b'
		elif ch == 0x3D:
			ch = 'f'
		elif ch == 0x3E:
			ch = 'k'
		elif ch == 0x40:
			ch = 'i'
		elif ch == 0x5B:
			ch = 'l'
		elif ch == 0x5C:
			ch = 't'
		elif ch == 0x5D:
			ch = 'h'
		elif ch == 0x5E:
			ch = 'd'
		elif ch == 0x60:
			ch = ','
		elif ch == 0xD0:
			ch = '<DETECTIVE SIR/MISS>'
		elif ch == 0xD1:
			ch = '<VICTIM FIRST/LASTNAME>'
		elif ch == 0xD2:
			ch = '<WORD SENTENCE START>'
		elif ch == 0xD3:
			ch = '<WORD SENTENCE END>'
		elif ch == 0xD4:
			ch = '<DETECTIVE>'
		elif ch >= 0x80:
			ch = '<$%02x>' % ch
		else:
			ch = chr(ch)
		s += ch
	return s

DIR = './Gamefiles/'
for filename in sorted(os.listdir(DIR)):
	if not filename.endswith('.OBJ'):
		continue
	ret = loadObjectFile.loadObj(DIR + filename)
	if not ret:
		continue
	# the cluelist is loaded to $7800
	loadAdr = list(ret.keys())[0]
	if loadAdr != 0x7800:
		continue
	cluelist = ret[loadAdr]
	print(filename[:-4])
	print('=' * (len(filename)-4))
	msbs = cluelist[:96]
	lsbs = cluelist[96:96+96]
	idx = 0
	for lsb,msb in zip(lsbs,msbs):
		offset = (msb << 8) + lsb
		print('#%2d $%04x "%s"' % (idx, offset, getString(cluelist,offset - 0x7800)))
		idx += 1
