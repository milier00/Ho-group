# -*- coding: utf-8 -*-
"""
@Date     : 2021/12/8 20:58:10
@Author   : milier00
@FileName : patch linecut.py
"""
import os
import numpy as np
import matplotlib.pyplot as plt

file_list = []
dir_path = './test data/cc/'
for root, dirs, files in os.walk(dir_path, topdown=False):
    for file in files:
        if file[:4] == "test":
            data_path = os.path.join(root, file)
            file_list.append(data_path)
print('file number:', len(file_list))

dat_list = []
for file in file_list:
    dat = np.loadtxt(file)
    if file_list.index(file) == 0:
        dat_list.append(dat)
        dat_list = np.array(dat_list)
    else:
        dat_list = np.vstack((dat_list, dat))
print('patched data shape:', dat_list.shape)

plt.imshow(dat_list)
plt.show()