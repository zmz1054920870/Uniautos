#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# @Time    : 2021/3/25 23:53
# @Author  : 超级无敌张铁柱
# @File    : test.py

import re

p = '''system-view
         \^
Error: Unrecognized command found at '\^' position.
\[~'''

a = r'''<HUAWEI>system-view
Enter system view, return user view with return command.
[~HUAWEI]
system-view
         ^
Error: Unrecognized command found at '^' position.
[~HUAWEI]'''

c = re.search(p, a)
print(c.group())
