# -*- coding: utf-8 -*-
import random
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
        for c in value:
            fgimg = Image.new('RGBA', self.size, self.font_color)
            charimg = Image.new('L', self.font.getsize(c), '#000000')
            
            draw = ImageDraw.Draw(charimg)
            draw.text((0,0), c, font=self.font, fill='#ffffff')
            
            charimg = charimg.rotate(random.randint(-20,20), expand=1, resample=Image.BICUBIC)
            charimg = charimg.crop(charimg.getbbox())
            
            maskimg = Image.new('L', self.size)
            y = (im2.size[1] - charimg.size[1]) / 2
            maskimg.paste(charimg, (x, y, charimg.size[0] + x, charimg.size[1] + y))
            
            im2 = Image.composite(fgimg, im2, maskimg)
            x += charimg.size[0] - 3 # - X重叠值
        
        # 将生成的验证码 x 居中
        center = (im.size[0] - x) / 2
        im.paste(im2, (center, 0, im2.size[0]+center, im2.size[1]))
        
        im.save(stream, self.image_type)
