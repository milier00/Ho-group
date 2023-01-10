# -*- coding: utf-8 -*-
"""
@Date     : 12/28/2022 15:40:46
@Author   : milier00
@FileName : CustomHistogramLUTItem.py
"""
"""
GraphicsWidget displaying an image histogram along with gradient editor. Can be used to
adjust the appearance of images.
"""
from pyqtgraph import ROI
from pyqtgraph import ViewBox
import pyqtgraph
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
#from numpy.linalg import norm

from pyqtgraph import Point
from pyqtgraph import SRTTransform
from math import cos, sin
from pyqtgraph import functions as fn
from pyqtgraph import GraphicsObject
from pyqtgraph import UIGraphicsItem
from pyqtgraph import getConfigOption
from PyQt5.QtCore import Qt

import weakref

import numpy as np
from pyqtgraph import debug as debug
from pyqtgraph import functions as fn
from pyqtgraph import Point
from PyQt5 import QtGui, QtWidgets
from pyqtgraph import QtCore
from pyqtgraph import AxisItem
from pyqtgraph import GradientEditorItem
from pyqtgraph import GraphicsWidget
from pyqtgraph import LinearRegionItem
from pyqtgraph import PlotCurveItem
from pyqtgraph import ViewBox
import pyqtgraph as pg

__all__ = ['CustomHistogramLUTItem', 'CustomGradientEditorItem']
class CustomGradientEditorItem(pg.GradientEditorItem):
    def __init__(self, *args, **kwds):
        pg.GradientEditorItem.__init__(self, *args, **kwds)

    def setColorMap(self, cm, num):
        # Mass edit ticks without graphics update
        signalsBlocked = self.blockSignals(True)

        self.setColorMode('rgb')
        for t in list(self.ticks.keys()):
            self.removeTick(t, finish=False)
        colors = cm.getColors(mode='qcolor')

        ''' Customize ticks from line number '''
        xx = np.linspace(0, 1, num)
        pos_index = np.linspace(0, len(cm.pos) - 1, num)
        pos_index = [int(ind) for ind in pos_index]
        cc = [colors[p] for p in pos_index]
        for i in range(len(xx)):
            x = xx[i]
            c = cc[i]
            self.addTick(x, c, finish=False)
        ''' --------- End ---------- '''

        # Close with graphics update
        self.blockSignals(signalsBlocked)
        self.sigTicksChanged.emit(self)
        self.sigGradientChangeFinished.emit(self)

    ## need to rewrite!!
    def restoreState(self, state):
        """
        Restore the gradient specified in state.

        ==============  ====================================================================
        **Arguments:**
        state           A dictionary with same structure as those returned by
                        :func:`saveState <pyqtgraph.GradientEditorItem.saveState>`

                        Keys must include:

                            - 'mode': hsv or rgb
                            - 'ticks': a list of tuples (pos, (r,g,b,a))
        ==============  ====================================================================
        """
        ## public

        # Mass edit ticks without graphics update
        signalsBlocked = self.blockSignals(True)

        self.setColorMode(state['mode'])
        for t in list(self.ticks.keys()):
            self.removeTick(t, finish=False)
        for t in state['ticks']:
            c = QtGui.QColor(*t[1])
            self.addTick(t[0], c, finish=False)
        self.showTicks(state.get('ticksVisible',
                                 next(iter(self.ticks)).isVisible()))

        # Close with graphics update
        self.blockSignals(signalsBlocked)
        self.sigTicksChanged.emit(self)
        self.sigGradientChangeFinished.emit(self)


