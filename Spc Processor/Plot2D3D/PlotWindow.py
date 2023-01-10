# -*- coding: utf-8 -*-

import sys

from PyQt5.QtWidgets import  QApplication, QMainWindow,QLabel

from PyQt5.QtCore import  pyqtSlot,Qt

##from PyQt5.QtWidgets import   

##from PyQt5.QtGui import QColor
import copy
import numpy as np

import matplotlib as mpl
from cycler import cycler
import colorcet as cc
from mpl_toolkits.mplot3d import axes3d

##from matplotlib import cm  #colormap

##import matplotlib.style as mplStyle

##import matplotlib.pyplot as plt


from MainWindow_ui import Ui_MainWindow


class myPlotWindow(QMainWindow):

   def __init__(self, parent=None):
      super().__init__(parent)   #调用父类构造函数，创建窗体
      self.ui=Ui_MainWindow()    #创建UI对象
      self.ui.setupUi(self)      #构造UI界面

      self.__colormap= mpl.cm.seismic  #当前colormap
      self.__iniUI()    #初始化界面

      mpl.rcParams['font.sans-serif']=['SimHei']  #黑体
      mpl.rcParams['font.size']=10   
##  黑体：SimHei 宋体：SimSun 新宋体：NSimSun 仿宋：FangSong  楷体：KaiTi 
      mpl.rcParams['axes.unicode_minus'] =False    #减号unicode编码

      self.__colorbar=None   #colorbar对象
      # self.__generateData()  #生成数据
      # self.__iniFigure()     #绘图

      self.ui.widgetPlot.figure.canvas.setCursor(Qt.CrossCursor)
      self.ui.widgetPlot.figure.canvas.mpl_connect("motion_notify_event", self.do_canvas_mouseMove)
      self.ui.widgetPlot.figure.canvas.mpl_connect("pick_event", self.do_canvas_pick)

      self.ui.widgetPlot.figure.subplots_adjust(left=0.05,
               bottom=0.26, right=0.97, top=0.92, wspace=0.28)

      ''' Add these lines to MainWindow_ui.py '''
      # import ctypes
      # ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

   ##  ==============自定义功能函数========================
   def __iniUI(self):
      self.resize(1300, 700)
   ##  状态栏
      self.__labPick=QLabel("picked artist")
      self.__labPick.setMinimumWidth(200)
      self.ui.statusBar.addWidget(self.__labPick)
      
      self.__labMove=QLabel("(x,y)=")
      self.__labMove.setMinimumWidth(200)
      self.ui.statusBar.addWidget(self.__labMove)

      self.__labCmp=QLabel("colormap=seismic")
      self.__labCmp.setMinimumWidth(200)
      self.ui.statusBar.addWidget(self.__labCmp)

   ##  工具栏
      self.ui.widgetPlot.naviBar.addAction(self.ui.actSetCursor)
      self.ui.widgetPlot.naviBar.addSeparator()
      self.ui.widgetPlot.naviBar.addAction(self.ui.actQuit)

   ##  各个coloamap 下拉列表框
      cmList1=('viridis', 'plasma', 'inferno', 'magma', 'cividis')
      self.ui.comboCm1.addItems(cmList1)
      self.ui.comboCm1.currentTextChanged.connect(self.do_comboColormap_Changed)

      cmList2=('Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn')
      self.ui.comboCm2.addItems(cmList2)
      self.ui.comboCm2.currentTextChanged.connect(self.do_comboColormap_Changed)

      cmList3=( 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
            'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper')
      self.ui.comboCm3.addItems(cmList3)
      self.ui.comboCm3.currentTextChanged.connect(self.do_comboColormap_Changed)
      
      cmList4=('PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic')
      self.ui.comboCm4.addItems(cmList4)
      self.ui.comboCm4.currentTextChanged.connect(self.do_comboColormap_Changed)

      self.ui.comboCm5.currentTextChanged.connect(self.do_comboColormap_Changed)

      cmList2d = ('cc.glasbey', 'cc.glasbey_hv', 'cc.glasbey_cool', 'cc.glasbey_warm', 'cc.glasbey_dark', \
                  'cc.glasbey_light', 'blue', 'green', 'red', 'orange',\
                  'purple', 'black')
      self.cmDict2d = {0:cc.glasbey, 1:cc.glasbey_hv, 2:cc.glasbey_cool, 3:cc.glasbey_warm, 4:cc.glasbey_dark,\
                       5:cc.glasbey_light, 6:['#038add']*50, 7:['#2CA02C']*50, 8:['#d60000']*50, 9:['#FF7F0E']*50,\
                       10:['#ba6efd']*50, 11:['#1E1E1E']*50}
      # 6: blue, 7: green, 8:red, 9:orange, 10: purple, 11:black
      self.ui.combo2D_color.clear()
      self.ui.combo2D_color.addItems(cmList2d)

   def init_data(self, data_x, data3D):
      self.data3D = data3D
      y = np.linspace(0, data3D.shape[0] - 1, data3D.shape[0], endpoint=True)
      x = np.linspace(0, data3D.shape[1] - 1, data3D.shape[1], endpoint=True)
      x, y = np.meshgrid(x, y)  # 二维网格化数组
      z = data3D
      self._X = x
      self._Y = y
      self._Z = z

      self.x = data_x
      self.xyz = data3D
      self.xy = data3D

      self.ui.spinDivCount.setMinimum(0)
      self.ui.spinDivCount.setMaximum(np.max(data3D)*data3D.shape[0])

   def refresh_data(self):
      self.xyz = copy.deepcopy(self.data3D)
      interval = self.ui.spinDivCount.value()
      y = np.linspace(0, self.xyz.shape[0] * (int(interval) + 1) - 1, self.xyz.shape[0] * (int(interval) + 1), endpoint=True)
      x = np.linspace(0, self.xyz.shape[1], self.xyz.shape[1], endpoint=True)
      x, y = np.meshgrid(x, y)  # 二维网格化数组

      for i in range(self.xyz.shape[0] - 1, -1, -1):
         b = np.array(self.xyz[i, :].tolist() * int(interval)).reshape(int(interval), self.xyz.shape[1])
         self.xyz = np.insert(self.xyz, i, values=b, axis=0)

      self._X = x
      self._Y = y
      self._Z = copy.deepcopy(self.xyz)

      self.xy = copy.deepcopy(self.data3D)
      for i in range(len(self.data3D)):
         self.xy[i] += i * (interval/5)

   def __generateData(self): #生成数据
      divCount=self.ui.spinDivCount.value()  #划分网格个数
      # x=np.linspace(-5, 5, divCount, endpoint=True)
      # y=np.linspace(-5, 5, divCount, endpoint=True)
      #
      # x,y= np.meshgrid(x, y) # 二维网格化数组
      # p11=3*((1-x)**2)
      # p12=np.exp(-x**2-(y+1)**2)
      # p1=p11*p12     #按元素相乘
      #
      # p21=x/5-x**3-y**5
      # p22=np.exp(-x**2-y**2)
      # p2=-10*p21*p22
      #
      # p31=np.exp(-(x+1)**2-y**2)
      # p3=-p31/3
      #
      # self._Z=p1+p2+p3  # Z数据
      # self._X=x         # X数据
      # self._Y=y         # Y数据

   def iniFigure(self):  ##初始化图表，创建子图
      self.ui.widgetPlot.figure.clear()
      gs=self.ui.widgetPlot.figure.add_gridspec(1,2)  #1行，2列

      # 返回的self.ax3D是 mpl_toolkits.mplot3d.axes3d.Axes3D 类
   ##      self.ax3D=self.ui.widgetPlot.figure.add_subplot(1,2,1,projection='3d',label="plot3D")
      self.ax3D=self.ui.widgetPlot.figure.add_subplot(
               gs[0,0],projection='3d',label="plot3D")
   ##      self.ax3D.set_xlabel("axis-X")
   ##      self.ax3D.set_ylabel("axis-Y")
   ##      self.ax3D.set_zlabel("axis-Z")

   ##      self.ax2D=self.ui.widgetPlot.figure.add_subplot(1,2,2,label="plot2D")
      self.ax2D=self.ui.widgetPlot.figure.add_subplot(gs[0,1],label="plot2D")
   ##      self.ax2D.set_xlabel("axis-X")
   ##      self.ax2D.set_ylabel("axis-Y")
      

