import os
from django.conf import settings


def thispath(*p):
    return os.path.join(os.path.dirname(__file__), *p)


CAPTCHA_AGE = getattr(settings, 'CAPTCHA_AGE', 60 * 15)

CAPTCHA_OUTPUT_FORMAT = getattr(settings, 'CAPTCHA_OUTPUT_FORMAT', """
%(hidden_field)s
%(text_field)s
<div class="help-block">
<img src="%(image_url)s" id="%(id)s_image">
<a href="javascript:;" class="btn" onclick="$.getJSON('%(api_url)s',function(r){$('#%(id)s_image').attr('src',r.image);$('#%(id)s_0').val(r.key);});">%(new_challenge)s</a>
</div>""")

CAPTCHA_CHARS = 'ABCDEFGHJKLMNPRSTWXZV'

CAPTCHA_LENGTH = getattr(settings, 'CAPTCHA_LENGTH', 4)  # Chars

CAPTCHA_DRAWS = {
    'default': {
        'DRAW': 'jiango.captcha.draws.simple',
        'OPTIONS': {
            'WIDTH': 100,
            'HEIGHT': 30,
            'BACKGROUND_COLOR': '#E0E8F3',
            'FONT_COLOR': '#000000',
            'FONT_SIZE': 30,
            'FONT_PATH': thispath('fonts', 'verdana.ttf'),
        }
    }
}

if hasattr(settings, 'CAPTCHA_DRAWS'):
    CAPTCHA_DRAWS.update(settings.CAPTCHA_DRAWS)

CAPTCHA_DRAW = getattr(settings, 'CAPTCHA_DRAW', 'default')
