#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import struct
import pprint
import loadObjectFile

pp = pprint.PrettyPrinter(depth=6)

def chunks(a,n):
	return [a[i:i + n] for i in range(0, len(a), n)]

def getString(data,offset):
	s = ''
	while offset < len(data):
		ch = data[offset]
		offset += 1
		if ch == 0x9B: # Atari EOL
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
		elif (ch & 0xF0) == 0x80:
			ch = '<SUSPECT CALLS %s>' % SUSPECTS[ch & 0xF]
		elif (ch & 0xF0) == 0x90:
			pidx = (ch & 0xF) * 2
			ch = '<PRONOUN %s/%s>' % (PRONOUNS[pidx],PRONOUNS[pidx+1])
		elif (ch & 0xF0) == 0xA0:
			ch = '<PERSON %s>' % SUSPECTS[ch & 0xF]
		elif (ch & 0xF0) == 0xB0:
			ch = '<PERSON %s>' % SUSPECTS[ch & 0xF]
		elif (ch & 0xF0) == 0xC0:
			ch = '<VERB %s/%s>' % (VERBS[ch & 0xF],VERBS[(ch & 0xF)+1])
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
		elif ch >= 0x80: # unknown codes
			ch = '<$%02x>' % ch
		else:
			ch = chr(ch)
		s += ch
	return s

def parseLSB_MSB_Text(data,baseAdr,size,lsbOffset,msbOffset):
	lsbs = data[lsbOffset:lsbOffset+size]
	msbs = data[msbOffset:msbOffset+size]
	idx = 0
	words = []
	for lsb,msb in zip(lsbs,msbs):
		offset = (msb << 8) + lsb
		s = getString(data,offset - baseAdr)
		#print('#%2d $%04x "%s"' % (idx, offset, s))
		idx += 1
		words.append(s)
	return words

def parseLSB_Text(data,baseAdr,size,lsbOffset,msb):
	lsbs = data[lsbOffset:lsbOffset+size]
	idx = 0
	words = []
	for lsb in lsbs:
		offset = (msb << 8) + lsb
		s = getString(data,offset - baseAdr)
		#print('#%2d $%04x "%s"' % (idx, offset, s))
		idx += 1
		words.append(s)
	return words

gamecode = bytearray(0x6DE) + bytearray(open('Murder on the Zinderneuf (1983)[a].atx.atboot','rb').read())

# these need to be parsed first, because getString() might require them
PRONOUNS = parseLSB_Text(gamecode,0,32,0x2e13,0x2e)
VERBS = parseLSB_Text(gamecode,0,32,0x2e8c,0x2f)
SUSPECTS = []
suspect_firstname = parseLSB_Text(gamecode,0,17,0x1EB8,0x1F)
suspect_lastname = parseLSB_Text(gamecode,0,17,0x1EC9,0x1F)
for first,last in zip(suspect_firstname,suspect_lastname):
	SUSPECTS.append('%s %s' % (first,last))
pp.pprint(SUSPECTS)

room = getString(gamecode,0x1dad) # 'Room '
rooms = parseLSB_Text(gamecode,0,19,0x1D63,0x1D) # The room names
ROOMNAMES = []
for idx in range(len(rooms)):
	if idx == 0 or idx >= 17:
		name = rooms[idx]
	else: # the room numbers have a guest assigned to them
		name = '%s%s: %s' % (room, rooms[idx], SUSPECTS[idx])
	ROOMNAMES.append(name)
pp.pprint(ROOMNAMES)

# Sentence start based on which person the detective talks to
sentence_start = parseLSB_Text(gamecode,0,16,0x2412,0x24)
#print(sentence_start)
# Sentence end based on which person the detective talks to
sentence_end = parseLSB_Text(gamecode,0,16,0x24F1,0x25)
#print(sentence_end)

knows_nothing = parseLSB_Text(gamecode,0,16,0x2817,0x27)
#print(knows_nothing)

# if the person is ask about themselves as the suspect
words = parseLSB_MSB_Text(gamecode, 0, 16, 0x29d3, 0x29e3)
#print(words)

# if the mood table has a zero entry, the person does not answer the above question, but replies like this
words = parseLSB_MSB_Text(gamecode, 0, 16, 0x2827, 0x2837)
#print(words)

# person has no more answers about the suspect
words = parseLSB_MSB_Text(gamecode, 0, 16, 0x2bc2, 0x2bd2)
#print(words)

DIR = './Gamefiles/'
for filename in sorted(os.listdir(DIR)):
	if not filename.endswith('.OBJ'):
		continue
	ret = loadObjectFile.loadObj(DIR + filename)
	if not ret:
		continue
	# scene files are loaded to $4800
	loadAdr = list(ret.keys())[0]
	SCENE_ADR = 0x4800
	if loadAdr != SCENE_ADR:
		continue
	scene = ret[loadAdr]
	print(filename[:-4])
	print('=' * (len(filename)-4))
	if True:
		pp.pprint(chunks(parseLSB_MSB_Text(scene, SCENE_ADR, 48, 0x0030, 0x0000),8))
		print()
		pp.pprint(chunks(parseLSB_MSB_Text(scene, SCENE_ADR, 24, 0x0078, 0x0060),8))
		print()
		print('Clues:')
		pp.pprint(parseLSB_MSB_Text(scene, SCENE_ADR, 8, 0x0188, 0x0190))
		print()
		print('Confession:')
		pp.pprint(parseLSB_MSB_Text(scene, SCENE_ADR, 8, 0x01B8, 0x01C0))
		print()

	msbA = list(scene[0x090:0x090+48])
	lsbA = list(scene[0x0C0:0x0C0+48])
	bits = []
	for m,l in zip(msbA,lsbA):
		bits.append('%04x' % ((m << 8) + l))
	print(bits)
	masks = list(scene[0x0F0:0x0F0+3*8])
	bits = []
	for idx in range(8):
		bits.append('%02x%02x%02x' % (masks[idx*3+0],masks[idx*3+1],masks[idx*3+2]))
	print(bits)

	hints = []
	for idx in range(8):
		hints.append(list(scene[0x168+4*idx:0x168+4*(idx+1)]))
	pp.pprint(hints)

	shuffle = list(scene[0x108:0x108+8])
	for i in range(8):
		cs = shuffle[i]
		if cs == 0:
			cs = 'r'
		else:
			j = 0
			while cs != 0:
				j += 1
				cs >>= 1
			cs = j
		print('#%d %s: %s' % (i,cs,list(scene[0x120+4*i:0x120+4*(i+1)])))

	al = list(scene[0x140:0x140+16])
	bl = list(scene[0x150:0x150+16])
	cl = list(scene[0x160:0x160+8])
	pp.pprint(al)
	pp.pprint(bl)
	pp.pprint(cl)
	print()
	break
