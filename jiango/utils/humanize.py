# -*- coding: utf-8 -*-
# Created on 2015-12-2
# @author: Yefei
import re
import datetime
from django.utils.timezone import is_aware, utc
from django.utils.translation import ungettext, ugettext
from django.utils.encoding import force_unicode


# 1d=1天,1h=1小时,1m=1分钟,1s=1秒s可以不加。例如10天20小时15分3秒: 10d20h15m3
def parse_humanize_second(value):
    if isinstance(value, basestring):
        if value.isdigit():
            return int(value)
        tmp = ''
        sec = 0
        for c in str(value).lower():
            if c.isdigit():
                tmp += c
            elif c == 'd':
                sec += int(tmp) * 86400
                tmp = ''
            elif c == 'h':
                sec += int(tmp) * 3600
                tmp = ''
            elif c == 'm':
                sec += int(tmp) * 60
                tmp = ''
            elif c == 's':
                sec += int(tmp)
                tmp = ''
        # 结尾不加 s 的秒数
        if tmp:
            sec += int(tmp)
        return sec
    return value


def humanize_second(seconds):
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return ''.join((('%dd' % days if days else ''),
                    ('%dh' % hours if hours else ''),
                    ('%dm' % minutes if minutes else ''),
                    (str(seconds) if seconds else ''),
                    ))


SIZE_UNITS = [None,'K','M','G','T','P','E','Z','Y']


def humanize_size(size, step=1024, units=SIZE_UNITS):
    if size < step:
        return size, None
    u = None
    for u in units:
        if abs(size) < step:
            break
        size /= float(step)
    return size, u


def intcomma4(value):
    return re.sub(r"(\d)(?=(\d{4})+(?!\d))", r"\1,", force_unicode(value))


def timesince_single(d, now=None, reversed=False):
    """
    Takes two datetime objects and returns the time between d and now
    as a nicely formatted string, e.g. "10 minutes".  If d occurs after now,
    then "0 minutes" is returned.
    """
    chunks = (
      (60 * 60 * 24 * 365, lambda n: ungettext('year', 'years', n)),
      (60 * 60 * 24 * 30, lambda n: ungettext('month', 'months', n)),
      (60 * 60 * 24 * 7, lambda n : ungettext('week', 'weeks', n)),
      (60 * 60 * 24, lambda n : ungettext('day', 'days', n)),
      (60 * 60, lambda n: ungettext('hour', 'hours', n)),
      (60, lambda n: ungettext('minute', 'minutes', n))
    )
    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    if not now:
        now = datetime.datetime.now(utc if is_aware(d) else None)

    delta = (d - now) if reversed else (now - d)
    # ignore microseconds
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        # d is in the future compared to now, stop processing.
        return u'0 ' + ugettext('minutes')
    for i, (seconds, name) in enumerate(chunks):
        count = since // seconds
        if count != 0:
            break
    return ugettext('%(number)d %(type)s') % {'number': count, 'type': name(count)}
