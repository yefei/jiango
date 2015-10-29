from cStringIO import StringIO
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from jiango.shortcuts import render_serialize
from .helpers import decrypt_challenge, create_crypted_challenge
from .draws import draw


def captcha_image(request, key, ext):
    challenge = decrypt_challenge(key)
    if not challenge:
        raise Http404()
    buf = StringIO()
    draw.render(buf, challenge)
    return HttpResponse(buf.getvalue(), draw.minetype)


@render_serialize
def captcha_json(request, response):
    key = create_crypted_challenge()
    image_uri = reverse('jiango-captcha-image', kwargs={'key': key, 'ext': draw.image_ext})
    return {'key': key, 'image': image_uri}
