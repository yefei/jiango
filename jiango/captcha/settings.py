import os
from django.conf import settings

thispath = lambda *p: os.path.join(os.path.dirname(__file__), *p)


CAPTCHA_AGE = getattr(settings,'CAPTCHA_AGE', 60 * 60 * 1)

CAPTCHA_OUTPUT_FORMAT = getattr(settings,'CAPTCHA_OUTPUT_FORMAT', """
%(hidden_field)s
<div>
    <div style="float:left;width:100px;">%(image_tag)s</div>
    <div style="float:left;width:80px;">%(text_field)s</div>
    <div style="float:left;line-height:30px;padding-left:10px">%(new_challenge_tag)s</div>
    <div class="clearfix"></div>
</div>""")

CAPTCHA_CHARS = 'ABCDEFGHJKLMNPRSTWXZV'

CAPTCHA_LENGTH = getattr(settings, 'CAPTCHA_LENGTH', 4) # Chars


CAPTCHA_DRAWS = getattr(settings, 'CAPTCHA_DRAWS', {
    'default': {
        'DRAW': 'jiango.captcha.draws.simple',
        'OPTIONS': {
            'WIDTH': 100,
            'HEIGHT': 30,
            'BACKGROUND_COLOR': '#E0E8F3',
            'FONT_COLOR': '#000000',
            'FONT_SIZE': 30,
            'FONT_PATH': thispath('fonts','verdana.ttf'),
        }
    }
})

CAPTCHA_DRAW = getattr(settings, 'CAPTCHA_DRAW', 'default')