class CustomHistogramLUTItem(GraphicsWidget):
    """
    :class:`~pyqtgraph.GraphicsWidget` with controls for adjusting the display of an
    :class:`~pyqtgraph.ImageItem`.

    Includes:

      - Image histogram
      - Movable region over the histogram to select black/white levels
      - Gradient editor to define color lookup table for single-channel images

    Parameters
    ----------
    image : pyqtgraph.ImageItem, optional
        If provided, control will be automatically linked to the image and changes to
        the control will be reflected in the image's appearance. This may also be set
        via :meth:`setImageItem`.
    fillHistogram : bool, optional
        By default, the histogram is rendered with a fill. Performance may be improved
        by disabling the fill. Additional control over the fill is provided by
        :meth:`fillHistogram`.
    levelMode : str, optional
        'mono' (default)
            One histogram with a :class:`~pyqtgraph.LinearRegionItem` is displayed to
            control the black/white levels of the image. This option may be used for
            color images, in which case the histogram and levels correspond to all
            channels of the image.
        'rgba'
            A histogram and level control pair is provided for each image channel. The
            alpha channel histogram and level control are only shown if the image
            contains an alpha channel.
    gradientPosition : str, optional
        Position of the gradient editor relative to the histogram. Must be one of
        {'right', 'left', 'top', 'bottom'}. 'right' and 'left' options should be used
        with a 'vertical' orientation; 'top' and 'bottom' options are for 'horizontal'
        orientation.
    orientation : str, optional
        The orientation of the axis along which the histogram is displayed. Either
        'vertical' (default) or 'horizontal'.

    Attributes
    ----------
    sigLookupTableChanged : QtCore.Signal
        Emits the HistogramLUTItem itself when the gradient changes
    sigLevelsChanged : QtCore.Signal
        Emits the HistogramLUTItem itself while the movable region is changing
    sigLevelChangeFinished : QtCore.Signal
        Emits the HistogramLUTItem itself when the movable region is finished changing

    See Also
    --------
    :class:`~pyqtgraph.ImageItem`
        HistogramLUTItem is most useful when paired with an ImageItem.
    :class:`~pyqtgraph.ImageView`
        Widget containing a paired ImageItem and HistogramLUTItem.
    :class:`~pyqtgraph.HistogramLUTWidget`
        QWidget containing a HistogramLUTItem for widget-based layouts.
    """

    sigLookupTableChanged = QtCore.Signal(object)
    sigLevelsChanged = QtCore.Signal(object)
    sigLevelChangeFinished = QtCore.Signal(object)

    def __init__(self, image=None, fillHistogram=True, levelMode='mono',
                 gradientPosition='right', orientation='vertical'):
        GraphicsWidget.__init__(self)
        self.lut = None
        self.imageItem = lambda: None  # fake a dead weakref
        self.levelMode = levelMode
        self.orientation = orientation
        self.gradientPosition = gradientPosition

        if orientation == 'vertical' and gradientPosition not in {'right', 'left'}:
            self.gradientPosition = 'right'
        elif orientation == 'horizontal' and gradientPosition not in {'top', 'bottom'}:
            self.gradientPosition = 'bottom'

        self.layout = QtWidgets.QGraphicsGridLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(0)

        self.gradient = CustomGradientEditorItem(orientation=self.gradientPosition)

        self.layout.addItem(self.gradient, 0, 0)
        self.gradient.setFlag(self.gradient.GraphicsItemFlag.ItemStacksBehindParent)
        self.gradient.sigGradientChanged.connect(self.gradientChanged)

        self._showRegions()

        if image is not None:
            self.setImageItem(image)


    def paint(self, p, *args):
        pass

    def setImageItem(self, img):
        """Set an ImageItem to have its levels and LUT automatically controlled by this
        HistogramLUTItem.
        """
        self.imageItem = weakref.ref(img)
        img.sigImageChanged.connect(self.imageChanged)
        self._setImageLookupTable()
        self.regionChanged()
        self.imageChanged(autoLevel=True)

    def viewRangeChanged(self):
        self.update()

    def gradientChanged(self):
        if self.imageItem() is not None:
            self._setImageLookupTable()

        self.lut = None
        self.sigLookupTableChanged.emit(self)

    def _setImageLookupTable(self):
        if self.gradient.isLookupTrivial():
            self.imageItem().setLookupTable(None)
        else:
            self.imageItem().setLookupTable(self.getLookupTable)

    def getLookupTable(self, img=None, n=None, alpha=None):
        """Return a lookup table from the color gradient defined by this
        HistogramLUTItem.
        """
        if self.levelMode != 'mono':
            return None
        if n is None:
            if img.dtype == np.uint8:
                n = 256
            else:
                n = 512
        if self.lut is None:
            self.lut = self.gradient.getLookupTable(n, alpha=alpha)
        return self.lut

    def regionChanged(self):
        if self.imageItem() is not None:
            self.imageItem().setLevels(self.getLevels())
        self.sigLevelChangeFinished.emit(self)

    def regionChanging(self):
        if self.imageItem() is not None:
            self.imageItem().setLevels(self.getLevels())
        self.update()
        self.sigLevelsChanged.emit(self)

    def imageChanged(self, autoLevel=False, autoRange=False):
        if self.imageItem() is None:
            return

        if self.levelMode == 'mono':
            for plt in self.plots[1:]:
                plt.setVisible(False)
            self.plots[0].setVisible(True)
            # plot one histogram for all image data
            profiler = debug.Profiler()
            h = self.imageItem().getHistogram()
            profiler('get histogram')
            if h[0] is None:
                return
            self.plot.setData(*h)
            profiler('set plot')
            if autoLevel:
                mn = h[0][0]
                mx = h[0][-1]
                self.region.setRegion([mn, mx])
                profiler('set region')
            else:
                mn, mx = self.imageItem().levels
                self.region.setRegion([mn, mx])
        else:
            # plot one histogram for each channel
            self.plots[0].setVisible(False)
            ch = self.imageItem().getHistogram(perChannel=True)
            if ch[0] is None:
                return
            for i in range(1, 5):
                if len(ch) >= i:
                    h = ch[i-1]
                    self.plots[i].setVisible(True)
                    self.plots[i].setData(*h)
                    if autoLevel:
                        mn = h[0][0]
                        mx = h[0][-1]
                        self.regions[i].setRegion([mn, mx])
                else:
                    # hide channels not present in image data
                    self.plots[i].setVisible(False)
            # make sure we are displaying the correct number of channels
            self._showRegions()

    def getLevels(self):
        """Return the min and max levels.

        For rgba mode, this returns a list of the levels for each channel.
        """
        if self.levelMode == 'mono':
            return self.region.getRegion()
        else:
            nch = self.imageItem().channels()
            if nch is None:
                nch = 3
            return [r.getRegion() for r in self.regions[1:nch+1]]

    def setLevels(self, min=None, max=None, rgba=None):
        """Set the min/max (bright and dark) levels.

        Parameters
        ----------
        min : float, optional
            Minimum level.
        max : float, optional
            Maximum level.
        rgba : list, optional
            Sequence of (min, max) pairs for each channel for 'rgba' mode.
        """
        if None in {min, max} and (rgba is None or None in rgba[0]):
            raise ValueError("Must specify min and max levels")

        if self.levelMode == 'mono':
            if min is None:
                min, max = rgba[0]
            self.region.setRegion((min, max))
        else:
            if rgba is None:
                rgba = 4*[(min, max)]
            for levels, region in zip(rgba, self.regions[1:]):
                region.setRegion(levels)

    def setLevelMode(self, mode):
        """Set the method of controlling the image levels offered to the user.

        Options are 'mono' or 'rgba'.
        """
        if mode not in {'mono', 'rgba'}:
            raise ValueError(f"Level mode must be one of {{'mono', 'rgba'}}, got {mode}")

        if mode == self.levelMode:
            return

        oldLevels = self.getLevels()
        self.levelMode = mode
        self._showRegions()

        # do our best to preserve old levels
        if mode == 'mono':
            levels = np.array(oldLevels).mean(axis=0)
            self.setLevels(*levels)
        else:
            levels = [oldLevels] * 4
            self.setLevels(rgba=levels)

        # force this because calling self.setLevels might not set the imageItem
        # levels if there was no change to the region item
        if self.imageItem() is not None:
            self.imageItem().setLevels(self.getLevels())

        self.imageChanged()
        self.update()

    def _showRegions(self):
        # for i in range(len(self.regions)):
        #     self.regions[i].setVisible(False)

        if self.levelMode == 'rgba':
            nch = 4
            if self.imageItem() is not None:
                # Only show rgb channels if connected image lacks alpha.
                nch = self.imageItem().channels()
                if nch is None:
                    nch = 3
            xdif = 1.0 / nch
            for i in range(1, nch+1):
                self.regions[i].setVisible(True)
                self.regions[i].setSpan((i-1) * xdif, i * xdif)
            self.gradient.hide()
        elif self.levelMode == 'mono':
            # self.regions[0].setVisible(True)
            self.gradient.show()
        else:
            raise ValueError(f"Unknown level mode {self.levelMode}")

    def saveState(self):
        return {
            'gradient': self.gradient.saveState(),
            'levels': self.getLevels(),
            'mode': self.levelMode,
        }

    def restoreState(self, state):
        if 'mode' in state:
            self.setLevelMode(state['mode'])
        self.gradient.restoreState(state['gradient'])
        self.setLevels(*state['levels'])
