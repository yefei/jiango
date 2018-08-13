# -*- coding: utf-8 -*-
from django.db.models.fields import PositiveIntegerField
from jiango.forms.fields import SecondField as FormSecondField


class SecondField(PositiveIntegerField):
    def formfield(self, **kwargs):
        defaults = {'form_class': FormSecondField}
        defaults.update(kwargs)
        return super(SecondField, self).formfield(**defaults)
