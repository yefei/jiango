# -*- coding: utf-8 -*-
from time import time
from PIL import Image, ImageColor, ImageDraw, ImageFont
from .base import BaseDraw


class CaptchaDraw(BaseDraw):
    
    minetype = 'image/png'
    image_type = 'png'
    image_ext = 'png'
    
    def __init__(self, options):
        super(CaptchaDraw, self).__init__(options)
        self.background = ImageColor.getrgb(self.options['BACKGROUND'])
        self.color = self.options['COLOR']
        self.size = self.options['SIZE']
        self.width = self.options['WIDTH']
        self.height = self.options['HEIGHT']
        self.im = Image.new('RGB', (self.width, self.height), self.background)
        self.font = ImageFont.truetype(self.options['FONT'], self.size)
    
    def render(self, stream, value):
        draw_im = self.im.copy()
        draw = ImageDraw.Draw(draw_im)
        x = 0
        for c in value:
            f_size, f_offset = self.font.font.getsize(c)
            y = (self.height - f_size[1]) / 2 - f_offset[1]  # 字符上下居中
            draw.text((x, y), c, font=self.font, fill=self.color)
            x += f_size[0] - int(self.size * 0.15)

        # 文字左右居中
        center = (self.width - x) / 2
        im = self.im.copy()
        im.paste(draw_im, (center, 0, self.width + center, self.height))

        # 绘制一条干扰线
        draw = ImageDraw.Draw(im)
        r = int(time() / 1000) % 1000 / 1000.0
        draw.line((center, r * self.height, center + x, (1-r) * self.height), self.color, 2)

        im.save(stream, self.image_type)
