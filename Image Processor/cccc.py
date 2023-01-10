# -*- coding: utf-8 -*-
"""
@Date     : 1/1/2023 18:33:27
@Author   : milier00
@FileName : cccc.py
"""
""" find center elements of an ndarray """
import numpy as np
# x = np.random.randn(5,5)
# print(x)
#
# def get_middle(arr):
#     n = arr.shape[0] / 2.0
#     n_int = int(n)
#     if n % 2 == 1:
#         return arr[[n_int], [n_int]]
#     else:
#         return arr[n_int:n_int + 2, n_int:n_int + 2]
# print(get_middle(x))
""""""
"""kernel"""
kernel = np.array([[0, 1 / 144, -1 / 72, 1 / 144, 0],
                   [1 / 144, -1 / 18, 1 / 9, -1 / 18, 1 / 144],
                   [-1 / 72, 1 / 9, 7 / 9, 1 / 9, -1 / 72],
                   [1 / 144, -1 / 18, 1 / 9, -1 / 18, 1 / 144],
                   [0, 1 / 144, -1 / 72, 1 / 144, 0]])
b = [np.unravel_index(xy, kernel.shape) for xy in np.where(kernel.flatten() == 0)[0]]
a = [np.unravel_index(xy, kernel.shape) for xy in kernel.flatten().argsort()[:3][::-1]]

print(a)
""""""
coordinates = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5),              (0, 11), (0, 12), (0, 13), (0, 14), (0, 15), (0, 16),
               (1, 0), (1, 1), (1, 2), (1, 3),                                                (1, 13), (1, 14), (1, 15), (1, 16),
               (2, 0), (2, 1),                                                                                  (2, 15), (2, 16),
               (3, 0), (3, 1),                                                                                  (3, 15), (3, 16),
               (4, 0),                                                                                                   (4, 16),
               (5, 0),                                                                                                   (5, 16),

               (11, 0),                                                                                                  (11, 16),
               (12, 0),                                                                                                  (12, 16),
               (13, 0), (13, 1),                                                                               (13, 15), (13, 16),
               (14, 0), (14, 1),                                                                               (14, 15), (14, 16),
               (15, 0), (15, 1), (15, 2), (15, 3),                                         (15, 13), (15, 14), (15, 15), (15, 16),
               (16, 0), (16, 1), (16, 2), (16, 3), (16, 4), (16, 5),   (16, 11), (16, 12), (16, 13), (16, 14), (16, 15), (16, 16)]
""""""


corr = [ (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6),        (0, 13), (0, 14), (0, 15), (0, 16), (0, 17), (0, 18), (0, 19),
         (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),                                          (1, 15), (1, 16), (1, 17), (1, 18), (1, 19),
         (2, 0), (2, 1), (2, 2),                                                                            (2, 17), (2, 18), (2, 19),
         (3, 0), (3, 1),                                                                                             (3, 18), (3, 19),
         (4, 0), (4, 1),                                                                                             (4, 18), (4, 19),
         (5, 0),                                                                                                              (5, 19),
         (6, 0),                                                                                                              (6, 19),

         (13, 0),                                                                                                              (13, 19),
         (14, 0),                                                                                                              (14, 19),
         (15, 0), (15, 1),                                                                                           (15, 18), (15, 19),
         (16, 0), (16, 1),                                                                                           (16, 18), (16, 19),
         (17, 0), (17, 1), (17, 2),                                                                        (17, 17), (17, 18), (17, 19),
         (18, 0), (18, 1), (18, 2), (18, 3), (18, 4),                                  (18, 15), (18, 16), (18, 17), (18, 18), (18, 19),
         (19, 0), (19, 1), (19, 2), (19, 3), (19, 4), (19, 5), (19, 6), (19, 13), (19, 14), (19, 15), (19, 16), (19, 17), (19, 18), (19, 19)]



import numpy as np
from math import floor
import copy

def smooth_sts_mapping(img, max, min):
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

a = np.random.randint(0,100,(8,8))
print(a.shape)
b = smooth_sts_mapping(a, 0.1, 0.1)
print(a)
print(b)