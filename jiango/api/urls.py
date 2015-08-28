# -*- coding: utf-8 -*-
from .loader import autodiscover, urlpatterns as api_urlpatterns

autodiscover()

urlpatterns = api_urlpatterns
