# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 14:33:31 2020

@author: yaoji
"""
import math
dacl = [0.0] * 9 + [-5.0, -10.0, 0.0, -20.0, 0.0, -2.5]
dacu = [5.0, 10.0, 20.0, 2 ** 24, 40.0] + [2 ** 24] * 4 + [5.0, 10.0, 2 ** 24, 20.0, 2 ** 24, 2.5]
adcl = [-10.24, -5.12, -2.56, 0.0, 0.0, 0.0, 0.0]
adcu = [10.24, 5.12, 2.56, 2 ** 24, 2 ** 24, 10.24, 5.12]
multiplier = [10.0, 1.0, 0.1]

def str2bool(v):
    return v.lower() in ("yes","true","t","1","True")

def b2v(b, bit_num = 16, lower_limit = -10, upper_limit = 10):
    return ((upper_limit - lower_limit) * b / (2 ** bit_num)) + lower_limit

def v2b(v, bit_num = 16, lower_limit = -10, upper_limit = 10):
    return int((v - lower_limit) / (upper_limit - lower_limit) * (2 ** bit_num))

def bv(b, flag, ran = 0):
    if flag == '20':
        lower_limit = -5.0
        upper_limit = 5.0
        bit_num = 20
    elif flag == 'a':
        lower_limit = adcl[ran]
        upper_limit = adcu[ran]
        bit_num = 16
    elif flag == 'd':
        lower_limit = dacl[ran]
        upper_limit = dacu[ran]
        bit_num = 16
    else:
        lower_limit = 0
        upper_limit = 2 ** 24
        bit_num = 16
        
    return b2v(b, bit_num, lower_limit, upper_limit)

def vb(v, flag, ran = 0):
    if flag == '20':
        lower_limit = -5.0
        upper_limit = 5.0
        bit_num = 20
    elif flag == 'a':
        lower_limit = adcl[ran]
        upper_limit = adcu[ran]
        bit_num = 16
    elif flag == 'd':
        lower_limit = dacl[ran]
        upper_limit = dacu[ran]
        bit_num = 16
    else:
        lower_limit = 0
        upper_limit = 2 ** 24
        bit_num = 16
        
    return v2b(v, bit_num, lower_limit, upper_limit)

# Convert I set bits to current setpoint based on current status
def b2i(bits, gain, ran):
    volt = bv(bits, 'd', ran)                              # Convert bits to voltage
    return 10.0 ** (-volt / 10.0) * multiplier[gain - 8]   # Return current setpoint
    
# Convert current setpoint to I set bits based on current status
def i2b(iset, gain, ran):
    volt = -10.0 * math.log(iset / multiplier[gain - 8], 10)    # Calculate I set voltage
    return vb(volt, 'd', ran)                                   # Convert it to I set bits

class myCNV():
    def __init__(self):
        self.dacl = [0.0] * 9 + [-5.0, -10.0, 0.0, -20.0, 0.0, -2.5]
        self.dacu = [5.0, 10.0, 20.0, 2 ** 24, 40.0] + [2 ** 24] * 4 + [5.0, 10.0, 2 ** 24, 20.0, 2 ** 24, 2.5]
        self.adcl = [-10.24, -5.12, -2.56, 0.0, 0.0, 0.0, 0.0]
        self.adcu = [10.24, 5.12, 2.56, 2 ** 24, 2 ** 24, 10.24, 5.12]
        
    def b2v(self, b, bit_num = 16, lower_limit = -10, upper_limit = 10):
        return ((upper_limit - lower_limit) * b / (2 ** bit_num)) + lower_limit

    def v2b(self, v, bit_num = 16, lower_limit = -10, upper_limit = 10):
        return int((v - lower_limit) / (upper_limit - lower_limit) * (2 ** bit_num))


if __name__ == "__main__":
    cnv = myCNV()