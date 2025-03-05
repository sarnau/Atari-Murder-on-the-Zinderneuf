#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import os

def dump_memory_block(data,start_data=0,size=0):
	if not size:
		size = len(data)
	LINE_LENGTH = 16
	for l in range(0,size,LINE_LENGTH):
		if True:
			print('%04x: ' % (start_data+l),end='')
		for p in range(0,LINE_LENGTH):
			offs = l + p
			if offs < len(data):
				print('%02x ' % data[offs],end='')
			else:
				print('   ',end='')
		if True:
			print(' ',end='')
			for p in range(0,LINE_LENGTH):
				offs = l + p
				if offs < len(data):
					c = data[l + p]
					if c < 0x20 or c >= 0x7F:
						c = ord('.')
					print('%c' % c,end='')
				else:
					print(' ',end='')
		print('')

GAME_FILES = './Gamefiles/'
if not os.path.exists(GAME_FILES):
    os.makedirs(GAME_FILES)

data = bytearray(open(GAME_FILES+'ASMMAP.OBJ','rb').read())
#dump_memory_block(data)

offset = 0
if data[offset] == 0xFF and data[offset+1] == 0xFF:
	offset += 2
startAdr = 0
endAdr = 0
buffer = None
while offset < len(data):
	sadr = data[offset+0] + (data[offset+1]<<8)
	eadr = data[offset+2] + (data[offset+3]<<8)
	#print("$%04x-$%04x" % (sadr,eadr))
	offset += 4
	blockLen = eadr - sadr + 1
	if sadr != endAdr + 1:
		if buffer:
			dump_memory_block(buffer,startAdr)
			print('=' * 71)
		buffer = bytearray()
		startAdr = sadr
	endAdr = eadr
	buffer += data[offset:offset+blockLen]
	offset += blockLen

dump_memory_block(buffer,startAdr)
