# -*- coding: utf-8 -*-
"""
@Date     : 2021/4/12 17:17:48
@Author   : milier00
@FileName : func2D.py
"""
from math import floor
import numpy as np
import copy
from scipy.io import savemat
import os
from scipy.ndimage import rotate

class myFunc():

    def __init__(self):
        super().__init__()

    # save MappingResult data from processed list
    def save_mat(self, path, data):
        parent_header = data.parent_data.header
        parent_name = data.parent_data.name
        parent_path = data.parent_data.path
        dir, file = os.path.split(path)
        name = file
        result = np.swapaxes(data.result, 0, 2)
        result = np.swapaxes(result, 0, 1)
        # dict2save = {'parent_header': parent_header, 'parent_name': parent_name, 'parent_path': parent_path,\
        #         'name':name, 'result': result}
        dict2save = {'parent_name': parent_name, 'parent_path': parent_path, 'name':name, 'result': result}
        savemat(path, dict2save, long_field_names=True)

    # converted from smooth_sts_mapping.m, displayed name is delete bad point
    def smooth_sts_mapping(self, sts, max, min):
        (x, y) = sts.shape
        s = sts * 1e12
        max_smooth_num = floor(x*y*max)
        min_smooth_num = floor(x*y*min)

        # for max values
        for j1 in range(max_smooth_num):
            x1 = 0
            y1 = 0
            temp = s[0, 0]
            for xx in range(x):
                for yy in range(y):
                    if s[xx, yy] >= temp:
                        x1 = xx
                        y1 = yy
                        temp = s[xx, yy]
            if x1 == 0 and y1 == 0:
                s[0, 0] = s[0, 1]*.5 + s[1, 0]*.5
            elif x1 == 0 and y1 == y-1:
                s[0, y1] = s[0, y1-1]*.5 + s[1, y1]*.5
            elif x1 == x-1 and y1 == 0:
                s[x1, 0] = s[x1-1, 0]*.5 + s[x1, 1]*.5
            elif x1 == x-1 and y1 == y-1:
                s[x1, y1] = s[x-2, y-1]*.5 + s[x-1, y-2]*.5
            elif x1 == 0 and y1 != 0 and y1 != y-1:
                s[0, y1] = s[0, y1-1]/3 + s[0, y1+1]/3 + s[1, y1]/3
            elif x1 == x-1 and y1 != 0 and y1 != y-1:
                s[x1, y1] = s[x-1, y1-1]/3 + s[x-1, y1+1]/3 + s[x1-1, y1]/3
            elif y1 == 0 and x1 != 0 and x1 != x-1:
                s[x1, y1] = s[x1-1, y1]/3 + s[x1+1, y1]/3 + s[x1, y1+1]/3
            elif y1 == y-1 and x1 != 0 and x1 != x-1:
                s[x1, y1] = s[x1-1, y1]/3 + s[x1+1, y1]/3 + s[x1, y1-1]/3
            else:
                s[x1, y1] = s[x1 - 1, y1] / 4 + s[x1 + 1, y1] / 4 + s[x1, y1 - 1] / 4 + s[x1, y1+1]/4

        # for min values
        for j1 in range(min_smooth_num):
            x1 = 0
            y1 = 0
            temp = s[0, 0]
            for xx in range(x):
                for yy in range(y):
                    if s[xx, yy] <= temp:
                        x1 = xx
                        y1 = yy
                        temp = s[xx, yy]
            if x1 == 0 and y1 == 0:
                s[0, 0] = s[0, 1]*.5 + s[1, 0]*.5
            elif x1 == 0 and y1 == y-1:
                s[0, y1] = s[0, y1-1]*.5 + s[1, y1]*.5
            elif x1 == x-1 and y1 == 0:
                s[x1, 0] = s[x1-1, 0]*.5 + s[x1, 1]*.5
            elif x1 == x-1 and y1 == y-1:
                s[x1, y1] = s[x-2, y-1]*.5 + s[x-1, y-2]*.5
            elif x1 == 0 and y1 != 0 and y1 != y-1:
                s[0, y1] = s[0, y1-1]/3 + s[0, y1+1]/3 + s[1, y1]/3
            elif x1 == x-1 and y1 != 0 and y1 != y-1:
                s[x1, y1] = s[x-1, y1-1]/3 + s[x-1, y1+1]/3 + s[x1-1, y1]/3
            elif y1 == 0 and x1 != 0 and x1 != x-1:
                s[x1, y1] = s[x1-1, y1]/3 + s[x1+1, y1]/3 + s[x1, y1+1]/3
            elif y1 == y-1 and x1 != 0 and x1 != x-1:
                s[x1, y1] = s[x1-1, y1]/3 + s[x1+1, y1]/3 + s[x1, y1-1]/3
            else:
                s[x1, y1] = s[x1 - 1, y1] / 4 + s[x1 + 1, y1] / 4 + s[x1, y1 - 1] / 4 + s[x1, y1+1]/4

        return s

    # converted from grid2mat.m, displayed name is open grid
    def grid2mat(self, path):
        grid = nap.read.Grid(path)
        channels = grid.header['channels']
        size = grid.signals[channels[0]].shape
        bias = grid.signals['sweep_signal']
        cluster = grid.signals[channels[0]].reshape((size[0] * size[1], size[2]))
        for i in range(1, len(channels)):
            cluster = np.dstack((cluster, grid.signals[channels[i]].reshape((size[0] * size[1], size[2]))))

        fake_header = copy.deepcopy(grid.header)
        fake_header['grid_dim'] = [[[grid.header['dim_px']]]]
        fake_header['grid_settings'] = [[grid.header['pos_xy'] + grid.header['size_xy'] + [grid.header['angle']]]]
        fake_header['filetype'] = [[grid.header['Filetype']]]
        fake_header['sweep_signal'] = [[grid.header['sweep_signal']]]
        fake_header['channels'] = [[grid.header['channels']]]
        for i in range(cluster.shape[0]):
            data = np.insert(cluster[i], 0, bias, axis=1)
            dict2save = {'a': fake_header, 'result': data}
            savemat(path[:-4] + '---' + str(i).zfill(5) + '.mat', dict2save)

    # converted from symmetry.m, displayed name is symmetry
    def symmetry(self, data, order):
        p1 = copy.deepcopy(data)
        if order == 2:
            p2 = rotate(data, 180, reshape=False, mode='nearest')
            result = (p1+p2)/2
        elif order == 3:
            p2 = rotate(data, 120, reshape=False, mode='nearest')
            p3 = rotate(data, 240, reshape=False, mode='nearest')
            result = (p1+p2+p3)/3
        elif order == 4:
            p2 = rotate(data, 90, reshape=False, mode='nearest')
            p3 = rotate(data, 180, reshape=False, mode='nearest')
            p4 = rotate(data, 270, reshape=False, mode='nearest')
            result = (p1+p2+p3+p4)/4
        elif order == 5:
            p2 = rotate(data, 72, reshape=False, mode='nearest')
            p3 = rotate(data, 144, reshape=False, mode='nearest')
            p4 = rotate(data, 216, reshape=False, mode='nearest')
            p5 = rotate(data, 288, reshape=False, mode='nearest')
            result = (p1+p2+p3+p4+p5)/5
        elif order == 6:
            p2 = rotate(data, 60, reshape=False, mode='nearest')
            p3 = rotate(data, 120, reshape=False, mode='nearest')
            p4 = rotate(data, 180, reshape=False, mode='nearest')
            p5 = rotate(data, 240, reshape=False, mode='nearest')
            p6 = rotate(data, 300, reshape=False, mode='nearest')
            result = (p1+p2+p3+p4+p5+p6)/6
        return result

    # joint density of state
    def jdos(self, matrix):
        (x, y) = matrix.shape
        jdos = np.zeros((2 * x - 1, 2 * y - 1))
        temp = np.zeros((x, y))
        avg = np.average(matrix)
        for i in range(x):
            for j in range(y):
                if matrix[i, j] < avg * .01:
                    continue
                else:
                    temp = matrix[i, j] * matrix
                    jdos[x - i - 1:2 * x - i - 1, y - j - 1:2 * y - j - 1] = jdos[x - i - 1:2 * x - i - 1,
                                                                             y - j - 1:2 * y - j - 1] + temp
        jdos[x - 1, y - 1] = 0
        return jdos





