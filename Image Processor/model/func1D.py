# -*- coding: utf-8 -*-
"""
@Date     : 2021/4/5 15:20:29
@Author   : milier00
@FileName : func1D.py
"""
import numpy as np
from PyQt5.QtGui import QColor
from scipy.signal import medfilt
from scipy.ndimage import gaussian_filter1d
from scipy.ndimage import uniform_filter1d
from scipy.signal import savgol_filter
import colorcet as cc
from scipy.integrate import trapezoid
from math import sin, cos



class myFunc():

    def __init__(self):
        super().__init__()

    def load_dat(self, path):
        ''' This function read .dat file and return header, data, channels. '''
        header_dict = {}    # string dict for header
        with open(path, "r") as f:
            for line in f.readlines():
                line = line.strip('\n')
                if line[:6] == "[DATA]":
                    break
                if len(line.split('\t')) > 1:
                    header_dict[line.split('\t')[0]] = line.split('\t')[1]

        channels = []       # string list for channel names
        with open(path, "r") as f:
            for line in f.readlines()[18:19]:
                line = line.strip('\n')
                channels = line.split('\t')

        data = []           # 2D array for data
        with open(path, "r") as f:
            for line in f.readlines()[19:]:
                line = line.strip('\n')
                tmp = []
                for i in range(len(channels)):
                    tmp.append(float(line.split('\t')[i]))
                data.append(np.array(tmp))
        data = np.array(data)

        return header_dict, data, channels

    # def load_mat(self, path):
    #     ''' This function load .mat file and return header, data. '''
    #     mat = sio.loadmat(path)
    #
    #     header_dict = {}
    #     header_dict['grid_dim'] = mat['a']['grid_dim'][0][0][0].tolist()
    #     header_dict['grid_settings'] = mat['a']['grid_settings'][0][0].tolist()
    #     header_dict['filetype'] = mat['a']['filetype'][0][0].tolist()
    #     header_dict['sweep_signal'] = mat['a']['sweep_signal'][0][0].tolist()
    #     # header_dict['fixed_parameters'] = mat['a']['fixed_parameters'][0][0][0][0].tolist() + \
    #     #                                   mat['a']['fixed_parameters'][0][0][0][1].tolist()
    #     a = []
    #     for i in range(len(mat['a']['channels'][0][0][0])):
    #         a += mat['a']['channels'][0][0][0][i].tolist()
    #     header_dict['channels'] = a
    #
    #     data = mat['result']
    #     # print('func1D:', data.shape)   #(301, 24) (301, 65)
    #
    #     return header_dict, data

    def save_dat(self, path, data):
        channels = 'Bias (V)'
        cols = data.shape[1] - 1
        for i in range(cols):
            channels += '\tLI Demod 1 X [' + str(i).zfill(5) + '] (A)' + '\tLI Demod 1 X [' + str(i).zfill(5) + '] (A)'
        for i in range(data.shape[1] - 1, 0, -1):
            col = data[:, i]
            data = np.insert(data, i, values=col, axis=1)
        header = 'Experiment\t\nSaved Date\t\nUser\t\nDate\t\nX (m)\t\nY (m)\t\nZ (m)\t\nZ offset (m)\t\nSettling time (s)\t\nIntegration time (s)\t\nZ-Ctrl hold\t\nFinal Z (m)\t\nStart time\t\nFilter\t\nOrder\t\nCutoff frq\t\n\n[DATA]\n' + channels
        np.savetxt(path, data, header=header,delimiter='\t', comments='')

    def save_txt(self, path, data):

        channels = 'Bias (V)'
        cols = data.shape[0] - 1

        ### data : [(x, ch0_fwd, ch1_fwd, ch2_fwd, ch0_bwd, ch1_bwd, ch2_bwd)]
        if cols == 6:
            channels += '\tch0_fwd' + '\tch1_fwd' + '\tch2_fwd' +  '\tch0_bwd' + '\tch1_bwd' + '\tch2_bwd'

        ### data : [(x, ch0, ch1, ch2)]
        elif cols == 3:
            channels += '\tch0' + '\tch1' + '\tch2'

        elif cols == 1:
            channels += '\tch'

        header = channels
        np.savetxt(path, data.T, header=header, delimiter='\t', comments='')

    def make_fake(self, data):
        for i in range(1, data.shape[1] - 1):
            if i % 2 != 0:
                tmp = data[:, i + 1]
                data[:, i] = tmp
        return data

    def gaussian(self,x,amp,cen,wid):
        return amp*np.exp(-(x-cen)**2/wid)

    def gaussian2(self,x,amp1,cen1,wid1,amp2,cen2,wid2):
        return amp1 * np.exp(-(x - cen1) ** 2 / wid1)\
               +amp2 * np.exp(-(x - cen2) ** 2 / wid2)

    def gaussian3(self,x,amp1,cen1,wid1,amp2,cen2,wid2,amp3,cen3,wid3):
        return amp1 * np.exp(-(x - cen1) ** 2 / wid1) \
               + amp2 * np.exp(-(x - cen2) ** 2 / wid2) \
               + amp3 * np.exp(-(x - cen3) ** 2 / wid3)

    def gaussian4(self,x,amp1,cen1,wid1,amp2,cen2,wid2,amp3,cen3,wid3,\
                  amp4,cen4,wid4):
        return amp1 * np.exp(-(x - cen1) ** 2 / wid1) \
               + amp2 * np.exp(-(x - cen2) ** 2 / wid2) \
               + amp3 * np.exp(-(x - cen3) ** 2 / wid3) \
               + amp4 * np.exp(-(x - cen4) ** 2 / wid4)

    def gaussian5(self,x,amp1,cen1,wid1,amp2,cen2,wid2,amp3,cen3,wid3,\
                  amp4,cen4,wid4,amp5,cen5,wid5):
        return amp1 * np.exp(-(x - cen1) ** 2 / wid1) \
               + amp2 * np.exp(-(x - cen2) ** 2 / wid2) \
               + amp3 * np.exp(-(x - cen3) ** 2 / wid3) \
               + amp4 * np.exp(-(x - cen4) ** 2 / wid4) \
               + amp5 * np.exp(-(x - cen5) ** 2 / wid5)

    def lorentzian(self,x,amp,miu,sigma):
        return amp*sigma/((x-miu)**2+sigma**2)

    def lorentzian2(self, x, amp1, miu1, sigma1,amp2, miu2, sigma2):
        return amp1 * sigma1 / ((x - miu1) ** 2 + sigma1 ** 2)\
            +amp2 * sigma2 / ((x - miu2) ** 2 + sigma2 ** 2)

    def lorentzian3(self, x, amp1, miu1, sigma1,amp2, miu2, sigma2,\
                    amp3, miu3, sigma3):
        return amp1 * sigma1 / ((x - miu1) ** 2 + sigma1 ** 2)\
            +amp2 * sigma2 / ((x - miu2) ** 2 + sigma2 ** 2) \
            + amp3 * sigma3 / ((x - miu3) ** 2 + sigma3 ** 2)

    def lorentzian4(self, x, amp1, miu1, sigma1,amp2, miu2, sigma2,\
                    amp3, miu3, sigma3,amp4, miu4, sigma4):
        return amp1 * sigma1 / ((x - miu1) ** 2 + sigma1 ** 2)\
            +amp2 * sigma2 / ((x - miu2) ** 2 + sigma2 ** 2) \
            +amp3 * sigma3 / ((x - miu3) ** 2 + sigma3 ** 2) \
            +amp4 * sigma4 / ((x - miu4) ** 2 + sigma4 ** 2)

    def lorentzian5(self, x, amp1, miu1, sigma1,amp2, miu2, sigma2,\
                    amp3, miu3, sigma3,amp4, miu4, sigma4,amp5, miu5, sigma5):
        return amp1 * sigma1 / ((x - miu1) ** 2 + sigma1 ** 2)\
            +amp2 * sigma2 / ((x - miu2) ** 2 + sigma2 ** 2) \
            +amp3 * sigma3 / ((x - miu3) ** 2 + sigma3 ** 2) \
            +amp4 * sigma4 / ((x - miu4) ** 2 + sigma4 ** 2) \
            +amp5 * sigma5 / ((x - miu5) ** 2 + sigma5 ** 2)

    def moffat(self,x,amp,miu,sigma,beta):
        return amp*((x-miu)**2/sigma/sigma+1)**(-beta)

    def breitwigner(self,x,amp,miu,sigma,q):
        return amp*(q*sigma/2+x-miu)**2/((sigma/2)**2+(x-miu)**2)

    def smoothdata_movmean(self, data, factor):
        scale = 10/99
        size = int(factor*len(data)/100*scale)
        data = uniform_filter1d(data, size=size)
        return data

    def smoothdata_movmedian(self, data, factor):
        scale = 10 / 99
        size = int(factor*len(data)/100*scale) if (int(factor*len(data)/100*scale)%2) != 0 else int(factor*len(data)/100*scale)+1
        data = medfilt(data, kernel_size=size)
        return data

    def smoothdata_gaussian(self, data, factor):
        size = factor*.01*6
        data = gaussian_filter1d(data, sigma=size)
        return data

    def smoothdata_sgolay(self, data, factor):
        scale = 20/99
        size = int(factor*len(data)/100*scale) if (int(factor*len(data)/100*scale) % 2) != 0 else int(factor*len(data)/100*scale) + 1
        data = savgol_filter(data, size, 3)
        return data

    @property
    def parent_data_colors(self):
        parent_colors = []
        for color in cc.glasbey_dark:
            parent_colors.append(QColor(color))
        return parent_colors

    @property
    def processed_data_colors(self):
        processed_colors = []
        clist = reversed(cc.glasbey_dark)
        for color in clist:
            processed_colors.append(QColor(color))
        return processed_colors

    def do_int(self, x, y):
        int_y = [y[0]]
        for i in range(1, y.shape[0]):
            int_y.append(trapezoid(y[:i], x[:i]))
        int_y = np.array(int_y)
        return int_y

    def myrotate(self, x, y, deg):
        theta = np.deg2rad(deg)
        rot = np.array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
        newx = []
        newy = []
        for i in range(x.shape[0]):
            vec = np.array([x[i], y[i]])
            #         print('--',i,'--\n', vec)
            newxy = np.dot(rot, vec)
            #         print('--',i,'--\n', newxy)
            newx += [newxy[0]]
            newy += [newxy[1]]
        newx = np.array(newx);
        newy = np.array(newy)
        #     print(newx, '\n', newy)
        return newx, newy

# myf = myFunc()
# print(type(myf.moffat))
# xdata=np.linspace(-10,10,4000)
# y=myf.breitwigner(xdata,1,2,3,4)
# np.random.seed(1729)
# y_noise=0.1*np.random.normal(size=xdata.size)
# ydata=y+y_noise
# plt.plot(xdata,ydata,'b-')
# popt, pcov = curve_fit(myf.breitwigner,xdata,ydata)
# plt.plot(xdata,myf.breitwigner(xdata,*popt))
# plt.show()
# print(popt)
# print(pcov)