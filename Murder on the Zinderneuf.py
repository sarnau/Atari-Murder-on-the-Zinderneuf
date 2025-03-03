#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict, namedtuple
import random
import sys
import struct
import os
from datetime import datetime, timedelta

SECTOR_SIZE = 128

def dump_memory_block(data,start_data=0,size=SECTOR_SIZE):
	LINE_LENGTH = 16
	for l in range(0,size,LINE_LENGTH):
		if True:
			print('%04x: ' % (start_data+l),end='')
		for p in range(0,LINE_LENGTH):
			offs = start_data + l + p
			if offs < len(data):
				print('%02x ' % data[offs],end='')
			else:
				print('   ',end='')
		if True:
			print(' ',end='')
			for p in range(0,LINE_LENGTH):
				offs = start_data + l + p
				if offs < len(data):
					c = data[start_data + l + p]
					if c < 0x20 or c >= 0x7F:
						c = ord('.')
					print('%c' % c,end='')
				else:
					print(' ',end='')
		print('')

def atx_readSector(atxData, sectorNo, sectorIndex):
	offset = 0

	onTrack = (sectorNo - 1) // 18
	onSector = sectorNo - onTrack * 18

	# read file header
	header,version_number,fh_size = struct.unpack('<4sh22xl16x', atxData[offset+0:offset+0x30])
	if header != b'AT8X':
		print('File Header AT8X not found')
		return
	if fh_size != 48:
		print('File Header Size != 48 bytes')
		return
	if version_number != 1:
		print('File Header Version != 1')
		return
	offset += fh_size

	while offset < len(atxData):
		# read track header
		th_record_size,record_type,track_number,sector_count,th_size = struct.unpack('<lh2xB1xh8xl8x', atxData[offset+0:offset+0x20])
		if th_size != 32:
			print('Track Header Size != 32 bytes')
			return False
		if record_type != 0:
			print('Track Header record type != data track')
			return False
		if track_number == onTrack:
			track = atxData[offset+0:offset+th_record_size]
			# read sector list header
			record_size,record_type = struct.unpack('<lB3x', track[th_size+0:th_size+8])
			if record_type != 1:
				print('Sector List Header record type != sector list')
				return False

			# read sector list
			sectors = []
			for sectorHeaderOffset in range(th_size+8,th_size+record_size,8):
				sector_number,sector_status,sector_position,start_data = struct.unpack('<BBhl', track[sectorHeaderOffset+0:sectorHeaderOffset+8])
				if sector_number == onSector:
					sectors.append((track[start_data:start_data+SECTOR_SIZE],sector_status))
			
			if len(sectors):
				return sectors[sectorIndex % len(sectors)]

		# proceed to the next track
		offset += th_record_size

	return [0] * SECTOR_SIZE,0x80

def readSector(sectorNo, sectorIndex):
	data,status = atx_readSector(atxDiskImage, sectorNo, sectorIndex)
	if True:
		if status != 0x00:
			print('$$$ STATUS = $%02x' % status)
		#dump_memory_block(data)
	return data,status


GAME_FILES = './Gamefiles/'
if not os.path.exists(GAME_FILES):
    os.makedirs(GAME_FILES)

atxDiskImage = bytearray(open('Murder on the Zinderneuf (1983)[a].atx','rb').read())
VTOCdata,status = atx_readSector(atxDiskImage, 360, 0)
dump_memory_block(VTOCdata)

dosCode,availSectors,unusedSectors = struct.unpack('<BHH5x', VTOCdata[0:10])
print('DOS code:          %d' % dosCode)
print('available sectors: #%d' % availSectors)
print('unused sectors:    #%d' % unusedSectors)

# print allocation bitmap
lastUsed = 0
startBit = 1
for sbit in range(1,720):
	used = (VTOCdata[10+sbit//8] >> (7-sbit%8)) != 0
	if used == lastUsed:
		continue
	if not lastUsed:
		print('+ %d-%d' % (startBit,sbit-1))
	else:
		print('. %d-%d' % (startBit,sbit-1))
	lastUsed = used
	startBit = sbit
if not lastUsed:
	print('+ %d-%d' % (startBit,719))
else:
	print('. %d-%d' % (startBit,719))

DIRdata = bytearray()
for dirSector in range(361,361+8):
	dd,status = atx_readSector(atxDiskImage, dirSector, 0)
	DIRdata += dd
#dump_memory_block(DIRdata,0,len(DIRdata))

if True:
	for dirEntryIndex in range(0,len(DIRdata)//16):
		flag,sectorCount,startSector,filename,ext = struct.unpack('<BHH8s3s',DIRdata[dirEntryIndex*16:(dirEntryIndex+1)*16])
		if sectorCount == 0:
			continue
		filename = filename.decode('ASCII').rstrip() + '.' + ext.decode('ASCII').rstrip()
		print('#%2d Flag:$%02x Len:%3d Start:%3d %s' % (dirEntryIndex,flag,sectorCount,startSector,filename))
		nextSector = startSector
		fileData = bytearray()
		while sectorCount > 0 and nextSector != 0:
			data,status = atx_readSector(atxDiskImage, nextSector, 0)
			fileDirIndex = data[125] >> 2
			assert fileDirIndex == dirEntryIndex
			nextSector = ((data[125] & 3) << 8) | data[126]
			sectorLen = data[127]
			#print('- #%2d - Next:#%3d - Len:%3d' % (fileDirIndex,nextSector,sectorLen))
			fileData += data[:sectorLen]
			sectorCount -= 1
		print('File length: #%d' % len(fileData))
		#dump_memory_block(fileData,0,len(fileData))
		open(GAME_FILES + filename, 'wb').write(fileData)
