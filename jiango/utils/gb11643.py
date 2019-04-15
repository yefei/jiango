# -*- coding: utf-8 -*-
"""
Author: FeiYe <316606233@qq.com>
Since: 2019/4/15
"""


# 验证身份证有效性
def check_gb11643(id_number):
    if len(id_number) != 18:
        return False

    # 每一位加权因子
    q = [(2 ** i) % 11 for i in range(18)]
    q.reverse()

    # 根据身份证的前17位，求和取余，返回余数
    n = 0
    for i in range(17):
        n += int(id_number[i]) * int(q[i])
    n = n % 11

    # 根据前17位的余数，计算第18位校验位的值
    t = 0
    for i in range(12):
        if (n + i) % 11 == 1:
            t = i % 11
    if t == 10:
        return id_number[-1].upper() == 'X'
    return id_number[-1] == str(t)
