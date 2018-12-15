# created by YeFei<316606233@qq.com>
# since 2018/10/11
from django.template import Template, RequestContext
from django.utils.functional import cached_property
from .models import get_cache_menus


class ItemWrapper:
    def __init__(self, item, request):
        self.item = item
        self.request = request

    @property
    def children(self):
        for i in self.item.children:
            yield ItemWrapper(i, self.request)

    @property
    def is_active(self):
        return self.url == self.request.path

    @cached_property
    def url(self):
        return Template(self.item.value).render(RequestContext(self.request))

    def __getitem__(self, item):
        return getattr(self.item, item)

    def __iter__(self):
        for i in self.children:
            yield i


class Menus:
    def __init__(self, request):
        self.request = request

    def __getitem__(self, item):
        for i in get_cache_menus():
            if i.value == item:
                return ItemWrapper(i, self.request)

    def __iter__(self):
        for i in get_cache_menus():
            yield ItemWrapper(i, self.request)


def menu(request):
    return {
        'MENUS': Menus(request),
    }
