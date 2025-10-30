# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 14:22:09 2025

@author: Dan Hargreaves
"""

def test(loc):
    if type(loc) == str:
        print('test1')
        loc = [int(loc[1])-1, ord(loc[0])-97]
        
    print(loc)
    
test('f6')