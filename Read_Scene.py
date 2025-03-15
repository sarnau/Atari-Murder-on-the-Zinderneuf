#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import struct
import loadObjectFile

SUSPECTS = [
	'Veronica Marlowe',
	'Francis "Buck" Battle',
	'Margaret Vandergilt',
	'Vincent van Wente',
	'Felicity Sucrose',
	'Rod London',
	'Sally Rose',
	'Oswald Stonemann',
	'Natalia Berenski',
	'Reverend Jeremiah Folmuth',
	'Stephie Hart-Winston',
	'Aldo Sandini',
	'Marie Roget',
	'Anton Peste',
	'Hester Prymme',
	'Phillip Wollcraft'
]

def getString(data,offset):
	s = ''
	while offset < len(data):
		ch = data[offset]
		offset += 1
		if ch == 0x22:
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
		elif ch >= 0x80 and ch <= 0x8F:
			ch = '<SUSPECT CALLS %s>' % SUSPECTS[ch & 0xF]
		elif ch == 0x90:
			ch = '<PRONOUN She/He>'
		elif ch == 0x91:
			ch = '<PRONOUN HER/HIS>'
		elif ch == 0x92:
			ch = '<PRONOUN her/him>'
		elif ch == 0x93:
			ch = '<PRONOUN she/he>'
		elif ch == 0x94:
			ch = '<PRONOUN her/his>'
		elif ch == 0x95:
			ch = '<PRONOUN husband/wife>'
		elif ch == 0x96:
			ch = '<PRONOUN Woman/man>'
		elif ch == 0x97:
			ch = '<PRONOUN Men/Women>'
		elif ch == 0x98:
			ch = '<PRONOUN He/She>'
		elif ch == 0x99:
			ch = '<PRONOUN he/she>'
		elif ch == 0x9A:
			ch = '<PRONOUN girl/fellow>'
		elif ch == 0x9B: # Atari EOL
			break
		elif ch == 0x9C:
			ch = '<PRONOUN man/woman>'
		elif ch == 0x9D:
			ch = '<PRONOUN him/her>'
		elif ch == 0x9E:
			ch = '<PRONOUN his/him>'
		elif ch == 0x9F:
			ch = '<PRONOUN Miss/Mr>'
		elif ch >= 0xA0 and ch <= 0xAF:
			ch = '<PERSON %s>' % SUSPECTS[ch & 0xF]
		elif ch >= 0xB0 and ch <= 0xBF:
			ch = '<PERSON %s>' % SUSPECTS[ch & 0xF]
		elif ch == 0xC0:
			ch = '<VERB is/was>'
		elif ch == 0xC1:
			ch = '<VERB s/d>'
		elif ch == 0xC2:
			ch = '<VERB s/ed>'
		elif ch == 0xC3:
			ch = '<VERB keeps/kept>'
		elif ch == 0xC4:
			ch = '<VERB \'s/was>'
		elif ch == 0xC5:
			ch = '<VERB oss/id>'
		elif ch == 0xC6:
			ch = '<VERB inks/ank>'
		elif ch == 0xC7:
			ch = '<VERB are/were>'
		elif ch == 0xC8:
			ch = '<VERB be/have been>'
		elif ch == 0xC9:
			ch = '<VERB can/could>'
		elif ch == 0xCA:
			ch = '<VERB s/>'
		elif ch == 0xCB:
			ch = '<VERB makes/made>'
		elif ch == 0xCC:
			ch = '<VERB gives/gave>'
		elif ch == 0xCD:
			ch = '<VERB will/would>'
		elif ch == 0xCE:
			ch = '<VERB have/had>'
		elif ch == 0xCF:
			ch = '<VERB have/had>'
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

def parseLSB_MSB_Text(data,baseAdr,size,lsbOffset,msbOffset):
	lsbs = data[lsbOffset:lsbOffset+size]
	msbs = data[msbOffset:msbOffset+size]
	idx = 0
	for lsb,msb in zip(lsbs,msbs):
		offset = (msb << 8) + lsb
		print('#%2d $%04x "%s"' % (idx, offset, getString(data,offset - baseAdr)))
		idx += 1

DIR = './Gamefiles/'
for filename in sorted(os.listdir(DIR)):
	if not filename.endswith('.OBJ'):
		continue
	ret = loadObjectFile.loadObj(DIR + filename)
	if not ret:
		continue
	# scene files are loaded to $4800
	loadAdr = list(ret.keys())[0]
	if loadAdr != 0x4800:
		continue
	scene = ret[loadAdr]
	print(filename[:-4])
	print('=' * (len(filename)-4))
	parseLSB_MSB_Text(scene, 0x4800, 48, 0x0030, 0x0000)
	print()
	parseLSB_MSB_Text(scene, 0x4800, 24, 0x0078, 0x0060)
	print()
	print('Clues:')
	parseLSB_MSB_Text(scene, 0x4800, 8, 0x0188, 0x0190)
	print()
	print('Confession:')
	parseLSB_MSB_Text(scene, 0x4800, 8, 0x01B8, 0x01C0)
	break