##  ==============event处理函数==========================


##  ==========由connectSlotsByName()自动连接的槽函数============


##=========图表操作

   @pyqtSlot()      ## 十字光标
   def on_actSetCursor_triggered(self):  
      self.ui.widgetPlot.figure.canvas.setCursor(Qt.CrossCursor)

   @pyqtSlot()      ##重新生成数据并绘图
   def on_btnRefreshData_clicked(self):  
      # self.__generateData()
      self.refresh_data()
      self.on_combo3D_type_currentIndexChanged(self.ui.combo3D_type.currentIndex())
      self.on_combo2D_color_currentIndexChanged(self.ui.combo2D_color.currentIndex())
      self.ui.chkBox3D_invertZ.setChecked(False)
      self.ui.chkBox3D_gridOn.setChecked(True)
      self.ui.chkBox3D_axisOn.setChecked(True)

##===== 3D绘图设置      

   @pyqtSlot(bool)      ## Z轴反向
   def on_chkBox3D_invertZ_clicked(self,checked):  
      self.ax3D.invert_zaxis()  #toggle
      self.ui.widgetPlot.redraw()

   @pyqtSlot(bool)      ## 显示网格
   def on_chkBox3D_gridOn_clicked(self,checked):  
      self.ax3D.grid(checked)  
      self.ui.widgetPlot.redraw()

   @pyqtSlot(bool)      ## 显示坐标轴
   def on_chkBox3D_axisOn_clicked(self,checked):  
      if checked:
         self.ax3D.set_axis_on()  
      else:
         self.ax3D.set_axis_off()  
      self.ui.widgetPlot.redraw()

   @pyqtSlot(int)      ## 3D绘图类型
   def on_combo3D_type_currentIndexChanged(self,index):  #
      self.ax3D.clear()
      if index==0:   # 3D surface
         normDef=mpl.colors.Normalize(vmin=self._Z.min(), vmax=self._Z.max())
         series3D = self.ax3D.plot_surface(self._X, self._Y, self._Z,
                           cmap=self.__colormap, linewidth=1, picker=True,
                           norm=normDef)
         self.ax3D.set_title("3D surface")
      elif index==1:  # 3D wireframe
         series3D = self.ax3D.plot_wireframe(self._X, self._Y, self._Z,
                           cmap=self.__colormap, linewidth=1, picker=True)
         self.ax3D.set_title("3D wireframe")
      elif index==2:   # 3D scatter 
         series3D = self.ax3D.scatter(self._X, self._Y, self._Z,
                           s=15, c='r', picker=True)
         self.ax3D.set_title("3D scatter")

      self.ax3D.set_xlabel("axis-X")
      self.ax3D.set_ylabel("axis-Y")
      self.ax3D.set_zlabel("axis-Z")

      # if self.__colorbar==None:   #还未创建__colorbar
      #    self.__colorbar = self.ui.widgetPlot.figure.colorbar(
      #          mappable= series3D, ax=[self.ax3D],
      #          orientation='horizontal',label="colorbar",
      #          shrink=0.8, aspect=25,  pad=0.2, fraction=0.05)
      #    self.__colorbar.solids.set_edgecolor("face")
      # print("create: ", self.__colorbar)

      self.ui.widgetPlot.redraw()


         ##colorbar(self, mappable, cax=None, ax=None, use_gridspec=True, **kw)
         ##    Create a colorbar for a ScalarMappable instance, *mappable*.
      ##        *orientation* vertical or horizontal
      ##        *fraction*    0.15; fraction of original axes to use for colorbar
      ##        *pad*         0.05 if vertical, 0.15 if horizontal; fraction
      ##                      of original axes between colorbar and new image axes
      ##        *shrink*      1.0; fraction by which to multiply the size of the colorbar 大小
      ##        *aspect*      20; ratio of long to short dimensions 窗宽比
      ##        *anchor*      (0.0, 0.5) if vertical; (0.5, 1.0) if horizontal;
      ##                      the anchor point of the colorbar axes
      ##        *panchor*     (1.0, 0.5) if vertical; (0.5, 0.0) if horizontal;
      ##                      the anchor point of the colorbar parent axes. If
      ##                      False, the parent axes' anchor will be unchanged

