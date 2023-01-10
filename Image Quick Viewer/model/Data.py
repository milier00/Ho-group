# -*- coding: utf-8 -*-
"""
@Date     : 2021/4/5 16:31:03
@Author   : milier00
@FileName : Data.py
"""

import sys
import copy
import numpy as np
import os
from func1D import myFunc
import pickle
from DataStruct import *


class Spc_SinglePt():
    def __init__(self, data, scan_dir, data_num):
        super().__init__()
        self.data = data
        self.mode = scan_dir
        self.dat_num = data.shape[1]
        self.ch_num = data.shape[0]-1 if data.shape[0]-1 <=4 else (data.shape[0]-1)//2
        self.data_num = data_num

        self.xf = None; self.ch0f = None; self.ch1f = None; self.ch2f = None;
        self.xb = None; self.ch0b = None; self.ch1b = None; self.ch2b = None;
        self.channels = [self.xf, self.ch0f, self.ch1f, self.ch2f, self.ch0b, self.ch1b, self.ch2b]
        self.x_fwd = None; self.ch0_fwd = None; self.ch1_fwd = None; self.ch2_fwd = None;
        self.fwd = [self.x_fwd, self.ch0_fwd, self.ch1_fwd, self.ch2_fwd]
        self.x_bwd = None; self.ch0_bwd = None; self.ch1_bwd = None; self.ch2_bwd = None;
        self.bwd = [self.x_bwd, self.ch0_bwd, self.ch1_bwd, self.ch2_bwd]
        self.x_avg = None; self.ch0_avg = None; self.ch1_avg = None; self.ch2_avg = None;
        self.avg = [self.x_avg, self.ch0_avg, self.ch1_avg, self.ch2_avg]
        # print('---', self.data.shape, self.ch_num)
        self.load_ch()

    def load_ch(self):
        if self.mode != 2:
            for i in range(self.ch_num+1):
                self.channels[i] = self.data[i, :]

            if self.mode == 0:  # forward only
                self.fwd = self.channels
                self.avg = self.channels
            elif self.mode == 1:    # backward only
                self.bwd = self.channels
                self.avg = self.channels
            elif self.mode == 3:    # avg forward and backward
                self.avg = self.channels
        elif self.mode == 2:    # forward and backward
            for i in range(self.data.shape[0]):
                self.channels[i] = self.data[i, :]
            for i in range(self.ch_num+1):
                self.fwd[i] = self.channels[i]
            self.bwd[0] = self.channels[0]
            for i in range(self.ch_num+1, self.data.shape[0]):
                self.bwd[i-3] = self.channels[i]
            for i in range(self.ch_num+1):
                tmp = np.vstack((self.fwd[i], self.bwd[i]))
                self.avg[i] = np.average(tmp, axis=0)


    # for SpcPassEditor refresh_list and init_list
    def pack_data(self, show_fb):
        if not show_fb:
            # each element is a 2d array (x,ch), length=ch_num
            # [(x,I),(x,X1), (x, X2)]
            data_list = []
            for i in range(1, self.ch_num+1):
                data_list.append(np.vstack((self.avg[0], self.avg[i])))
        else:
            # each element is a 2d array (x,ch), length=ch_num,
            # [(x,Ifwd),(x,X1fwd), (x, X2fwd),(x,Ibwd),(x,X1bwd),(x,X2bwd)]
            data_list = []
            for i in range(1, self.ch_num+1):
                data_list.append(np.vstack((self.fwd[0], self.fwd[i])))
            for i in range(1, self.ch_num+1):
                data_list.append(np.vstack((self.bwd[0], self.bwd[i])))
        return data_list


