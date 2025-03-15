#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import struct
import loadObjectFile

PIXEL_SET = '█︎'
PIXEL_CLEAR = ' '

def drawFont(data,addr,firstChar,lastChar):
	width = 16
	lineLen = 4
	gap = 0
	chheight = 16
	for cindex in range(firstChar,lastChar+1,lineLen):
		s = ''
		for o in range(0,lineLen):
			if o + cindex <= lastChar:
				st = '$%04x:%02x' % (addr+o*chheight+cindex*lineLen,cindex + o)
				s += (st + ' ' * 30)[:width+gap] + ' '
		print(s)
		for row in range(0,chheight):
			s = ''
			for o in range(0,lineLen):
				if o + cindex <= lastChar:
					bstr = '{:08b}'.format(data[addr + (chheight * (cindex + o)) + row])
					st = bstr.replace('1',PIXEL_SET*2).replace('0',PIXEL_CLEAR*2)
					s += st + ' ' + ' ' * gap
			print(s)
	print()

def getString(data,offset):
	s = ''
	while offset < len(data):
		ch = data[offset]
		offset += 1
		if ch == 0x9B: # EOL
			break
		if ch == 0x3C:
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
			ch = '.'
		elif ch == 0xD0:
			ch = '<DETECTIVE SIR/MISS>'
		elif ch == 0xD1:
			ch = '<VICTIM FIRST/LASTNAME>'
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
	# detective files are loaded to $7000
	loadAdr = list(ret.keys())[0]
	if loadAdr != 0x7000:
		continue
	detective = ret[loadAdr]
	print(filename[:-4])
	print('=' * (len(filename)-4))
	detID,detColor,detSex, detSearch,detInterrogMoodAdr,detFirstNameAdr,detLastNameAdr,detTitle,detWrongConfessionAdr,detStartAdr = struct.unpack('4B6H', detective[:4*1+6*2])
	detInterrogMoodAdr -= loadAdr
	detFirstNameAdr -= loadAdr
	detLastNameAdr -= loadAdr
	detTitle -= loadAdr
	detWrongConfessionAdr -= loadAdr
	detStartAdr -= loadAdr
	if detSex == 0:
		detSex = 'MALE'
	elif detSex == 1:
		detSex = 'FEMALE'
	detectiveFullName = ' '.join((	getString(detective,detTitle),getString(detective,detFirstNameAdr),getString(detective,detLastNameAdr))).strip()
	print('ID          #%d : %s (%s)' % (detID,detectiveFullName,detSex))
	print('COLOR       $%02x' % detColor)
	print('SEARCH      %d' % detSearch)
	print('START       %s' % getString(detective,detStartAdr))
	print('FAIL        %s' % getString(detective,detWrongConfessionAdr))
	moodCount = detective[detInterrogMoodAdr]
	moods = []
	for mood in range(moodCount):
		offs = detInterrogMoodAdr+1
		while mood > 0:
			if detective[offs] == 0x9B:
				mood -= 1
			offs += 1
		moods.append(getString(detective,offs))
	print('MOODS       %s' % ','.join(moods))
	personFlags = []
	for flag in struct.unpack('15B', detective[0x10:0x1F]):
		if flag:
			personFlags.append('L')
		else:
			personFlags.append('F')
	print('PERSONFLAGS %s' % ''.join(personFlags[:moodCount]))
	print('QUESTION BASED ON MOOD:')
	for mood in range(moodCount):
		interrog  = []
		for val in detective[0x1F+mood*16:0x1F+16+mood*16]:
			interrog.append(val)
		print(interrog)

	if False:
		print('PM Graphics:')
		drawFont(detective[0x77:0x177],0x00,0x00,0x0F)
	print()	
