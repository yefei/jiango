# -*- coding: utf-8 -*-
from django.forms import ValidationError
from django.forms.fields import CharField, MultiValueField
from django.utils.translation import ugettext_lazy as _
from .widgets import CaptchaWidget
from .helpers import CaptchaStore, decrypt_challenge
from . import settings


class CaptchaField(MultiValueField):
    default_error_messages = {
        'invalid': _(u'Incorrect challenge')
    }
    
    def __init__(self, *args, **kwargs):
        fields = (
            CharField(show_hidden_initial=True), 
            CharField(),
        )
        
        kwargs['label'] = kwargs.get('label', _(u'Captcha'))
        output_format = kwargs.pop('output_format', settings.CAPTCHA_OUTPUT_FORMAT)
        
        super(CaptchaField, self).__init__(fields=fields,
                                           widget=CaptchaWidget(output_format=output_format), *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return ''.join(data_list)
        return None
    
    def clean(self, value):
        super(CaptchaField, self).clean(value)
        
        challenge = decrypt_challenge(value[0])
        if challenge is not None and challenge.lower() == value[1].lower():
            # 保证验证码一次性
            store = CaptchaStore(value[0])
            if not store.exists():
                store.create()
                return value[1]
        
        raise ValidationError(self.error_messages['invalid'])