class SpcData():

    def __init__(self, path):
        super().__init__()
        
        dir, file = os.path.split(path)
        self.name = file
        self.path = path
        self.dir = dir
        self.indentor = '      '

        '''
        self.child:
        # True: single pass file
        # False: parent and not every
        # None: child
        '''
        self.ischild = False
        self.if_child()
        self.child = []       # axis0 is pass num, each one is spc
        self.child_name = []  # name list for child data
        self.child_path = []  # 2d array list for child data
        self.child_dict = {}  # data dict {'name': data}
        '''
        self.every:
        # True: parent and every
        # False: parent and not every
        # None: child
        '''
        self.every = False
        self.load_child()

        with open(path, 'rb') as input:
            spc = pickle.load(input)
        spc.get_cnv_data()

        '''
        spc.data_:
        # axis 0 is point index
        # axis 1 is read channel
        # axis 2 is data num
        '''
        self.data = spc.data
        self.data_num = spc.data_num
        (self.pt_num, _, self.dat_num) = spc.data.shape
        self.ch_num = spc.data.shape[1]-1 if spc.data.shape[1] <= 4 else (spc.data.shape[1]-1)//2
        self.pass_num = spc.pass_num
        self.pt_data = []
        '''
        # Scan direction flag: 
        # 0 -> Read forward only
        # 1 -> Read backward only
        # 2 -> Read both forward and backward but don't average
        # 3 -> Average both forward and backward
        '''
        self.scan_dir = spc.scan_dir
        self.ch_names = []
        self.ch_names_folded = []
        self.get_ch_names()
        self.pt_ch_names = []
        self.pt_ch_names_folded = []
        self.get_pt_ch_names()
        self.ch_suffix = []
        self.ch_suffix_folded = []
        self.get_ch_suffix()
        self.point_list = spc.point_list    # Physical point list
        self.load_spc()

        self.func1D = myFunc()

    # Load single physical point data (single-pass/averaged-passes)
    def load_spc(self):
        for i in range(self.pt_num):
            pt = Spc_SinglePt(self.data[i], self.scan_dir, self.data_num)
            self.pt_data.append(pt)

    # Check if it's child
    def if_child(self):
        if self.name.find('_pass') != -1 and self.name[-4:] == ".spc":
            self.ischild = True
        elif self.name.find('_pass') == -1 and self.name[-4:] == ".spc":
            self.ischild = False
        return self.ischild

    # If it's save every and parent, load child data
    # Update self.if_child and self.every variable
    def load_child(self):
        find = 0
        for root, dirs, files in os.walk(self.dir, topdown=False):
            for file in files:
                if file[-4:] == ".spc" and file.find(self.name[:8]) != -1 and file.find('_pass') != -1:
                    self.every = True
                    find += 1
                    if self.ischild:    # save every but it's child
                        self.every = None
                    else:               # save every and it's parent
                        data_path = os.path.join(root, file)
                        with open(data_path, 'rb') as input:
                            child = pickle.load(input)
                        child.get_cnv_data()
                        self.child.append(child)
                        self.child_path.append(data_path)
                        self.child_name.append(file)

        # save pass-averaged data, only one child is parent itself
        if find == 0:
            self.every = False
            with open(self.path, 'rb') as input:
                child = pickle.load(input)
            child.get_cnv_data()
            self.child.append(child)
            self.child_path.append(self.path)
            self.child_name.append(self.name)

        self.child_num = len(self.child)

    # self must be a parent!!!
    def avg_child(self, show_fb):
        self.avg = []  # each element is a list for a single point = [x_avg, ch0_avg, ch1_avg, ch2_avg]
        self.avg_fwd = []  # each element is a list for a single point = [x_avg_fwd, ch0_avg_fwd, ch1_avg_fwd, ch2_avg_fwd]
        self.avg_bwd = []  # each element is a list for a single point = [x_avg_bwd, ch0_avg_bwd, ch1_avg_bwd, ch2_avg_bwd]
        pt_all_pass = []
        packed_data = []

        # load all child for each point
        for i in range(self.pt_num):
            pt_data_list = []  # length = pass_num; each element is Spc_SinglePt()
            for j in range(self.child_num):
                single_pt = Spc_SinglePt(self.child[j].data[i], self.scan_dir, self.data_num)
                pt_data_list.append(single_pt)
            pt_all_pass.append(pt_data_list)

            # average foeward and backward
            if not show_fb:
                x = [];
                ch0 = [];
                ch1 = [];
                ch2 = [];
                for ind, pt in enumerate(pt_all_pass[i]):
                    x.append(pt.avg[0])
                    if (pt.avg[1]) is not None:
                        ch0.append(pt.avg[1])
                    else:
                        ch0 = None
                    if (pt.avg[2]) is not None:
                        ch1.append(pt.avg[2])
                    else:
                        ch1 = None
                    if (pt.avg[3]) is not None:
                        ch2.append(pt.avg[3])
                    else:
                        ch2 = None

                x = np.array(x)
                ch0 = np.array(ch0) if ch0 is not None else None
                ch1 = np.array(ch1) if ch1 is not None else None
                ch2 = np.array(ch2) if ch2 is not None else None

                x_avg = np.average(x, axis=0)
                ch0_avg = np.average(ch0, axis=0) if ch0 is not None else None
                ch1_avg = np.average(ch1, axis=0) if ch1 is not None else None
                ch2_avg = np.average(ch2, axis=0) if ch2 is not None else None

                self.avg.append([x_avg, ch0_avg, ch1_avg, ch2_avg])

            # keep forward and backward
            else:
                # not backward only
                if self.scan_dir != 1:
                    x_fwd = [];
                    ch0_fwd = [];
                    ch1_fwd = [];
                    ch2_fwd = [];
                    for ind, pt in enumerate(pt_all_pass[i]):
                        if pt.fwd[0] is not None:
                            x_fwd.append(pt.fwd[0])
                        else:
                            x_fwd = None
                        if (pt.fwd[1]) is not None:
                            ch0_fwd.append(pt.fwd[1])
                        else:
                            ch0_fwd = None
                        if (pt.fwd[2]) is not None:
                            ch1_fwd.append(pt.fwd[2])
                        else:
                            ch1_fwd = None
                        if (pt.fwd[3]) is not None:
                            ch2_fwd.append(pt.fwd[3])
                        else:
                            ch2_fwd = None

                    x_fwd = np.array(x_fwd) if x_fwd is not None else None
                    ch0_fwd = np.array(ch0_fwd) if ch0_fwd is not None else None
                    ch1_fwd = np.array(ch1_fwd) if ch1_fwd is not None else None
                    ch2_fwd = np.array(ch2_fwd) if ch2_fwd is not None else None

                    x_avg_fwd = np.average(x_fwd, axis=0) if x_fwd is not None else None
                    ch0_avg_fwd = np.average(ch0_fwd, axis=0) if ch0_fwd is not None else None
                    ch1_avg_fwd = np.average(ch1_fwd, axis=0) if ch1_fwd is not None else None
                    ch2_avg_fwd = np.average(ch2_fwd, axis=0) if ch2_fwd is not None else None
                    self.avg_fwd.append([x_avg_fwd, ch0_avg_fwd, ch1_avg_fwd, ch2_avg_fwd])
                else:
                    self.avg_fwd = None

                # not forward only
                if self.scan_dir != 0:
                    x_bwd = [];
                    ch0_bwd = [];
                    ch1_bwd = [];
                    ch2_bwd = [];
                    for ind, pt in enumerate(pt_data_list):
                        if pt.bwd[0] is not None:
                            x_bwd.append(pt.bwd[0])
                        else:
                            x_bwd = pt.bwd[0]
                        if (pt.bwd[1]) is not None:
                            ch0_bwd.append(pt.bwd[1])
                        else:
                            ch0_bwd = None
                        if (pt.bwd[2]) is not None:
                            ch1_bwd.append(pt.bwd[2])
                        else:
                            ch1_bwd = None
                        if (pt.bwd[3]) is not None:
                            ch2_bwd.append(pt.bwd[3])
                        else:
                            ch2_bwd = None

                    x_bwd = np.array(x_bwd) if x_bwd is not None else None
                    ch0_bwd = np.array(ch0_bwd) if ch0_bwd is not None else None
                    ch1_bwd = np.array(ch1_bwd) if ch1_bwd is not None else None
                    ch2_bwd = np.array(ch2_bwd) if ch2_bwd is not None else None

                    x_avg_bwd = np.average(x_bwd, axis=0) if x_bwd is not None else None
                    ch0_avg_bwd = np.average(ch0_bwd, axis=0) if ch0_bwd is not None else None
                    ch1_avg_bwd = np.average(ch1_bwd, axis=0) if ch1_bwd is not None else None
                    ch2_avg_bwd = np.average(ch2_bwd, axis=0) if ch2_bwd is not None else None
                    self.avg_bwd.append([x_avg_bwd, ch0_avg_bwd, ch1_avg_bwd, ch2_avg_bwd])
                else:
                    self.avg_bwd = None

        # pack data, each element is a list of a single point, len=pt_num
        # packed_data[i] = [(x,ch0),(x,ch1),(x,ch2)]
        for i in range(self.pt_num):
            avg_list = []
            if not show_fb:
                for k in range(self.ch_num):
                    avg_list.append(np.vstack((self.avg[i][0], self.avg[i][k + 1])))
            elif self.scan_dir == 0:
                for k in range(self.ch_num):
                    avg_list.append(np.vstack((self.avg_fwd[i][0], self.avg_fwd[i][k + 1])))
            elif self.scan_dir == 1:
                for k in range(self.ch_num):
                    avg_list.append(np.vstack((self.avg_bwd[i][0], self.avg_bwd[i][k + 1])))
            elif self.scan_dir == 2:
                for k in range(self.ch_num):
                    avg_list.append(np.vstack((self.avg_fwd[i][0], self.avg_fwd[i][k + 1])))
                for k in range(self.ch_num):
                    avg_list.append(np.vstack((self.avg_bwd[i][0], self.avg_bwd[i][k + 1])))
            elif self.scan_dir == 3:
                for k in range(self.ch_num):
                    avg_list.append(np.vstack((self.avg[i][0], self.avg[i][k + 1])))


            packed_data.append(avg_list)

        # print('packed:', len(packed_data), len(packed_data[0]), packed_data[0][0].shape)  # 4 6 (2, 218)/4 3 (2, 218)
        return packed_data

    # Average passes
    # show_fb: if show forward and backward
    # del_pass: delelted passes not to average
    def avg_child_part(self, show_fb: bool, del_pass: list) -> list:
        # There are passes deleted
        if del_pass is not None:
            self.avg = []       # each element is a list for a single point = [x_avg, ch0_avg, ch1_avg, ch2_avg]
            self.avg_fwd = []   # each element is a list for a single point = [x_avg_fwd, ch0_avg_fwd, ch1_avg_fwd, ch2_avg_fwd]
            self.avg_bwd = []   # each element is a list for a single point = [x_avg_bwd, ch0_avg_bwd, ch1_avg_bwd, ch2_avg_bwd]
            pt_all_pass = []
            packed_data = []

            # load all child for each point
            for i in range(self.pt_num):
                pt_data_list = []  # length = pass_num; each element is Spc_SinglePt()
                for j in range(self.child_num):
                    if j not in del_pass[i]:
                        single_pt = Spc_SinglePt(self.child[j].data[i], self.scan_dir, self.data_num)
                        pt_data_list.append(single_pt)
                pt_all_pass.append(pt_data_list)

                # average foeward and backward
                if not show_fb:
                    x = [];
                    ch0 = [];
                    ch1 = [];
                    ch2 = [];
                    for ind, pt in enumerate(pt_all_pass[i]):
                        x.append(pt.avg[0])
                        if (pt.avg[1]) is not None:
                            ch0.append(pt.avg[1])
                        else:
                            ch0 = None
                        if (pt.avg[2]) is not None:
                            ch1.append(pt.avg[2])
                        else:
                            ch1 = None
                        if (pt.avg[3]) is not None:
                            ch2.append(pt.avg[3])
                        else:
                            ch2 = None

                    x = np.array(x)
                    ch0 = np.array(ch0) if ch0 is not None else None
                    ch1 = np.array(ch1) if ch1 is not None else None
                    ch2 = np.array(ch2) if ch2 is not None else None

                    x_avg = np.average(x, axis=0)
                    ch0_avg = np.average(ch0, axis=0) if ch0 is not None else None
                    ch1_avg = np.average(ch1, axis=0) if ch1 is not None else None
                    ch2_avg = np.average(ch2, axis=0) if ch2 is not None else None

                    self.avg.append([x_avg, ch0_avg, ch1_avg, ch2_avg])

                # keep forward and backward
                else:
                    # not backward only
                    if self.scan_dir != 1:
                        x_fwd = [];
                        ch0_fwd = [];
                        ch1_fwd = [];
                        ch2_fwd = [];
                        for ind, pt in enumerate(pt_all_pass[i]):
                            if pt.fwd[0] is not None:
                                x_fwd.append(pt.fwd[0])
                            else:
                                x_fwd = None
                            if (pt.fwd[1]) is not None:
                                ch0_fwd.append(pt.fwd[1])
                            else:
                                ch0_fwd = None
                            if (pt.fwd[2]) is not None:
                                ch1_fwd.append(pt.fwd[2])
                            else:
                                ch1_fwd = None
                            if (pt.fwd[3]) is not None:
                                ch2_fwd.append(pt.fwd[3])
                            else:
                                ch2_fwd = None

                        x_fwd = np.array(x_fwd) if x_fwd is not None else None
                        ch0_fwd = np.array(ch0_fwd) if ch0_fwd is not None else None
                        ch1_fwd = np.array(ch1_fwd) if ch1_fwd is not None else None
                        ch2_fwd = np.array(ch2_fwd) if ch2_fwd is not None else None

                        x_avg_fwd = np.average(x_fwd, axis=0) if x_fwd is not None else None
                        ch0_avg_fwd = np.average(ch0_fwd, axis=0) if ch0_fwd is not None else None
                        ch1_avg_fwd = np.average(ch1_fwd, axis=0) if ch1_fwd is not None else None
                        ch2_avg_fwd = np.average(ch2_fwd, axis=0) if ch2_fwd is not None else None
                        self.avg_fwd.append([x_avg_fwd, ch0_avg_fwd, ch1_avg_fwd, ch2_avg_fwd])
                    else:
                        self.avg_fwd = None

                    # not forward only
                    if self.scan_dir != 0:
                        x_bwd = [];
                        ch0_bwd = [];
                        ch1_bwd = [];
                        ch2_bwd = [];
                        for ind, pt in enumerate(pt_data_list):
                            if pt.bwd[0] is not None:
                                x_bwd.append(pt.bwd[0])
                            else:
                                x_bwd = pt.bwd[0]
                            if (pt.bwd[1]) is not None:
                                ch0_bwd.append(pt.bwd[1])
                            else:
                                ch0_bwd = None
                            if (pt.bwd[2]) is not None:
                                ch1_bwd.append(pt.bwd[2])
                            else:
                                ch1_bwd = None
                            if (pt.bwd[3]) is not None:
                                ch2_bwd.append(pt.bwd[3])
                            else:
                                ch2_bwd = None

                        x_bwd = np.array(x_bwd) if x_bwd is not None else None
                        ch0_bwd = np.array(ch0_bwd) if ch0_bwd is not None else None
                        ch1_bwd = np.array(ch1_bwd) if ch1_bwd is not None else None
                        ch2_bwd = np.array(ch2_bwd) if ch2_bwd is not None else None

                        x_avg_bwd = np.average(x_bwd, axis=0) if x_bwd is not None else None
                        ch0_avg_bwd = np.average(ch0_bwd, axis=0) if ch0_bwd is not None else None
                        ch1_avg_bwd = np.average(ch1_bwd, axis=0) if ch1_bwd is not None else None
                        ch2_avg_bwd = np.average(ch2_bwd, axis=0) if ch2_bwd is not None else None
                        self.avg_bwd.append([x_avg_bwd, ch0_avg_bwd, ch1_avg_bwd, ch2_avg_bwd])
                    else:
                        self.avg_bwd = None

            # pack data, each element is a list of a single point, len=pt_num
            # packed_data[i] = [(x,ch0),(x,ch1),(x,ch2)]
            for i in range(self.pt_num):
                avg_list = []
                if not show_fb:
                    for k in range(self.ch_num):
                        avg_list.append(np.vstack((self.avg[i][0], self.avg[i][k + 1])))
                elif self.scan_dir == 0:
                    for k in range(self.ch_num):
                        avg_list.append(np.vstack((self.avg_fwd[i][0], self.avg_fwd[i][k + 1])))
                elif self.scan_dir == 1:
                    for k in range(self.ch_num):
                        avg_list.append(np.vstack((self.avg_bwd[i][0], self.avg_bwd[i][k + 1])))
                elif self.scan_dir == 2:
                    for k in range(self.ch_num):
                        avg_list.append(np.vstack((self.avg_fwd[i][0], self.avg_fwd[i][k + 1])))
                    for k in range(self.ch_num):
                        avg_list.append(np.vstack((self.avg_bwd[i][0], self.avg_bwd[i][k + 1])))
                elif self.scan_dir == 3:
                    for k in range(self.ch_num):
                        avg_list.append(np.vstack((self.avg[i][0], self.avg[i][k + 1])))

                packed_data.append(avg_list)

            print('packed part:', len(packed_data), len(packed_data[0]), packed_data[0][0].shape) #4 6 (2, 218)/4 3 (2, 218)
            return packed_data
        # No passes are deleted
        else:
            return self.avg_child(show_fb)

    # abandoned!!!
    def pre_calibrate(self, ch_index, pt_index, del_pass, show_pt, show_fb):

        # calibrate all channels
        if ch_index == -1:
            raw_avg = self.avg_child_part(show_fb, del_pass)[pt_index]
            ### raw_avg : [(x,ch0_fwd), (x,ch1_fwd), (x,ch2_fwd), (x,ch0_bwd), (x,ch1_bwd), (x,ch2_bwd)]
            if show_fb:
                cal_fwd = self.calibrate_single(raw_avg[:3])
                cal_bwd = self.calibrate_single(raw_avg[3:])
            ### raw_avg : [(x,ch0), (x,ch1), (x,ch2)]
            else:
                cal_avgfb = self.calibrate_single(raw_avg)
            return raw_avg
        else:
            raw_avg = self.avg_child_part(show_fb, del_pass)[pt_index][ch_index]
            return raw_avg

    def calibrate_single(self, bundle):
        bias = bundle[0][0]
        I = bundle[0][1]
        dIdV = bundle[1][1]
        IETS = bundle[2][1]

        int_didv = self.func1D.do_int(bias, dIdV)


    # !!! need to fix
    def get_ch_names(self):
        # for i, cmd in enumerate(data.seq.command_list):
        #     if (data.seq.command_list[i] >= 0xc0) and (data.seq.command_list[i] <= 0xdc):
        #         channel = (data.seq.command_list[i] - 0xc0) / 4
        #         self.ch_names += [
        #             list(data.seq.channelDict.keys())[list(data.seq.channelDict.values()).index(channel)]]
        # print(self.ch_names)    # ['DAC7', 'Z offset fine', 'Z offset']

        if self.ch_num == 1:
            if self.scan_dir == 0:
                self.ch_names = [self.indentor+self.name+'_I_fwd']
            elif self.scan_dir == 1:
                self.ch_names = [self.indentor+self.name + '_I_bwd']
            elif self.scan_dir == 2:
                self.ch_names = [self.indentor+self.name + '_I_fwd', self.indentor+self.name + '_I_bwd']
            elif self.scan_dir == 3:
                self.ch_names = [self.indentor+self.name + '_I_avgfb']
        elif self.ch_num == 2:
            if self.scan_dir == 0:
                self.ch_names = [self.indentor+self.name + '_I_fwd', self.indentor+self.name + '_X1_fwd']
            elif self.scan_dir == 1:
                self.ch_names = [self.indentor+self.name + '_I_bwd', self.indentor+self.name + '_X1_bwd']
            elif self.scan_dir == 2:
                self.ch_names = [self.indentor+self.name + '_I_fwd', self.indentor+self.name + '_X1_fwd', self.indentor+self.name + '_I_bwd', self.indentor+self.name + '_X1_bwd']
            elif self.scan_dir == 3:
                self.ch_names = [self.indentor+self.name + '_I_avgfb', self.indentor+self.name + '_X1_avgfb']
        elif self.ch_num == 3:
            if self.scan_dir == 0:
                self.ch_names = [self.indentor+self.name + '_I_fwd', self.indentor+self.name + '_X1_fwd', self.indentor+self.name + '_X2_fwd']
            elif self.scan_dir == 1:
                self.ch_names = [self.indentor+self.name + '_I_bwd', self.indentor+self.name + '_X1_bwd', self.indentor+self.name + '_X2_bwd']
            elif self.scan_dir == 2:
                self.ch_names = [self.indentor+self.name + '_I_fwd', self.indentor+self.name + '_X1_fwd', self.indentor+self.name + '_X2_fwd',
                                 self.indentor+self.name + '_I_bwd', self.indentor+self.name + '_X1_bwd', self.indentor+self.name + '_X2_bwd']
            elif self.scan_dir == 3:
                self.ch_names = [self.indentor+self.name + '_I_avgfb', self.indentor+self.name + '_X1_avgfb', self.indentor+self.name + '_X2_avgfb']


        if self.ch_num == 1:
                self.ch_names_folded = [self.indentor+self.name + '_I_avgfb']
        elif self.ch_num == 2:
                self.ch_names_folded = [self.indentor+self.name + '_I_avgfb', self.indentor+self.name + '_X1_avgfb']
        elif self.ch_num == 3:
                self.ch_names_folded = [self.indentor+self.name + '_I_avgfb', self.indentor+self.name + '_X1_avgfb', self.indentor+self.name + '_X2_avgfb']


    def get_ch_suffix(self):
        if self.ch_num == 1:
            if self.scan_dir == 0:
                self.ch_suffix = ['_I_fwd']
            elif self.scan_dir == 1:
                self.ch_suffix = ['_I_bwd']
            elif self.scan_dir == 2:
                self.ch_suffix = ['_I_fwd', '_I_bwd']
            elif self.scan_dir == 3:
                self.ch_suffix = ['_I_avgfb']
        elif self.ch_num == 2:
            if self.scan_dir == 0:
                self.ch_suffix = ['_I_fwd', '_X1_fwd']
            elif self.scan_dir == 1:
                self.ch_suffix = ['_I_bwd', '_X1_bwd']
            elif self.scan_dir == 2:
                self.ch_suffix = ['_I_fwd', '_X1_fwd', '_I_bwd', '_X1_bwd']
            elif self.scan_dir == 3:
                self.ch_suffix = ['_I_avgfb', '_X1_avgfb']
        elif self.ch_num == 3:
            if self.scan_dir == 0:
                self.ch_suffix = ['_I_fwd', '_X1_fwd', '_X2_fwd']
            elif self.scan_dir == 1:
                self.ch_suffix = ['_I_bwd', '_X1_bwd', '_X2_bwd']
            elif self.scan_dir == 2:
                self.ch_suffix = ['_I_fwd', '_X1_fwd', '_X2_fwd', '_I_bwd', '_X1_bwd', '_X2_bwd']
            elif self.scan_dir == 3:
                self.ch_suffix = ['_I_avgfb', '_X1_avgfb', '_X2_avgfb']


        if self.ch_num == 1:
            self.ch_suffix_folded = ['_I_avgfb']
        elif self.ch_num == 2:
            self.ch_suffix_folded = ['_I_avgfb', '_X1_avgfb']
        elif self.ch_num == 3:
            self.ch_suffix_folded = ['_I_avgfb', '_X1_avgfb', '_X2_avgfb']


    def get_pt_ch_names(self):
        for i in range(self.pt_num):
            if self.ch_num == 1:
                if self.scan_dir == 0:
                    self.pt_ch_names += [self.name + '_Pt#'+str(i+1).zfill(2), self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_I_fwd']
                elif self.scan_dir == 1:
                    self.pt_ch_names += [self.name + '_Pt#'+str(i+1).zfill(2), self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_I_bwd']
                elif self.scan_dir == 2:
                    self.pt_ch_names += [self.name + '_Pt#'+str(i+1).zfill(2), self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_I_fwd', self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_I_bwd']
                elif self.scan_dir == 3:
                    self.pt_ch_names += [self.name + '_Pt#'+str(i+1).zfill(2), self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_I_avgfb']
            elif self.ch_num == 2:
                if self.scan_dir == 0:
                    self.pt_ch_names += [self.name + '_Pt#'+str(i+1).zfill(2), self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_I_fwd', self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_X1_fwd']
                elif self.scan_dir == 1:
                    self.pt_ch_names += [self.name + '_Pt#'+str(i+1).zfill(2), self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_I_bwd', self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_X1_bwd']
                elif self.scan_dir == 2:
                    self.pt_ch_names += [self.name + '_Pt#'+str(i+1).zfill(2), self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_I_fwd', self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_X1_fwd',
                                        self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_I_bwd', self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_X1_bwd']
                elif self.scan_dir == 3:
                    self.pt_ch_names += [self.name + '_Pt#'+str(i+1).zfill(2), self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_I_avgfb', self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_X1_avgfb']
            elif self.ch_num == 3:
                if self.scan_dir == 0:
                    self.pt_ch_names += [self.name + '_Pt#'+str(i+1).zfill(2), self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_I_fwd', self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_X1_fwd',
                                        self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_X2_fwd']
                elif self.scan_dir == 1:
                    self.pt_ch_names += [self.name + '_Pt#'+str(i+1).zfill(2), self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_I_bwd', self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_X1_bwd',
                                        self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_X2_bwd']
                elif self.scan_dir == 2:
                    self.pt_ch_names += [self.name + '_Pt#'+str(i+1).zfill(2), self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_I_fwd', self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_X1_fwd',
                                        self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_X2_fwd',
                                        self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_I_bwd', self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_X1_bwd',
                                        self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_X2_bwd']
                elif self.scan_dir == 3:
                    self.pt_ch_names += [self.name + '_Pt#'+str(i+1).zfill(2), self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_I_avgfb', self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_X1_avgfb',
                                        self.indentor + self.name + '_Pt#'+str(i+1).zfill(2) + '_X2_avgfb']


            if self.ch_num == 1:
                self.pt_ch_names_folded += [self.name + '_avg_Pt#'+str(i+1).zfill(2), self.indentor + self.name + '_avg_Pt#'+str(i+1).zfill(2) + '_I_avgfb']
            elif self.ch_num == 2:
                self.pt_ch_names_folded += [self.name + '_avg_Pt#'+str(i+1).zfill(2), self.indentor + self.name + '_avg_Pt#'+str(i+1).zfill(2) + '_I_avgfb', self.indentor + self.name + '_avg_Pt#'+str(i+1).zfill(2) + '_X1_avgfb']
            elif self.ch_num == 3:
                self.pt_ch_names_folded += [self.name + '_avg_Pt#'+str(i+1).zfill(2), self.indentor + self.name + '_avg_Pt#'+str(i+1).zfill(2) + '_I_avgfb', self.indentor + self.name + '_avg_Pt#'+str(i+1).zfill(2) + '_X1_avgfb',
                                           self.indentor + self.name + '_avg_Pt#'+str(i+1).zfill(2) + '_X2_avgfb']
        # print(self.pt_ch_names)
        # print(self.pt_ch_names_folded)


""" Figure out channel order """
from matplotlib import pyplot as plt
# path = 'D:/Code/2022oct/spc\\1104220z.spc'
# with open(path, 'rb') as input:
#     spc = pickle.load(input)
#     print(spc.data_.shape)  # parent.data_ = (1, 4, 436)    child.data_ = (1, 7, 218)
#     print(spc.data.shape)   # parent.data = (1, 7, 218)     child.data = (0,)
    # print('\n', spc.data_[0][2])
    # print('\n', spc.data[0][2])
    # plt.plot(spc.data[0][0], spc.data[0][1], label='1')     # I_fwd
    # plt.plot(spc.data[0][0], spc.data[0][2], label='2')   # X1_fwd
    # plt.plot(spc.data[0][0], spc.data[0][3], label='3')   # X2_fwd
    # plt.plot(spc.data[0][0], spc.data[0][4], label='4')     # I_bwd
    # plt.plot(spc.data[0][0], spc.data[0][5], label='5')   # X1_bwd
    # plt.plot(spc.data[0][0], spc.data[0][6], label='6')   # X2_bwd
    # plt.legend()
    # plt.show()

""" Test average child partially """
# spc = SpcData('D:/Code/2022oct/spc/testttt\\1105220c.spc')# 1 1 4 196 1 1 / 0 1 4 196 1 0
# print(spc.pass_num, spc.pt_num, spc.ch_num, spc.dat_num, spc.scan_dir, len(spc.child))    # 10 4 4 436 2
# show_fb = True
# del_pass = [[1],[1,2,3,4,5,6,7],[],[1,2,3,4,5,6,7,8,9,10]]
# pack = spc.avg_child_part(show_fb, del_pass)
# plt.plot(pack[0][5][0], pack[0][5][1])
# plt.show()
# print(spc.pt_ch_names)
""" Test load_child for pass-aveasged data """
# spc = SpcData('D:/Code/2022oct/spc/testttt\\1104220f.spc')
# print(spc.every, spc.pass_num, spc.pt_num, spc.ch_num, spc.dat_num, spc.scan_dir, len(spc.child))
# no child
""" """
# spc = SpcData('D:/Code/2022oct/spc/testttt\\1104220b.spc')
# print(spc.every, spc.pass_num, spc.pt_num, spc.ch_num, spc.dat_num, spc.scan_dir, len(spc.child))#True 1 1 3 201 2 1
# with open('D:/Code/2022oct/spc/testttt\\1117220d.spc', 'rb') as input:
#     spc = pickle.load(input)
# print(spc.data.shape) #(1, 4, 11)
""" """
# for i, pt in enumerate(spc.pt_data):
#     pt.load_ch()
#     print(i, pt.ch_num, pt.avg[0].shape)
# print(spc.child[0].data.shape)
# single = Spc_SinglePt(spc.child[0].data[1], spc.scan_dir, spc.data_num)
# single.load_ch()
# print(single.fwd)
# spc.avg_child(True)
# print(spc.avg[0][0].shape)  # Point#0, ch0 (218,)
""" Search for data """
# dir_path= 'D:/Code/2022oct/spc/testttt'
# for root, dirs, files in os.walk(dir_path, topdown=False):
#     for file in files:
#         if file[-4:] == ".spc" and file.find('_pass1') == -1:
#             data_path = os.path.join(root, file)
#             with open(data_path, 'rb') as input:
#                 spc = pickle.load(input)
#                 ch_num = spc.data.shape[1]-1 if spc.data.shape[1] <= 4 else (spc.data.shape[1] - 1) // 2
#                 print(file, '\t', spc.scan_dir, '\t',  ch_num, '\t', spc.data_.shape, '\t', spc.data.shape)
""" Search for data """
# dir_path= 'D:/Code/2022oct/spc/testttt'
# for root, dirs, files in os.walk(dir_path, topdown=False):
#     for file in files:
#         if file[-4:] == ".spc" and file.find('_pass') != -1:
#             data_path = os.path.join(root, file)
#             with open(data_path, 'rb') as input:
#                 spc = pickle.load(input)
#                 spc.data = spc.data_
#                 print(file, spc.data.shape)
#             with open(data_path, 'wb') as output:
#                 pickle.dump(spc, output, pickle.HIGHEST_PROTOCOL)  # Save data

""" Search for data """
# dir_path= 'D:/Code/2022oct/spc'
# multi_path = []
# multi_name = []
# for root, dirs, files in os.walk(dir_path, topdown=False):
#     for file in files:
#         if file[-4:] == ".spc" and file.find('_pass') == -1:
#             data_path = os.path.join(root, file)
#             try:
#                 data = SpcData(data_path)
#                 if data.pass_num > 1 and data.every:
#                     # print(data.name, data.pass_num, data.ch_num)
#                     multi_path.append(data_path)
#                     multi_name.append(file)
#             except:
#                 continue
#
# for ind, name in enumerate(multi_name):
#     with open(multi_path[ind], 'rb') as input:
#         spc = pickle.load(input)
#     print('----------------------')
#     print(spc.scan_dir)
#     print(name, spc.data_.shape)
#     print(name, spc.data.shape)
#     for root, dirs, files in os.walk(dir_path, topdown=False):
#         for file in files:
#             if file[-4:] == ".spc" and file.find(name[:8]) != -1 and file.find("_pass") != -1:
#                 data_path = os.path.join(root, file)
#                 with open(data_path, 'rb') as input:
#                     spc = pickle.load(input)
#                 print(file, spc.data_.shape)
#                 print(file, spc.data.shape)

""" Make a fake data with 4 points, 4 channels, 436 pts """
### fake parent data
# import copy
# path = 'D:/Code/2022oct/spc/testttt\\1105220c.spc'
# with open(path, 'rb') as input:
#     spc = pickle.load(input)
# tmp1 = np.zeros(spc.data.shape)
# tmp2 = np.ones(spc.data.shape)
# tmp3 = np.ones(spc.data.shape) + 1
# spc.data = np.vstack((spc.data, tmp1))
# spc.data = np.vstack((spc.data, tmp2))
# spc.data = np.vstack((spc.data, tmp3))
# print(spc.data.shape)   # (4, 4, 436)
#
# with open(path, 'wb') as output:
#     pickle.dump(spc, output, pickle.HIGHEST_PROTOCOL)  # Save data

### check
# spc = SpcData('D:/Code/2022oct/spc/testttt\\1105220c.spc')
# print(spc.pass_num, spc.pt_num, spc.ch_num, spc.dat_num)    # 10 4 3 218
#
# data_path = 'D:/Code/2022oct/spc/testttt\\1105220c.spc'
# with open(data_path, 'rb') as input:
#     spc = pickle.load(input)
# print(spc.data.shape)  # (1, 7, 218)

### fake children
# #
# for root, dirs, files in os.walk('D:/Code/2022oct/spc/testttt', topdown=False):
#     for file in files:
#         if file[-4:] == ".spc" and file.find('1105220c') != -1 and file.find('_pass') != -1:
#             print(file)
#             data_path = os.path.join(root, file)
#             with open(data_path, 'rb') as input:
#                 spc = pickle.load(input)
#             spc.data = spc.data_
#             print(spc.data.shape)   # (1, 7, 218)
#             tmp1 = copy.deepcopy(spc.data)
#             tmp2 = copy.deepcopy(spc.data)
#             tmp3 = copy.deepcopy(spc.data)
#             spc.data = np.vstack((spc.data, tmp1))
#             spc.data = np.vstack((spc.data, tmp2))
#             spc.data = np.vstack((spc.data, tmp3))
#             print(spc.data.shape)  # (4, 7, 218)
#             # for i in range(1, spc.data.shape[0]):
#             #     for j in range(1, spc.data.shape[1]):
#             #         spc.data[i][j] = spc.data[0][j] + np.random.random()*(np.max(spc.data[0][j])-np.min(spc.data[0][j]))
#
#             with open(data_path, 'wb') as output:
#                 pickle.dump(spc, output, pickle.HIGHEST_PROTOCOL)  # Save data




class MappingData():

    def __init__(self, path):
        super().__init__()
        dir, file = os.path.split(path)
        self.name = file
        self.path = path

        self.child_name = []  # name list for child data
        self.child_data = []  # 2d array list for child data
        self.child_dict = {}  # data dict {'name': data}

        with open(path, 'rb') as input:
            self.grid = pickle.load(input)
        # self.header = grid.header

        # self.scale = grid.header['dim_px']

        # self.channels = grid.header['channels']
        # if grid.header['num_channels'] > 75:
        #     return

        ''' ccpp 1.1 read the 2nd channel '''
        self.data = self.grid.data
        self.data_ = copy.deepcopy(self.data)
        self.child_num = self.data.shape[0]
        self.energy = [0] * self.data.shape[0]
        self.scale = (200, 200)
        self.get_child()
        self.indentor = '\t'

    def get_child(self):
        for i in range(self.child_num):
            self.child_name.append('\t' + self.name + '_No' + str(i).zfill(2))
            self.child_data.append(self.data[i, :, :])
            self.child_dict[self.child_name[-1]] = self.child_data[-1]

class MappingResult():
    ''' data is MappingData; index = -1 (parent), index = num (child) '''
    def __init__(self, data, index):
        super().__init__()
        self.parent_data = data
        self.parent_index = index
        self.parent_name = data.name
        self.parent_path = data.path
        self.scale = data.scale
        self.name = ''
        self.result = []
        self.energy = []
        self.scale = []
        self.get_energy(data, index)
        self.get_target(data, index)

    def get_energy(self, data, index):
        if index == -1:
            self.energy = data.energy
        else:
            self.energy = [data.energy[index]]

    def get_target(self, data, index):
        if index == -1:
            self.target = data.child_data
        else:
            self.target = [data.child_data[index]]



