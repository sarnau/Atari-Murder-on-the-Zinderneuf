#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import struct
from PIL import Image, ImageDraw, ImageShow, ImageFont


PIXEL_SET = '█︎'
PIXEL_CLEAR = ' '

class bcolors:
	BLACK = '\033[38;5;0m'
	WHITE = '\033[38;5;15m'
	RED = '\033[38;5;1m'
	CYAN = '\033[38;5;13m'
	PURPLE = '\033[38;5;5m'
	GREEN = '\033[38;5;2m'
	BLUE = '\033[38;5;4m'
	YELLOW = '\033[38;5;11m'

	ORANGE = '\033[38;5;220m'
	BROWN = '\033[38;5;88m'
	LIGHT_RED = '\033[38;5;9m'
	DARK_GREY = '\033[38;5;238m'
	GREY = '\033[38;5;244m'
	LIGHT_GREEN = '\033[38;5;10m'
	LIGHT_BLUE = '\033[38;5;12m'
	LIGHT_GREY = '\033[38;5;252m'
	
	DEFAULT = '\033[1;39m'

atari_colors = (
			bcolors.BLACK,
			bcolors.GREEN,
			bcolors.BLUE,
			bcolors.GREY,
			)


def drawFont(addr,firstChar=0x00,lastChar=0x40,isColor=False):
	print('Font $%04x $%02x-$%02x' % (addr,firstChar,lastChar))
	print('=====================')
	if isColor:
		width = 8
		lineLen = 16
	else:
		width = 16
		lineLen = 8
	gap = 0
	chheight = 8
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
					st = ''
					if isColor:
						for i in range(0,len(bstr),2):
							val = int(bstr[i:i+2],2)
							st += atari_colors[val]+PIXEL_SET*2
						st += bcolors.DEFAULT
					else:
						st = bstr.replace('1',PIXEL_SET*2).replace('0',PIXEL_CLEAR*2)
					s += st + ' ' + ' ' * gap
			print(s)
	print()

DIR = './Gamefiles/'
for filename in sorted(os.listdir(DIR)):
	if not filename.endswith('.SET'):
		continue
	print(filename)
	print('=' * len(filename))
	data = open(DIR + filename,'rb').read()
	if filename == 'MAP.SET':
		color = True
	else:
		color = False
	drawFont(0x0000,0x00,0x7F,color)  # multi color - Font for characters in the rooms
