# -*- coding: utf-8 -*-
# Created on 2015-9-5
# @author: Yefei
from django.core.paginator import Paginator, Page
from django.core.urlresolvers import reverse


class SafePaginator(Paginator):
    def validate_number(self, number):
        try:
            number = int(number)
        except (TypeError, ValueError):
            return 1
        if number < 1:
            return 1
        if number > self.num_pages:
            return self.num_pages
        return number


class Paging(SafePaginator):
    def __init__(self, object_list, request, per_page=30, field_name='page', *args, **kwargs):
        self.request = request
        self.field_name = field_name
        super(Paging, self).__init__(object_list, per_page, *args, **kwargs)
    
    def page(self):
        return super(Paging, self).page(self.request.GET.get(self.field_name))
    
    def page_url(self, page_number):
        getvars = self.request.GET.copy()
        getvars[self.field_name] = page_number
        return '%s?%s' % (self.request.path, getvars.urlencode())
    
    def previous_url(self, page_obj):
        if page_obj.has_previous():
            return self.page_url(page_obj.previous_page_number())
    
    def next_url(self, page_obj):
        if page_obj.has_next():
            return self.page_url(page_obj.next_page_number())


class ReversePaging(SafePaginator):
    def __init__(self, object_list, request, viewname, view_args=None, view_kwargs=None, per_page=30, field_name='page',
                 *args, **kwargs):
        self.request = request
        self.viewname = viewname
        self.view_args = view_args
        self.view_kwargs = view_kwargs or {}
        self.field_name = field_name
        super(ReversePaging, self).__init__(object_list, per_page, *args, **kwargs)
    
    def page_url(self, page_number):
        getvars = ''
        if self.request.GET:
            getvars = '?' + self.request.GET.urlencode()
        self.view_kwargs[self.field_name] = page_number
        return '%s%s' % (reverse(self.viewname, args=self.view_args, kwargs=self.view_kwargs), getvars)
    
    def previous_url(self, page_obj):
        if page_obj.has_previous():
            return self.page_url(page_obj.previous_page_number())
    
    def next_url(self, page_obj):
        if page_obj.has_next():
            return self.page_url(page_obj.next_page_number())


def paginate(page_obj, window=1):
    if not page_obj:
        return None
    assert isinstance(page_obj, Page), "%r is not %r object" % (page_obj, Page)
    assert isinstance(page_obj.paginator, (Paging, ReversePaging)), "%r is not %r object" % (page_obj.paginator, Paging)
    
    paginator = page_obj.paginator
    page_range = paginator.page_range
    
    # First and last are simply the first *n* pages and the last *n* pages,
    # where *n* is the current window size.
    first = set(page_range[:window])
    last = set(page_range[-window:])
    # Now we look around our current page, making sure that we don't wrap
    # around.
    current_start = page_obj.number-1-window
    if current_start < 0:
        current_start = 0
    current_end = page_obj.number+window
    if current_end < 0:
        current_end = 0
    current = set(page_range[current_start:current_end])
    pages = []
    # If there's no overlap between the first set of pages and the current
    # set of pages, then there's a possible need for elusion.
    if len(first.intersection(current)) == 0:
        first_list = list(first)
        first_list.sort()
        second_list = list(current)
        second_list.sort()
        pages.extend(first_list)
        diff = second_list[0] - first_list[-1]
        # If there is a gap of two, between the last page of the first
        # set and the first page of the current set, then we're missing a
        # page.
        if diff == 2:
            pages.append(second_list[0] - 1)
        # If the difference is just one, then there's nothing to be done,
        # as the pages need no elusion and are correct.
        elif diff == 1:
            pass
        # Otherwise, there's a bigger gap which needs to be signaled for
        # elusion, by pushing a None value to the page list.
        else:
            pages.append(None)
        pages.extend(second_list)
    else:
        unioned = list(first.union(current))
        unioned.sort()
        pages.extend(unioned)
    # If there's no overlap between the current set of pages and the last
    # set of pages, then there's a possible need for elusion.
    if len(current.intersection(last)) == 0:
        second_list = list(last)
        second_list.sort()
        diff = second_list[0] - pages[-1]
        # If there is a gap of two, between the last page of the current
        # set and the first page of the last set, then we're missing a 
        # page.
        if diff == 2:
            pages.append(second_list[0] - 1)
        # If the difference is just one, then there's nothing to be done,
        # as the pages need no elusion and are correct.
        elif diff == 1:
            pass
        # Otherwise, there's a bigger gap which needs to be signaled for
        # elusion, by pushing a None value to the page list.
        else:
            pages.append(None)
        pages.extend(second_list)
    else:
        differenced = list(last.difference(current))
        differenced.sort()
        pages.extend(differenced)
    
    page_urls = []
    for page in pages:
        page_urls.append((page, paginator.page_url(page) if page else None))
    
    return {
        'count': paginator.count,
        'pages': pages,
        'page_urls': page_urls,
        'previous_url': paginator.previous_url(page_obj),
        'next_url': paginator.next_url(page_obj),
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': paginator.count > paginator.per_page,
    }
