# -*- coding: utf-8 -*-
from django.template import Context
from django.template.loader import get_template
from django import template
from django import forms
from django.forms.forms import BoundField

register = template.Library()


@register.filter
def bootstrap(element):
    if isinstance(element, BoundField):
        tpl = get_template("bootstrap/field.html")
        context = Context({'field': element})
    else:
        has_management = getattr(element, 'management_form', None)
        if has_management:
            tpl = get_template("bootstrap/formset.html")
            context = Context({'formset': element})
        else:
            tpl = get_template("bootstrap/form.html")
            context = Context({'form': element})
    return tpl.render(context)


@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxInput)


@register.filter
def is_multiple_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxSelectMultiple)


@register.filter
def is_radio(field):
    return isinstance(field.field.widget, forms.RadioSelect)


@register.filter
def is_file(field):
    return isinstance(field.field.widget, forms.FileInput)
