# -*- coding: utf-8 -*-
"""
@Date     : 2021/4/12 17:17:48
@Author   : milier00
@FileName : func2D.py
"""
from math import floor
import numpy as np
import copy
# from scipy.io import savemat
import os
from scipy.ndimage import rotate

class myFunc():

    def __init__(self):
        super().__init__()

    #converted from smooth_sts_mapping.m, displayed name is delete bad point
    def smooth_sts_mapping(self, sts, max, min):
        (x, y) = sts.shape
        s = sts
        max_smooth_num = floor(x*y*max)     # num of maximum points to be smoothed
        min_smooth_num = floor(x*y*min)     # num of minimum points to be smoothed

        # for max values
        for j1 in range(max_smooth_num):
            x1 = 0
            y1 = 0
            temp = s[0, 0]
            """ 遍历全部点，找到最大值点，值为temp, 坐标为(x1,y1) """
            for xx in range(x):
                for yy in range(y):
                    if s[xx, yy] >= temp:
                        x1 = xx
                        y1 = yy
                        temp = s[xx, yy]
            """ 如果该点在角上，用最近邻两个边上的点平均值替代
                如果该点在边上，用最近邻三个点平均值替代
                如果该点在中心，用最近邻四个点平均值替代 """
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

    def delete_bad_point(self, img, max, min):
        """ rewrite version of smooth_sts_mapping
            average max and min points determined at the beginning
            faster than old version
        """
        tmp = copy.deepcopy(img)
        max_num = floor(img.shape[0] * img.shape[1] * max)  # num of maximum points to be smoothed
        min_num = floor(img.shape[0] * img.shape[1] * min)  # num of minimum points to be smoothed
        max_indices = [np.unravel_index(xy, img.shape) for xy in img.flatten().argsort()[-max_num:][::-1]]
        min_indices = [np.unravel_index(xy, img.shape) for xy in img.flatten().argsort()[:min_num][::-1]]
        indices = max_indices + min_indices

        for xy in indices:
            if ((xy[0] == 0) + (xy[0] == img.shape[0] - 1)) * ((xy[1] == 0) + (xy[1] == img.shape[1] - 1)):
                tmp[xy] = (img[xy[0] + 1 if xy[0] == 0 else xy[0] - 1, xy[1]] + img[
                    xy[0], xy[1] + 1 if xy[1] == 0 else xy[1] - 1]) / 2
            elif ((xy[0] == 0) + (xy[0] == img.shape[0] - 1)) * ((xy[1] != 0) * (xy[1] != img.shape[1] - 1)):
                tmp[xy] = (img[xy[0], xy[1] + 1] + img[xy[0], xy[1] - 1]) / 2
            elif ((xy[0] != 0) * (xy[0] != img.shape[0] - 1)) * ((xy[1] == 0) + (xy[1] == img.shape[1] - 1)):
                tmp[xy] = (img[xy[0] - 1, xy[1]] + img[xy[0] + 1, xy[1]]) / 2
            else:
                tmp[xy] = (img[xy[0], xy[1] + 1] + img[xy[0], xy[1] - 1] + img[xy[0] - 1, xy[1]] + img[
                    xy[0] + 1, xy[1]]) / 4

        return tmp

    def delete_bad_point2(self, img, max, min):
        """
            this one replace all bad points with global mean
        """
        tmp = copy.deepcopy(img)
        max_num = floor(img.shape[0] * img.shape[1] * max)  # num of maximum points to be smoothed
        min_num = floor(img.shape[0] * img.shape[1] * min)  # num of minimum points to be smoothed
        max_indices = [np.unravel_index(xy, img.shape) for xy in img.flatten().argsort()[-max_num:][::-1]]
        min_indices = [np.unravel_index(xy, img.shape) for xy in img.flatten().argsort()[:min_num][::-1]]
        indices = max_indices + min_indices

        for xy in indices:
            tmp[xy] = np.average(img)

        return tmp

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






