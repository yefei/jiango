# -*- coding: utf-8 -*-
from django.forms.widgets import TextInput, MultiWidget, HiddenInput
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from .helpers import create_crypted_challenge
from .draws import draw


class CaptchaWidget(MultiWidget):
    def __init__(self, attrs=None, **kwargs):
        self._args = kwargs
        widgets = (
            HiddenInput(attrs),
            TextInput(attrs),
        )
        super(CaptchaWidget, self).__init__(widgets, attrs)
        self.output_attrs = {}
    
    def decompress(self, value):
        if value:
            return [value[:32], value[32:]]
        return [None, None]
    
    def format_output(self, rendered_widgets):
        hidden_field, text_field = rendered_widgets
        self.output_attrs['hidden_field'] = hidden_field
        self.output_attrs['text_field'] = text_field
        return self._args.get('output_format') % self.output_attrs
    
    def render(self, name, value, attrs=None):
        key = create_crypted_challenge()
        value = [key, u'']
        final_attrs = self.build_attrs(attrs)
        self.output_attrs = {
            'id': final_attrs.get('id', None),
            'image_url': reverse('jiango-captcha-image', kwargs={'key': key, 'ext': draw.image_ext}),
            'api_url': reverse('jiango-captcha-json'),
            'new_challenge': _('Get a new challenge'),
        }
        return super(CaptchaWidget, self).render(name, value, attrs=attrs)

    # This probably needs some more love
    def id_for_label(self, id_):
        if id_:
            id_ += '_1'
        return id_
