# -*- coding: utf-8 -*-
"""
@Date     : 1/8/2023 18:53:21
@Author   : milier00
@FileName : old2new.py
"""
import os
import numpy as np
import pickle
""" 
Convert old spectra to .spc file 
This converts single .txt to .spc, assuming it has 6 channels
I forward, I backward, didv fwd, didv bws, IETS fwd, IETS bwd 
Use this as an example and modify by your data 
"""

dir_path = 'C:/Users/DAN/Downloads/exp/'    # old data to be converted

# get a file list for raw data
file_list = []
for root, dirs, files in os.walk(dir_path, topdown=False):
    for file in files:
        if file[:6] == "100422" and file[-4:] == '.txt':
            data_path = os.path.join(root, file)
            file_list.append(data_path)
print('file number:', len(file_list))


dir_path = 'C:/Users/DAN/Downloads/exp/'
index = file_list.index(dir_path+"10042249.txt")
file_name = os.path.split(file_list[index])[1][:-4]

ivf = np.loadtxt(file_list[index], skiprows=1)
didvf = np.loadtxt(file_list[index+1], skiprows=1)
ietsf = np.loadtxt(file_list[index+2], skiprows=1)
ivb = np.loadtxt(file_list[index+3], skiprows=1)
didvb = np.loadtxt(file_list[index+4], skiprows=1)
ietsb = np.loadtxt(file_list[index+5], skiprows=1)

bias = ivf[:,0]

data = np.vstack((bias, ivf[:,1])); data = np.vstack((data, didvf[:,1]));
data = np.vstack((data, ietsf[:,1])); data = np.vstack((data, ivb[:,1]));
data = np.vstack((data, didvb[:,1])); data = np.vstack((data, ietsb[:,1]));
data = data[np.newaxis,:,:]
print(data.shape)

# open a dummy .nstm file as a model
with open('./1104220f.spc', 'rb') as input:
    dummy = pickle.load(input)
dummy.name = file_name
dummy.path = file_list[index]
dummy.dir = dir_path
dummy.ischild = False
dummy.data = data
dummy.pass_num = 0
dummy.scan_dir = 2

# write .spc file
with open('D:/Code/2022oct/old2new/' + file_name + '.spc', 'wb') as output:
    pickle.dump(dummy, output, pickle.HIGHEST_PROTOCOL)  # Save data
