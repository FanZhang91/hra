__author__ = 'Cheng'

from PyQt4.QtGui import *
from PyQt4.Qwt5 import *
from PyQt4.QtCore import *


#  ---------------------------------------------------------------------------------------------------------------------
#  class : PlotTable
#  ---------------------------------------------------------------------------------------------------------------------
class PlotTable(QwtPlot):
    def __init__(self, *args):
        QwtPlot.__init__(self, *args)

        self.setTitle('Frequency Response of a face processing system')
        self.setCanvasBackground(Qt.darkBlue)

        # legend
        legend = QwtLegend()
        legend.setFrameStyle(QFrame.Box | QFrame.Sunken)
        legend.setItemMode(QwtLegend.ClickableItem)
        self.insertLegend(legend, QwtPlot.BottomLegend)

        # grid
        self.grid = QwtPlotGrid()
        self.grid.enableXMin(True)
        self.grid.setMajPen(QPen(Qt.white, 0, Qt.DotLine))
        self.grid.setMinPen(QPen(Qt.gray, 0 , Qt.DotLine))
        self.grid.attach(self)

        # axes
        self.setAxisTitle(QwtPlot.xBottom, u'\u03c9/\u03c9<sub>0</sub>')
        self.setAxisTitle(QwtPlot.yLeft, 'Smooth_Result')

        #self.setAxisMaxMajor(QwtPlot.xBottom, 6)
        #self.setAxisMaxMinor(QwtPlot.xBottom, 10)
        #self.setAxisScaleEngine(QwtPlot.xBottom, QwtLog10ScaleEngine())

        # curves
        self.curve1 = QwtPlotCurve('Smooth')
        self.curve1.setRenderHint(QwtPlotItem.RenderAntialiased);
        self.curve1.setPen(QPen(Qt.yellow))

        self.curve1.setYAxis(QwtPlot.yLeft)
        self.curve1.attach(self)

        # alias
        fn = self.fontInfo().family()

        # marker
        self.dB3Marker = m = QwtPlotMarker()
        m.setValue(0.0, 0.0)
        m.setLineStyle(QwtPlotMarker.VLine)
        m.setLabelAlignment(Qt.AlignRight | Qt.AlignBottom)
        m.setLinePen(QPen(Qt.green, 2, Qt.DashDotLine))
        text = QwtText('')
        text.setColor(Qt.green)
        text.setBackgroundBrush(Qt.red)
        text.setFont(QFont(fn, 12, QFont.Bold))
        m.setLabel(text)
        m.attach(self)

        self.peakMarker = m = QwtPlotMarker()
        m.setLineStyle(QwtPlotMarker.HLine)
        m.setLabelAlignment(Qt.AlignRight | Qt.AlignBottom)
        m.setLinePen(QPen(Qt.red, 2, Qt.DashDotLine))
        text = QwtText('')
        text.setColor(Qt.red)
        text.setBackgroundBrush(QBrush(self.canvasBackground()))
        text.setFont(QFont(fn, 12, QFont.Bold))

        m.setLabel(text)
        m.setSymbol(QwtSymbol(QwtSymbol.Diamond, QBrush(Qt.yellow), QPen(Qt.green), QSize(7,7)))
        m.attach(self)

        # text marker
        m = QwtPlotMarker()
        m.setValue(0.1, -20.0)
        m.setLabelAlignment(Qt.AlignRight | Qt.AlignBottom)
        text = QwtText(
            u'[1-(\u03c9/\u03c9<sub>0</sub>)<sup>2</sup>+2j\u03c9/Q]'
            '<sup>-1</sup>'
            )
        text.setFont(QFont(fn, 12, QFont.Bold))
        text.setColor(Qt.blue)
        text.setBackgroundBrush(QBrush(Qt.yellow))
        text.setBackgroundPen(QPen(Qt.red, 2))
        m.setLabel(text)
        m.attach(self)

        self.setDamp(0.01)

    # __init__()

    def showData(self, frequency, amplitude):
        self.curve1.setData(frequency, amplitude)
        self.setAxisAutoScale(QwtPlot.xBottom)
        self.setAxisAutoScale(QwtPlot.yLeft)
        self.replot()

    # showData()

    def showPeak(self, frequency, amplitude):
        self.peakMarker.setValue(frequency, amplitude)
        label = self.peakMarker.label()
        label.setText('Peak: %4g dB' % amplitude)
        self.peakMarker.setLabel(label)

    # showPeak()

    def show3dB(self, frequency):
        self.dB3Marker.setValue(frequency, 0.0)
        label = self.dB3Marker.label()
        label.setText('-3dB at f = %4g' % frequency)
        self.dB3Marker.setLabel(label)

    def setDamp(self, d):
        self.replot()