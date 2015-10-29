# -*- coding: utf-8 -*-
# Created on 2015-10-16
# @author: Yefei
from django.db import models, router
from django.db.models.deletion import Collector
from django.utils.text import capfirst
from django.utils.encoding import force_unicode


def get_deleted_objects(queryset, using=None):
    if using is None:
        using = router.db_for_write(queryset.model)
        print using
    
    collector = NestedObjects(using=using)
    collector.collect(queryset)
    
    def format_callback(obj):
        opts = obj._meta
        return u'%s: %s' % (capfirst(opts.verbose_name), force_unicode(obj))

    to_delete = collector.nested(format_callback)
    protected = [format_callback(obj) for obj in collector.protected]
    return to_delete, protected


class NestedObjects(Collector):
    def __init__(self, *args, **kwargs):
        super(NestedObjects, self).__init__(*args, **kwargs)
        self.edges = {}  # {from_instance: [to_instances]}
        self.protected = set()

    def add_edge(self, source, target):
        self.edges.setdefault(source, []).append(target)

    def collect(self, objs, source_attr=None, **kwargs):
        for obj in objs:
            if source_attr:
                self.add_edge(getattr(obj, source_attr), obj)
            else:
                self.add_edge(None, obj)
        try:
            return super(NestedObjects, self).collect(objs, source_attr=source_attr, **kwargs)
        except models.ProtectedError, e:
            self.protected.update(e.protected_objects)

    def related_objects(self, related, objs):
        qs = super(NestedObjects, self).related_objects(related, objs)
        return qs.select_related(related.field.name)

    def _nested(self, obj, seen, format_callback):
        if obj in seen:
            return []
        seen.add(obj)
        children = []
        for child in self.edges.get(obj, ()):
            children.extend(self._nested(child, seen, format_callback))
        if format_callback:
            ret = [format_callback(obj)]
        else:
            ret = [obj]
        if children:
            ret.append(children)
        return ret

    def nested(self, format_callback=None):
        """
        Return the graph as a nested list.
        """
        seen = set()
        roots = []
        for root in self.edges.get(None, ()):
            roots.extend(self._nested(root, seen, format_callback))
        return roots
