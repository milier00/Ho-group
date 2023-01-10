# -*- coding: utf-8 -*-
"""
@Date     : 1/3/2023 17:52:07
@Author   : milier00
@FileName : touteng.py
"""
from Data import SpcData
from matplotlib import pyplot as plt
""" Test average child partially """
spc = SpcData('D:/Code/2022oct/spc/testttt\\1105220c.spc')# 1 1 4 196 1 1 / 0 1 4 196 1 0
print(spc.pass_num, spc.pt_num, spc.ch_num, spc.dat_num, spc.scan_dir, len(spc.child))    # 10 4 4 436 2
show_fb = True
del_pass = [[1],[1,2,3,4,5,6,7],[],[1,2,3,4,5,6,7,8,9]]
pack = spc.avg_child_part(show_fb, del_pass)

plt.plot(pack[0][2][0], pack[0][2][1], label='pt#'+str(1))
plt.plot(pack[3][2][0], pack[3][2][1], label='pt#'+str(4))
plt.legend()
plt.show()
