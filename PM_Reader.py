#!/usr/bin/env python3
# -*- coding: utf-8 -*-


PIXEL_SET = '█︎'
PIXEL_CLEAR = ' '

def drawFont(addr,firstChar,lastChar):
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

data = open('Murder on the Zinderneuf (1983)[a].atx.atboot','rb').read()
drawFont(0x1934,0x00,0x3F)
