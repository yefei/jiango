# -*- coding: utf-8 -*-
from django.db.models.fields import PositiveIntegerField, SmallIntegerField
from jiango.forms.fields import SecondField as FormSecondField


class SecondField(PositiveIntegerField):
    def formfield(self, **kwargs):
        defaults = {'form_class': FormSecondField}
        defaults.update(kwargs)
        return super(SecondField, self).formfield(**defaults)


class OrderField(SmallIntegerField):
    def __init__(self, verbose_name=u'顺序', *args, **kwargs):
        if 'blank' not in kwargs:
            kwargs['blank'] = True
        if 'db_index' not in kwargs:
            kwargs['db_index'] = True
        if 'help_text' not in kwargs:
            kwargs['help_text'] = u'按照从小到大排序，不填写则自动在最后'
        super(OrderField, self).__init__(verbose_name, *args, **kwargs)

    def pre_save(self, model_instance, add):
        val = super(OrderField, self).pre_save(model_instance, add)
        if val is None:
            try:
                qs = self.model.objects
                if model_instance:
                    qs = qs.exclude(pk=model_instance.pk)
                last_obj = qs.latest(self.attname)
            except self.model.DoesNotExist:
                last_obj = None
            val = last_obj.order + 1 if last_obj else 0
        return val
