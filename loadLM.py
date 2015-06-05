# -*- coding: utf-8 -*-
"""
Created on Fri Jun 05 02:03:29 2015

@author: Misha Kushnir
"""

def readTestLM():
    f = open("TestLM", 'r')
    LMlines = []
    for line in f:
        LMlines.append(line)
        
    return LMlines
    f.close()