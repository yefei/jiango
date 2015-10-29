# -*- coding: utf-8 -*-
from time import time
try:
    from PIL import Image, ImageColor, ImageDraw, ImageFont
except ImportError:
    import Image, ImageColor, ImageDraw, ImageFont
from .base import BaseDraw


class CaptchaDraw(BaseDraw):
    
    minetype = 'image/png'
    image_type = 'png'
    image_ext = 'png'
    
    def __init__(self, options):
        super(CaptchaDraw, self).__init__(options)
        self._new()
    
    def _new(self):
        self.background_color = ImageColor.getrgb(self.options['BACKGROUND_COLOR'])
        self.font_color = ImageColor.getrgb(self.options['FONT_COLOR'])
        self.font_size = self.options['FONT_SIZE']
        
        self.size = (self.options['WIDTH'], self.options['HEIGHT'])
        self.im = Image.new('RGB', self.size, self.background_color)
        self.font = ImageFont.truetype(self.options['FONT_PATH'],
                                       self.options['FONT_SIZE'])
    
    def render(self, stream, value):
        im = self.im.copy()
        im2 = self.im.copy()
        x = 0
        r_i = sum(ord(c) for c in value)  # 根据验证码字符串产生一个固定数值
        for c in value:
            fgimg = Image.new('RGBA', self.size, self.font_color)
            charimg = Image.new('L', self.font.getsize(c), '#000000')
            
            draw = ImageDraw.Draw(charimg)
            draw.text((0, 0), c, font=self.font, fill='#ffffff')
            
            r = (int(time()) / 1000 + ord(c) + r_i) % 40 - 20  # 计算一段时间内每个字符的旋转值
            charimg = charimg.rotate(r, expand=1, resample=Image.BICUBIC)
            charimg = charimg.crop(charimg.getbbox())
            
            maskimg = Image.new('L', self.size)
            y = (im2.size[1] - charimg.size[1]) / 2
            maskimg.paste(charimg, (x, y, charimg.size[0] + x, charimg.size[1] + y))
            
            im2 = Image.composite(fgimg, im2, maskimg)
            x += charimg.size[0] - 5  # - X重叠值
        
        # 将生成的验证码 x 居中
        center = (im.size[0] - x) / 2
        im.paste(im2, (center, 0, im2.size[0]+center, im2.size[1]))
        
        im.save(stream, self.image_type)
