from matplotlib.colors import  LinearSegmentedColormap
import numpy as np
import pickle
import pyqtgraph as pg
color_list = np.loadtxt(r"C:\Users\DAN\OneDrive\Document\myCode\STM softeware\pyinstall\Image Processor\model\RAINBOW.PAL")
colors = []
for i, color in enumerate(color_list):
    colors.append((color[0], color[1], color[2]))
# rainbow = LinearSegmentedColormap.from_list('cmap', colors, 256)
# rrainbow = LinearSegmentedColormap.from_list('cmap', colors[::-1], 256)

rrainbow = pg.ColorMap(np.linspace(0,1,235), colors)

print(rrainbow)
# print(rrainbow.getLookupTable(nPts=256))

with open(r"C:\\Users\\DAN\\OneDrive\\Document\\myCode\\STM softeware\\pyinstall\\Image Processor\\model\\RRAINBOW.CMAP", 'wb') as output:
    pickle.dump(rrainbow, output, pickle.HIGHEST_PROTOCOL)  # Save data

# with open(r"C:\\Users\\DAN\\OneDrive\\Document\\myCode\\STM softeware\\pyinstall\\Image Quick Viewer\\model\\RRAINBOW.CMAP", 'rb') as input:
#     cmap = pickle.load(input)
#
# print(cmap)