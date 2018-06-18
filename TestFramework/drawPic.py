#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import os

class drawPic():

    def createPic(self, x, y, picFile):
        if not os.path.exists(picFile):
            im = Image.new('RGB', (x,y),'white')
            im.save(picFile)
        else:
            os.remove(picFile)
            im = Image.new('RGB', (x,y),'white')
            im.save(picFile)


    def drawRec(self, x0, y0, x1, y1, picFile, col = 'red'):

        im = Image.open(picFile)
        draw = ImageDraw.Draw(im)
        draw.rectangle((x0, y0, x1, y1), outline=col)
        im.save(picFile)

    def drawLine(self, x0, y0, x1, y1, picFile, col = 'red'):
        im = Image.open(picFile)
        draw = ImageDraw.Draw(im)
        draw.line([(x0, y0), (x1,y1)], width=1, fill=col)
        im.save(picFile)

    def drawText(self, x0, y0, text, picFile, col = 'blue'):
        fontpath = '/usr/share/fonts/truetype/freefont/FreeSerif.ttf'
        mfont = ImageFont.truetype(fontpath,32)
        im = Image.open(picFile)
        draw = ImageDraw.Draw(im)
        draw.text((x0,y0),text,fill=col, font=mfont)
        im.save(picFile)

if __name__ == '__main__':

    dpic = drawPic()
    picFile = 'activity.jpeg'
    dpic.createPic(800,600,picFile)

    for i in range(0,10):

        dpic.drawRec(100,i*10, 200,i*10+5 ,picFile)
        dpic.drawText(300, i*10, 'hello')

