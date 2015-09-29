from django.conf.urls import url
from .views import captcha_image, captcha_json

urlpatterns = [
    url(r'^new.json$', captcha_json, name='jiango-captcha-json'),
    url(r'^(?P<key>[\w_-]+).(?P<ext>\w+)$', captcha_image, name='jiango-captcha-image'),
]
