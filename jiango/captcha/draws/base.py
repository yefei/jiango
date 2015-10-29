# -*- coding: utf-8 -*-


class BaseDraw(object):
    
    minetype = None
    image_type = None
    image_ext = None
    
    def __init__(self, options):
        self.options = options
    
    def render(self, value, stream):
        raise NotImplementedError
