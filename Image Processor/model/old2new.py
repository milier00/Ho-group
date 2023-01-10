# -*- coding: utf-8 -*-
"""
@Date     : 1/8/2023 18:11:41
@Author   : milier00
@FileName : old2new.py
"""
import copy
import os
import numpy as np
import pickle

""" 
Convert old topography to .nstm file
This converts all files in the folder to .nstm, assuming it is topography
Use this as an example and modify by your data 
"""
dir_path = r"D:\Code\2022oct\old2new"   # old data to be converted, change it to your path
topo_list = []
topos = []
for root, dirs, files in os.walk(dir_path, topdown=False):
    for file in files:
        data_path = os.path.join(root, file)
        topo_list.append(file)
        img = np.flipud(np.loadtxt(data_path)).T[np.newaxis, :, :]
        print(img.shape)
        # open a dummy .nstm file as a model
        with open(r".\11102208.nstm", 'rb') as input:
            fake_sample = pickle.load(input)
        fake_sample.name = file
        fake_sample.path = data_path
        fake_sample.step_num = img.shape[1]
        fake_sample.step_size = img.shape[2]
        fake_sample.data = copy.deepcopy(img)
        # where to save the converted .nstm, change it to your path
        with open('D:/Code//2022oct/old2new/'+file+'.nstm', 'wb') as output:
            pickle.dump(fake_sample, output, pickle.HIGHEST_PROTOCOL)  # Save data

print('topo number:', len(topo_list))