##==========2D绘图

   @pyqtSlot(int)      ## 2D绘图类型
   def on_combo2D_color_currentIndexChanged(self, index):
      if hasattr(self, "ax2D"):

         self.ax2D.clear()
         # if index == 0:
         #    self.ax2D.set_prop_cycle(cycler('color', cc.glasbey))
         # elif index == 1:
         #    self.ax2D.set_prop_cycle(cycler('color', cc.glasbey_hv))
         # elif index == 2:
         #    self.ax2D.set_prop_cycle(cycler('color', cc.glasbey_cool))
         # elif index == 3:
         #    self.ax2D.set_prop_cycle(cycler('color', cc.glasbey_warm))

         self.ax2D.set_prop_cycle(cycler('color', self.cmDict2d[index]))

         for i in range(self.xy.shape[0]):
            self.ax2D.plot(self.x, self.xy[i])

         self.ax2D.set_xlabel("axis-X")
         self.ax2D.set_ylabel("axis-Y")
         self.ui.widgetPlot.redraw()

##  =================自定义槽函数==========

   @pyqtSlot(str)  ##在ComboBox中选择了colormap
   def do_comboColormap_Changed(self, arg1):
      self.__colormap=mpl.cm.get_cmap(arg1)  #通过字符串获得colormap，当前colormap
      self.__labCmp.setText("colormap="+arg1)
      # !!! color bar do not have "set_cmap"
      # self.__colorbar.set_cmap(self.__colormap)
      # self.__colorbar.draw_all()

      index=self.ui.combo3D_type.currentIndex()    #三维图类型
      self.on_combo3D_type_currentIndexChanged(index)   #重画三维图
      self.ui.chkBox3D_invertZ.setChecked(False)
      self.ui.chkBox3D_gridOn.setChecked(True)
      self.ui.chkBox3D_axisOn.setChecked(True)

      # index=self.ui.combo2D_type.currentIndex()    #二维图类型
      self.on_combo2D_color_currentIndexChanged(self.ui.combo2D_color.currentIndex())   #重画二维图

   def do_canvas_mouseMove(self, event): ##鼠标移动
      if event.inaxes==self.ax2D:
         info="2D plot(x,y)=(%.2f, %.2f)"%(event.xdata,event.ydata)
      elif event.inaxes==self.ax3D:    #3D图不能得到正确的坐标数据
         info="3D plot(x,y)=(%.2f, %.2f)"%(event.xdata,event.ydata)
      else:
         info=""
      self.__labMove.setText(info)
      
   def do_canvas_pick(self, event):  ##拾取对象
      info="picked artist="+event.artist.__class__.__name__  #类名称
      self.__labPick.setText(info)

   def close(self) -> bool:
      self.ui.widgetPlot.figure.clear()
      self.close()
    
   
##  ============窗体测试程序 ================================
if  __name__ == "__main__":        #用于当前窗体测试
   app = QApplication(sys.argv)    #创建GUI应用程序
   form=myPlotWindow()            #创建窗体
   form.show()
   sys.exit(app.exec_())
