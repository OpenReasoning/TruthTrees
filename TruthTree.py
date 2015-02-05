"""
Truth Tree implementation written in Python
"""

# -*- coding: utf-8 -*-

from __future__ import print_function
from forseti.parser import get_main_symbol

__author__ = 'mpeveler'

"""
[A if (B and C)
 C iff B
 not C
 not (not A)]
"""

TREE = ["A > (B & C)", "C < B", "- C", "- (- A)"]
# symbols = ["&", "|", ">", "<", "-"]

for i in TREE:
    print(get_main_symbol(i))
