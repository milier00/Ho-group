# -*- coding: utf-8 -*-
"""
@Date     : 2021/1/9 19:59:25
@Author   : milier00
@FileName : image.py
"""
import copy
import sys
from matplotlib.colors import LinearSegmentedColormap
from PyQt5.QtWidgets import QWidget
import numpy as np
import pickle
from matplotlib import cm
from numpy import genfromtxt
import matplotlib.colors as colors
from PIL import Image
import pyqtgraph as pg
import cv2 as cv

class myImages(QWidget):
    colormap_dict_name = {0: 'viridis', 1: 'plasma', 2: 'inferno', 3: 'magma', 4: 'cividis', 5: 'Greys',
                        6: 'Purples', 7: 'Blues', 8: 'Greens', 9: 'Oranges', 10: 'Reds', 11: 'YlOrBr',
                        12: 'YlOrRd', 13: 'OrRd', 14: 'PuRd', 15: 'RdPu', 16: 'BuPu', 17: 'GnBu',
                        18: 'PuBu', 19: 'YlGnBu', 20: 'PuBuGn', 21: 'BuGn', 22: 'YlGn', 23: 'binary',
                        24: 'gist_yarg', 25: 'gist_gray', 26: 'gray', 27: 'bone', 28: 'pink', 29: 'spring',
                        30: 'summer', 31: 'autumn', 32: 'winter', 33: 'cool', 34: 'Wistia', 35: 'hot',
                        36: 'afmhot', 37: 'gist_heat', 38: 'copper', 39: 'PiYG', 40: 'PRGn', 41: 'BrBG',
                        42: 'PuOr', 43: 'RdGy', 44: 'RdBu', 45: 'RdYlBu', 46: 'RdYlGn', 47: 'Spectral',
                        48: 'coolwarm', 49: 'bwr', 50: 'seismic', 51: 'twilight', 52: 'twilight_shifted',
                        53: 'hsv', 54: 'Pastel1', 55: 'Pastel2', 56: 'Paired', 57: 'Accent', 58: 'Dark2',
                        59: 'Set1', 60: 'Set2', 61: 'Set3', 62: 'tab10', 63: 'tab20', 64: 'tab20b',
                        65: 'tab20c', 66: 'flag', 67: 'prism', 68: 'ocean', 69: 'gist_earth',
                        70: 'terrain', 71: 'gist_stern', 72: 'gnuplot', 73: 'gnuplot2', 74: 'CMRmap',
                        75: 'cubehelix', 76: 'brg', 77: 'gist_rainbow', 78: 'rainbow', 79: 'jet', 80: 'turbo',
                        81: 'nipy_spectral', 82: 'gist_ncar'}
    with open(r"./model/RRAINBOW.CMAP", 'rb') as input:
        rrainbow = pickle.load(input)

    colormap_dict_cm = {
                     0: pg.colormap.get('viridis', source='matplotlib'), 1: pg.colormap.get('plasma', source='matplotlib'),
                     2: pg.colormap.get('inferno', source='matplotlib'), 3: pg.colormap.get('magma', source='matplotlib'),
                     4: pg.colormap.get('cividis', source='matplotlib'),

                     5: pg.colormap.get('Greys', source='matplotlib'), 6: pg.colormap.get('Purples', source='matplotlib'),
                     7: pg.colormap.get('Blues', source='matplotlib'), 8: pg.colormap.get('Greens', source='matplotlib'),
                     9: pg.colormap.get('Oranges', source='matplotlib'), 10: pg.colormap.get('Reds', source='matplotlib'),
                     11: pg.colormap.get('YlOrBr', source='matplotlib'), 12: pg.colormap.get('YlOrRd', source='matplotlib'),
                     13: pg.colormap.get('OrRd', source='matplotlib'), 14: pg.colormap.get('PuRd', source='matplotlib'),
                     15: pg.colormap.get('RdPu', source='matplotlib'), 16: pg.colormap.get('BuPu', source='matplotlib'),
                     17: pg.colormap.get('GnBu', source='matplotlib'), 18: pg.colormap.get('PuBu', source='matplotlib'),
                     19: pg.colormap.get('YlGnBu', source='matplotlib'), 20: pg.colormap.get('PuBuGn', source='matplotlib'),
                     21: pg.colormap.get('BuGn', source='matplotlib'), 22: pg.colormap.get('YlGn', source='matplotlib'),

                     23: pg.colormap.get('binary', source='matplotlib'), 24: pg.colormap.get('gist_yarg', source='matplotlib'),
                     25: pg.colormap.get('gist_gray', source='matplotlib'), 26: pg.colormap.get('gray', source='matplotlib'),
                     27: pg.colormap.get('bone', source='matplotlib'), 28: pg.colormap.get('pink', source='matplotlib'),
                     29: pg.colormap.get('spring', source='matplotlib'), 30: pg.colormap.get('summer', source='matplotlib'),
                     31: pg.colormap.get('autumn', source='matplotlib'), 32: pg.colormap.get('winter', source='matplotlib'),
                     33: pg.colormap.get('cool', source='matplotlib'), 34: pg.colormap.get('Wistia', source='matplotlib'),
                     35: pg.colormap.get('hot', source='matplotlib'), 36: pg.colormap.get('afmhot', source='matplotlib'),
                     37: pg.colormap.get('gist_heat', source='matplotlib'), 38: pg.colormap.get('copper', source='matplotlib'),

                     39: pg.colormap.get('PiYG', source='matplotlib'), 40: pg.colormap.get('PRGn', source='matplotlib'),
                     41: pg.colormap.get('BrBG', source='matplotlib'), 42: pg.colormap.get('PuOr', source='matplotlib'),
                     43: pg.colormap.get('RdGy', source='matplotlib'), 44: pg.colormap.get('RdBu', source='matplotlib'),
                     45: pg.colormap.get('RdYlBu', source='matplotlib'), 46: pg.colormap.get('RdYlGn', source='matplotlib'),
                     47: pg.colormap.get('Spectral', source='matplotlib'), 48: pg.colormap.get('coolwarm', source='matplotlib'),
                     49: pg.colormap.get('bwr', source='matplotlib'), 50: pg.colormap.get('seismic', source='matplotlib'),

                     51: pg.colormap.get('twilight', source='matplotlib'), 52: pg.colormap.get('twilight_shifted', source='matplotlib'),
                     53: pg.colormap.get('hsv', source='matplotlib'),

                     54: pg.colormap.get('Pastel1', source='matplotlib'), 55: pg.colormap.get('Pastel2', source='matplotlib'),
                     56: pg.colormap.get('Paired', source='matplotlib'), 57: pg.colormap.get('Accent',source='matplotlib'),
                     58: pg.colormap.get('Dark2', source='matplotlib'), 59: pg.colormap.get('Set1', source='matplotlib'),
                     60: pg.colormap.get('Set2', source='matplotlib'), 61: pg.colormap.get('Set3', source='matplotlib'),
                     62: pg.colormap.get('tab10', source='matplotlib'), 63: pg.colormap.get('tab20', source='matplotlib'),
                     64: pg.colormap.get('tab20b', source='matplotlib'), 65: pg.colormap.get('tab20c', source='matplotlib'),

                     66: pg.colormap.get('flag', source='matplotlib'), 67: pg.colormap.get('prism', source='matplotlib'),
                     68: pg.colormap.get('ocean', source='matplotlib'), 69: pg.colormap.get('gist_earth', source='matplotlib'),
                     70: pg.colormap.get('terrain', source='matplotlib'), 71: pg.colormap.get('gist_stern', source='matplotlib'),
                     72: pg.colormap.get('gnuplot', source='matplotlib'), 73: pg.colormap.get('gnuplot2', source='matplotlib'),
                     74: pg.colormap.get('CMRmap', source='matplotlib'), 75: pg.colormap.get('cubehelix', source='matplotlib'),
                     76: pg.colormap.get('brg', source='matplotlib'),

                     77: pg.colormap.get('gist_rainbow', source='matplotlib'), 78: pg.colormap.get('rainbow', source='matplotlib'),
                     79: pg.colormap.get('jet', source='matplotlib'), 80: pg.colormap.get('turbo', source='matplotlib'),
                     81: pg.colormap.get('nipy_spectral', source='matplotlib'), 82: pg.colormap.get('gist_ncar', source='matplotlib'),
                     83: rrainbow
                    }



    def __init__(self):
        super().__init__()

    #
    # color -> gray
    #
    def color2gray(self, img):
        # img = cv.imread(path)
        # img = cv.resize(img, dsize=(440, 440))
        # cv.imshow('read_img',img)
        gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # cv.imshow('gray_img', gray_img)
        psudo_gray_img = cv.cvtColor(gray_img, cv.COLOR_GRAY2BGR)
        # cv.imshow('psudo_gray_img', psudo_gray_img)
        # cv.imwrite('..\data\scan_example_gray.jpg', psudo_gray_img)
        # cv.waitKey(0)
        # cv.destroyAllWindows()
        return psudo_gray_img

    #
    # gray -> color
    #
    def gray2color(self, img):
        # img = cv.imread(path)
        img = cv.resize(img, dsize=(440, 440))
        # cv.imshow('read_img',img)
        # img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # img=cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
        img = cv.applyColorMap(img, 5)
        # cv.imshow('color_img', img)
        # cv.waitKey(0)
        # cv.destroyAllWindows()
        return img
    #
    # gray -> reversed
    #
    def gray2reverse(self, img):
        # img = cv.imread(path, 0)
        img = self.hist_normalization(img)
        height, width = img.shape
        dst = np.zeros((height, width), np.uint8)
        for i in range(height):
            for j in range(width):
                dst[i, j] = 255-img[i,j]
        # cv.imwrite('..\data\scan_example_reverse.png', dst)
        # cv.imshow('img',img)
        # cv.imshow('dst',dst)
        # cv.waitKey()
        return dst

    #
    # color -> reversed
    #
    def color2reverse(self, path):
        img = cv.imread(path, 1)
        cha = img.shape
        height, width, deep = cha
        dst = np.zeros((height, width, 3), np.uint8)
        for i in range(height):
            for j in range(width):
                b, g, r = img[i, j]
                dst[i, j] = (255-b, 255-g, 255-r)
        # cv.imshow('img', img)
        # cv.imshow('dst', dst)
        # cv.waitKey()
        return dst
    #
    # gray --> scharr operator --> diff
    #
    def illuminated(self, img):
        # img = cv.imread(path)
        img = self.hist_normalization(img)
        # scharr operator
        scharrx = cv.Scharr(img, cv.CV_64F, 1, 0)
        scharry = cv.Scharr(img, cv.CV_64F, 0, 1)
        scharrx = cv.convertScaleAbs(scharrx)
        scharry = cv.convertScaleAbs(scharry)
        scharrxy = cv.addWeighted(scharrx, 0.5, scharry, 0.5, 0)
        # cv.imwrite('..\data\scan_example_illuminated.png', scharrxy)
        # res = np.hstack((img, scharrx, scharry, scharrxy))
        # cv.imshow(res, 'res')
        # cv.waitKey()
        # cv.destroyAllWindows()
        return scharrxy

    #
    # gray -> plane fit
    #
    #
    # gray -> plane fit
    #
    def plane_fit(self, img):
        x = np.array([[i + 1] * img.shape[0] for i in range(img.shape[0])]).flatten()
        y = np.array(list(np.arange(img.shape[1]) + 1) * img.shape[1])
        z = img.flatten()

        # Create coefficient matrix A
        A = np.zeros((3, 3))
        for i in range(0, img.size):
            A[0, 0] = A[0, 0] + x[i] ** 2
            A[0, 1] = A[0, 1] + x[i] * y[i]
            A[0, 2] = A[0, 2] + x[i]
            A[1, 0] = A[0, 1]
            A[1, 1] = A[1, 1] + y[i] ** 2
            A[1, 2] = A[1, 2] + y[i]
            A[2, 0] = A[0, 2]
            A[2, 1] = A[1, 2]
            A[2, 2] = img.size

        # Create B
        b = np.zeros((3, 1))
        for i in range(0, img.size):
            b[0, 0] = b[0, 0] + x[i] * z[i]
            b[1, 0] = b[1, 0] + y[i] * z[i]
            b[2, 0] = b[2, 0] + z[i]

        # Solving x
        A_inv = np.linalg.inv(A)
        X = np.dot(A_inv, b)

        # Calculate variance
        R = 0
        for i in range(0, img.size):
            R = R + (X[0, 0] * x[i] + X[1, 0] * y[i] + X[2, 0] - z[i]) ** 2

        x_p = np.linspace(1, img.shape[0] + 1, 100)
        y_p = np.linspace(1, img.shape[1] + 1, 100)
        x_p, y_p = np.meshgrid(x_p, y_p)

        new_z = X[0, 0] * x + X[1, 0] * y + X[2, 0] + np.min(img)
        new_z = z - new_z
        new_z = np.reshape(new_z, (img.shape[0], img.shape[1])).astype(np.float32)

        new_z = self.hist_normalization(new_z)
        return new_z

    # histogram normalization
    def hist_normalization(self, img, a=0, b=255):
        # get max and min
        c = img.min()
        d = img.max()
        out = img.copy()
        # normalization
        out = (b - a) / (d - c) * (out - c) + a
        out[out < a] = a
        out[out > b] = b
        out = out.astype(np.uint8)
        return out

    def prepare_data(self, tmp):
        array = copy.deepcopy(tmp)

        xmax = max(map(max, array))
        xmin = min(map(min, array))
        # print(xmax, xmin)
        if xmax-xmin != 0:
            for i in range(array.shape[0]):
                for j in range(array.shape[1]):
                    array[i][j] = (array[i][j] - xmin) / (xmax - xmin)
        array = array.astype(np.float32)
        # print("prepare data:", array.max(), array.min())
        return array

    # Replace -1 with minimum data for load display
    def partial_renormalize(self, data):
        a = copy.deepcopy(data)
        b= []
        for corr in np.argwhere(a != -1):
            b.append(a[corr[0], corr[1]])
        minimum = np.min(b)
        for corr in np.argwhere(a == -1):
            a[corr[0], corr[1]] = minimum
        return a

    def read_csv(self, path):
        g = open(path, 'r')
        temp = genfromtxt(g, delimiter=',')
        im = Image.fromarray(temp).convert('RGB')
        pix = im.load()
        rows, cols = im.size
        for x in range(cols):
            for y in range(rows):
                print
                str(x) + " " + str(y)
                pix[x, y] = (int(temp[y, x] // 256 // 256 % 256), int(temp[y, x] // 256 % 256), int(temp[y, x] % 256))
        im.save(g.name[0:-4] + '.jpeg')
        # img = cv.imread(g.name[0:-4] + '.jpeg')
        # img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # img = np.reshape(img, (1, rows, cols))
        # data = pd.DataFrame(data=img.tolist())
        # data.to_csv('../data/real_stm_img_.csv',header=False)
        # print(img.shape)

    # RGB to HEX
    def RGB_to_Hex(self, rgb):
        color = '#'
        for i in rgb[0:3]:
            num = int(i)
            color += str(hex(num))[-2:].replace('x', '0').upper()
        return color

    # HEX to RGB
    def Hex_to_RGB(hex):
        r = int(hex[1:3], 16)
        g = int(hex[3:5], 16)
        b = int(hex[5:7], 16)
        rgb = str(r) + ',' + str(g) + ',' + str(b)
        print(rgb)
        return rgb

    def upsampling(self, img, up_height, up_width):
        height, width, channels = img.shape
        emptyImage = np.zeros((up_width, up_height, channels), np.uint8)
        sh = up_height / height
        sw = up_width / width
        for i in range(up_width):
            for j in range(up_height):
                x = int(i / sh)
                y = int(j / sw)
                emptyImage[i, j] = img[x, y]
        return emptyImage

    # color -> colormap
    def color_map(self, img, index):
        if index == 0:
            img = np.uint8(cm.viridis(img) * 255)
        elif index == 1:
            img = np.uint8(cm.plasma(img) * 255)
        elif index == 2:
            img = np.uint8(cm.inferno(img) * 255)
        elif index == 3:
            img = np.uint8(cm.magma(img) * 255)
        elif index == 4:
            img = np.uint8(cm.cividis(img) * 255)
        elif index == 5:
            img = np.uint8(cm.Greys(img) * 255)
        elif index == 6:
            img = np.uint8(cm.Purples(img) * 255)
        elif index == 7:
            img = np.uint8(cm.Blues(img) * 255)
        elif index == 8:
            img = np.uint8(cm.Greens(img) * 255)
        elif index == 9:
            img = np.uint8(cm.Oranges(img) * 255)
        elif index == 10:
            img = np.uint8(cm.Reds(img) * 255)
        elif index == 11:
            img = np.uint8(cm.YlOrBr(img) * 255)
        elif index == 12:
            img = np.uint8(cm.YlOrRd(img) * 255)
        elif index == 13:
            img = np.uint8(cm.OrRd(img) * 255)
        elif index == 14:
            img = np.uint8(cm.PuRd(img) * 255)
        elif index == 15:
            img = np.uint8(cm.RdPu(img) * 255)
        elif index == 16:
            img = np.uint8(cm.BuPu(img) * 255)
        elif index == 17:
            img = np.uint8(cm.GnBu(img) * 255)
        elif index == 18:
            img = np.uint8(cm.PuBu(img) * 255)
        elif index == 19:
            img = np.uint8(cm.YlGnBu(img) * 255)
        elif index == 20:
            img = np.uint8(cm.PuBuGn(img) * 255)
        elif index == 21:
            img = np.uint8(cm.BuGn(img) * 255)
        elif index == 22:
            img = np.uint8(cm.YlGn(img) * 255)
        elif index == 23:
            img = np.uint8(cm.binary(img) * 255)
        elif index == 24:
            img = np.uint8(cm.gist_yarg(img) * 255)
        elif index == 25:
            img = np.uint8(cm.gist_gray(img) * 255)
        elif index == 26:
            img = np.uint8(cm.gray(img) * 255)
        elif index == 27:
            img = np.uint8(cm.bone(img) * 255)
        elif index == 28:
            img = np.uint8(cm.pink(img) * 255)
        elif index == 29:
            img = np.uint8(cm.spring(img) * 255)
        elif index == 30:
            img = np.uint8(cm.summer(img) * 255)
        elif index == 31:
            img = np.uint8(cm.autumn(img) * 255)
        elif index == 32:
            img = np.uint8(cm.winter(img) * 255)
        elif index == 33:
            img = np.uint8(cm.cool(img) * 255)
        elif index == 34:
            img = np.uint8(cm.Wistia(img) * 255)
        elif index == 35:
            img = np.uint8(cm.hot(img) * 255)
        elif index == 36:
            img = np.uint8(cm.afmhot(img) * 255)
        elif index == 37:
            img = np.uint8(cm.gist_heat(img) * 255)
        elif index == 38:
            img = np.uint8(cm.copper(img) * 255)
        elif index == 39:
            img = np.uint8(cm.PiYG(img) * 255)
        elif index == 40:
            img = np.uint8(cm.PRGn(img) * 255)
        elif index == 41:
            img = np.uint8(cm.BrBG(img) * 255)
        elif index == 42:
            img = np.uint8(cm.PuOr(img) * 255)
        elif index == 43:
            img = np.uint8(cm.RdGy(img) * 255)
        elif index == 44:
            img = np.uint8(cm.RdBu(img) * 255)
        elif index == 45:
            img = np.uint8(cm.RdYlBu(img) * 255)
        elif index == 46:
            img = np.uint8(cm.RdYlGn(img) * 255)
        elif index == 47:
            img = np.uint8(cm.Spectral(img) * 255)
        elif index == 48:
            img = np.uint8(cm.coolwarm(img) * 255)
        elif index == 49:
            img = np.uint8(cm.bwr(img) * 255)
        elif index == 50:
            img = np.uint8(cm.seismic(img) * 255)
        elif index == 51:
            img = np.uint8(cm.twilight(img) * 255)
        elif index == 52:
            img = np.uint8(cm.twilight_shifted(img) * 255)
        elif index == 53:
            img = np.uint8(cm.hsv(img) * 255)
        elif index == 54:
            img = np.uint8(cm.Pastel1(img) * 255)
        elif index == 55:
            img = np.uint8(cm.Pastel2(img) * 255)
        elif index == 56:
            img = np.uint8(cm.Paired(img) * 255)
        elif index == 57:
            img = np.uint8(cm.Accent(img) * 255)
        elif index == 58:
            img = np.uint8(cm.Dark2(img) * 255)
        elif index == 59:
            img = np.uint8(cm.Set1(img) * 255)
        elif index == 60:
            img = np.uint8(cm.Set2(img) * 255)
        elif index == 61:
            img = np.uint8(cm.Set3(img) * 255)
        elif index == 62:
            img = np.uint8(cm.tab10(img) * 255)
        elif index == 63:
            img = np.uint8(cm.tab20(img) * 255)
        elif index == 64:
            img = np.uint8(cm.tab20b(img) * 255)
        elif index == 65:
            img = np.uint8(cm.tab20c(img) * 255)
        elif index == 66:
            img = np.uint8(cm.flag(img) * 255)
        elif index == 67:
            img = np.uint8(cm.prism(img) * 255)
        elif index == 68:
            img = np.uint8(cm.ocean(img) * 255)
        elif index == 69:
            img = np.uint8(cm.gist_earth(img) * 255)
        elif index == 70:
            img = np.uint8(cm.terrain(img) * 255)
        elif index == 71:
            img = np.uint8(cm.gist_stern(img) * 255)
        elif index == 72:
            img = np.uint8(cm.gnuplot(img) * 255)
        elif index == 73:
            img = np.uint8(cm.gnuplot2(img) * 255)
        elif index == 74:
            img = np.uint8(cm.CMRmap(img) * 255)
        elif index == 75:
            img = np.uint8(cm.cubehelix(img) * 255)
        elif index == 76:
            img = np.uint8(cm.brg(img) * 255)
        elif index == 77:
            img = np.uint8(cm.gist_rainbow(img) * 255)
        elif index == 78:
            img = np.uint8(cm.rainbow(img) * 255)
        elif index == 79:
            img = np.uint8(cm.jet(img) * 255)
        elif index == 80:
            img = np.uint8(cm.turbo(img) * 255)
        elif index == 81:
            img = np.uint8(cm.nipy_spectral(img) * 255)
        elif index == 82:
            img = np.uint8(cm.gist_ncar(img) * 255)
        elif index == 83:
            self.ho_rainbow()
            img = np.uint8(self.rrainbow_cm(img) * 255)
        return img

    def mycolormap(self):
        cdict  = [(0, 0, 128), (0, 0, 255), (0, 255, 255), (255, 255, 0), (255, 0, 0), (128, 0, 0)]
        return colors.ListedColormap(cdict, 'indexed')

    def ho_rainbow(self):
        color_list = np.loadtxt(r"./model/RAINBOW.PAL")
        colors = []
        for i, color in enumerate(color_list):
            colors.append((color[0] / 255, color[1] / 255, color[2] / 255))
        self.rainbow_cm = LinearSegmentedColormap.from_list('cmap', colors, 256)
        self.rrainbow_cm = LinearSegmentedColormap.from_list('cmap', colors[::-1], 256)

    def reverse_colormap(self, cmap):
        colors = cmap.getColors(mode=pg.ColorMap.BYTE)
        rcolors = colors[::-1]
        pos = np.linspace(0, 1, len(rcolors))
        rcm = pg.ColorMap(pos=pos, color=rcolors)
        return rcm

