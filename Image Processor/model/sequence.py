# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 13:52:32 2020

@author: yaoji
"""

import conversion as cnv
import numpy as np
import copy


class mySequence():
    def __init__(self, command_list=[], data_list=[], mode=True):
        # Basic property
        self.name = 'New Sequence'              # Initialize sequence name
        self.path = ''                          # Initialize file path to empty
        self.command_list = command_list        # Initialize command list
        self.data_list = data_list              # Initialize data list
        self.seq_num = len(self.command_list)   # Figure out sequence number
        self.read_num = 0                       # Initialize read number
        self.read_index = -1                    # Initialize read index
        self.exp_time = 0                       # Expected time to finish
        # Figure out read number
        for index, cmd in enumerate(self.command_list):
            if (cmd >= 0xc0) and (cmd <= 0xdc):
                self.read_num += 1
                self.read_index = index


        # Flag initialization
        self.validation_required = (self.seq_num == 0)      # Initialize validation required to false
        self.validated = False                              # Initialize validated to false
                
        # Raw code
        self.command = []
        self.channel = []
        self.option1 = []
        self.option2 = []
        self.data = []
        
        # For compile use
        self.commandDict = {'Wait': [0x00, 0x00, 0x00000000, 0x00000000, 0xffffffff],
                            'Match': [0x20, 0x00, 0x80000000, 0x00000000, 0x0000ffff],
                            'Dout': [0x40, 0x03, 0x00000000, 0x00000000, 0x00000001],
                            'Shift': [0x60, 0x1f, 0x80000000, 0x00000000, 0x000fffff],
                            'Aout': [0x80, 0x1f, 0x00000000, 0x00000000, 0x000fffff],
                            'Ramp': [0xa0, 0x1f, 0x00000000, 0xfff00000, 0x000fffff],
                            'Read': [0xc0, 0x1c, 0x00000000, 0x00000000, 0x0000ffff],
                            'ShiftRamp': [0xe0, 0x1f, 0x80000000, 0x7ff00000, 0x000fffff]}
        self.channelDict = { # dsp.lastdac, key is same as index, the last two are dropped
                            'Z offset fine': 2, 'Z offset': 3, 'Iset': 5, 'DAC6': 6, 'DAC7': 7, 'DAC8': 8, 'DAC9': 9,'DAC11': 11, 'Bias': 13,
                            # adc, key/4 = index
                            'AIN0': 0x00, 'AIN1': 0x04, 'AIN2': 0x08, 'AIN3': 0x0c, 'AIN4': 0x10, 'AIN5': 0x14, 'ZOUT': 0x18, 'PREAMP': 0x1c,
                            # dsp.lastdigital, key is same as index, the first three
                            'DitherB': 0, 'DitherZ': 1, 'Feedback': 2, ' ': 0}
        self.dataDict = {'Wait': self.bb, 'Match': self.mb, 'Dout': self.bb, 'Shift': self.sb,
                         'Aout': self.ab, 'Ramp': self.ab, 'Read': self.bb, 'ShiftRamp': self.sb}
        
        # Sequence status
        self.mode = mode                        # True for read sequence, False for deposition sequence
                                                # Default read sequence
        self.bias_dac = False                   # Default 16 bitDAC for bias
        self.range = [10, 10, 14] + ([10] * 9) + [14, 9] + ([10] * 3)  # Default DAC range
        self.preamp_gain = 9                     # Default preamp gain
        self.dac = [0x8000] * 16 + [0x828f5]   # Default DAC last output
        self.dac[13] = 0x828f                   # Default 16bit bias last output
        self.feedback = True                    # Default feedback on
        self.ditherB = False                    # Default bias dither off
        self.ditherZ = False                    # Default Z dither off

    # Configure current STM setting
    # If all system status same as previous sequence status, keep validated flag unchanged
    # Otherwise validated flag set to False
    def configure(self, bias_dac, preamp_gain, dacrange, lastdac, last20bitdac):        
        # Update bias DAC selection
        if self.bias_dac != bias_dac:
            self.validated = False
            self.bias_dac = bias_dac
            if self.bias_dac:
                self.channelDict.update({'Bias': 16})
            else:
                self.channelDict.update({'Bias': 13})
                
        # Update pre-amp gain
        if self.preamp_gain != preamp_gain:
            self.validated = False
            self.preamp_gain = preamp_gain
        
        # Update all DAC range
        if self.range != dacrange:
            self.validated = False
            self.range = dacrange
        
        # Update all DAC last output
        if self.dac != (lastdac + [last20bitdac]):
            self.validated = False
            self.dac = lastdac + [last20bitdac]

    # Load raw code
    # command, channel and data are lists of string
    # option1 and option2 are list of data
    def load_data(self, command, channel, option1, option2, data):
        self.command = command
        self.channel = channel
        self.option1 = option1
        self.option2 = option2
        self.data = data
        self.seq_num = len(self.command)
        self.validation_required = True

    # !!! Not finished
    # Validate raw code
    def validation(self, ditherB, ditherZ, feedback, mode):
        error = 0
        if self.validation_required:
            if self.mode:       # Validate read sequence
                self.validated = True
            else:               # Validate deposition sequence
                self.validated = True
                
        if (error == 0) and self.validation_required:
            self.build()
            cmd_list = [hex(cmd) for cmd in self.command_list]
            dat_list = [hex(dat) for dat in self.data_list]
            # print("Command List:\n", cmd_list)
            # print("Data List:\n", dat_list)
            # print("read_index:", self.read_index)
        return error

    # !!! Not finished
    # Simulate image, return image data
    def simulation_i(self):
        image = np.zeros((128, 128))
        return image
    
    # !!! Not finished
    # Simulate spectroscopy, return spectroscopy data
    def simulation_s(self):
        spc = np.zeros(200)
        return spc

    # Compile raw code
    def build(self):
        self.command_list = []              # Initialize command list
        self.data_list = []                 # Initialize data list
        self.read_num = 0                   # Re-initialize read number
        self.exp_time = 0                   # Re-initialize expectation time
        
        if self.validation_required and self.validated:
            # Figure out read number
            for i in range(self.seq_num):
                comm = self.command[i]
                comp = self.commandDict[comm]
                ch = self.channelDict[self.channel[i]]
                op1 = self.option1[i]
                op2 = self.option2[i]
                dstr = self.data[i]
                # print("-----build(uncompiled)", comm, op1, op2, (self.dataDict[comm](dstr, ch) & comp[4]))
                self.command_list += [(comp[0] & 0xe0) | (ch & comp[1])]
                self.data_list += [(self.dataDict[comm](dstr, ch) & comp[4]) | ((op2 << 20) & comp[3]) |
                                   ((op1 * comp[2]) & 0x80000000)]
                # print("-----build(compiled)", comm, hex((op1 * comp[2]) & 0x80000000), bin((op2 << 20) & comp[3]), bin(self.dataDict[comm](dstr, ch) & comp[4]))
                
                if comm == 'Read':
                    self.read_num += 1
                    self.read_index = i
                if comm == 'Wait':
                    self.exp_time += self.data_list[i]
        print("Command List:\n", self.command_list)
        print("Data List:\n", self.data_list)
    
    # Data compiling function for general use
    def bb(self, dstr, ch):
        return self.dac[ch] if dstr == 'Origin' else int(dstr)
    
    # Data compiling function for matching current
    def mb(self, dstr, ch):
        v = cnv.bv(self.dac[5], 'd', self.range[5])
        b = cnv.vb(10.0 ** (-v / 10.0), 'a')
        return b
                
    # Data compiling function for analog output related
    def ab(self, dstr, ch):
        if dstr == 'Origin':                        # If back to origin
            b = self.dac[ch]
        else:
            if (ch == 2) or (ch == 3):
                b = int(dstr)                       # Convert data string to bits value
            elif ch == 5:
                b = cnv.i2b(float(dstr), self.preamp_gain, self.range[5])
            else:
                v = float(dstr)                     # Convert data string to voltage value
                if ch != 16:
                    b = cnv.vb(v, 'd', self.range[ch])
                else:
                    b = cnv.vb(v, '20')
        return b

    def sb(self, dstr, ch):
        if dstr == 'Origin':                        # If back to origin
            b = self.dac[ch]
            return b
        elif float(dstr) < 0:
            return 0x0
        else:
            if (ch == 2) or (ch == 3):              # z offset fine & z offset
                b = int(dstr)                       # Convert data string to bits value
            elif ch == 5:                           # i set
                b = cnv.i2b(float(dstr), self.preamp_gain, self.range[5]) - 0x8000
            else:
                v = float(dstr)                     # Convert data string to voltage value
                if ch != 16:
                    b = cnv.vb(v, 'd', self.range[ch]) - 0x8000
                else:
                    b = cnv.vb(v, '20') - 0x80000
            return b
