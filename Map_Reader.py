#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw

asmmap = bytearray(open('Zinderneuf.bin','rb').read())
map_font = bytearray(open('./Gamefiles/MAP.SET','rb').read())

MAP_HEIGHT = 102
MAP_WIDTH = 40
CHAR_HEIGHT = 8
CHAR_WIDTH = 2
COLOR_BITS = 4

COLORS = (
		(0x00,0x00,0x00),
		(0xFF,0xFF,0xFF),
		(0xAA,0x00,0x00),
		(0xFF,0x55,0x55),
		(0xFF,0xFF,0x55),
		(0x55,0xFF,0x55),
		(0x55,0x55,0xFF),
		(0x00,0x00,0xAA),
		(0x55,0x55,0x55),
		(0xAA,0xAA,0xAA),
		(0xFF,0x55,0xFF),
		(0xAA,0x88,0x00),
		(0x00,0xAA,0x00),
		(0x00,0xAA,0xAA),
		(0xAA,0x00,0xAA),
		(0x55,0xFF,0xFF),
		)

img = Image.new('RGB', (MAP_WIDTH * CHAR_WIDTH * COLOR_BITS, int(MAP_HEIGHT * CHAR_HEIGHT)), color = 'white')
draw = ImageDraw.Draw(img)

for row in range(MAP_HEIGHT):
	for col in range(MAP_WIDTH):
		tile = asmmap[col + row * MAP_WIDTH]
		fonttile = map_font[tile * 8:tile * 8+8]
		for frow in range(CHAR_HEIGHT):
			for fcol in range(CHAR_WIDTH):
				color = COLORS[(fonttile[frow] >> (COLOR_BITS*fcol)) & ((1<<COLOR_BITS)-1)]
				for p in range(COLOR_BITS):
					draw.point([((col * CHAR_WIDTH + fcol) * COLOR_BITS + p, row * CHAR_HEIGHT + frow)], color)

img.save('ASMMAP.png')
