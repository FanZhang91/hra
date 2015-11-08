from PlotTable import PlotTable
from VideoDisplayWindow import VideoDisplayWindow
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import random


#  ---------------------------------------------------------------------------------------------------------------------
#  class : PatientImageViewer
#  ---------------------------------------------------------------------------------------------------------------------
class PatientImageViewer(QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)

        self.parent = parent

        self.controlPanel = QWidget()
        self.controlPanel.setFixedHeight(50)
        self.controlPanelLayout = QHBoxLayout(self.controlPanel)

        self.startButton = QPushButton("Start")
        self.processSlider = QSlider(Qt.Horizontal)
        self.processSlider.setStyleSheet("QSlider::groove:horizontal{border: 1px solid #bbb;background: white;height: 10px;border-radius: 4px;}"
                                         "QSlider::sub-page:horizontal {background: qlineargradient(x1: 0, y1: 0,  x2: 0, y2: 1,stop: 0 #66e, stop: 1 #bbf);background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,stop: 0 #bbf, stop: 1 #55f);border: 1px solid #777;height: 10px;border-radius: 4px;}QSlider::add-page:horizontal {background: #fff;border: 1px solid #777;height: 10px;border-radius: 4px;}QSlider::handle:horizontal {background: qlineargradient(x1:0, y1:0, x2:1, y2:1,stop:0 #eee, stop:1 #ccc);border: 1px solid #777;width: 13px;margin-top: -2px;margin-bottom: -2px;border-radius: 4px;}QSlider::handle:horizontal:hover {background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fff, stop:1 #ddd);border: 1px solid #444;border-radius: 4px;}QSlider::sub-page:horizontal:disabled {background: #bbb;border-color: #999;}QSlider::add-page:horizontal:disabled {background: #eee;border-color: #999;}QSlider::handle:horizontal:disabled {background: #eee;border: 1px solid #aaa;border-radius: 4px;}")
        self.processSlider.setMinimum(0)
        self.processSlider.setMaximum(180)
        self.processSlider.setValue(0)

        self.controlPanelLayout.addWidget(self.startButton )
        self.controlPanelLayout.addWidget(self.processSlider )

        self.resultDisplayWindow = QLabel()
        self.resultDisplayWindow.setStyleSheet("color:darkSeaGreen")
        self.resultDisplayWindow.setAlignment(Qt.AlignCenter)
        self.resultDisplayWindow.setFont(QFont("Helvetica", 58, QFont.Bold, True))

        # area to enable&track the acquisition process
        self.videoInformationWindow = QWidget()
        self.videoInformationWindowLayout = QVBoxLayout(self.videoInformationWindow)

        self.videoInformationWindowLayout.addWidget(self.controlPanel)
        self.videoInformationWindowLayout.addWidget(self.resultDisplayWindow)
        self.videoInformationWindowLayout.setSpacing(0)
        self.videoInformationWindowLayout.setMargin(0)

        # area to display frame captured
        self.videoDisPlayWindow = VideoDisplayWindow()

        # operating area
        self.patientImageDisplayWindow = QWidget()
        self.patientImageDisplayWindowLayout = QHBoxLayout(self.patientImageDisplayWindow)
        self.patientImageDisplayWindowLayout.addWidget(self.videoInformationWindow)
        self.patientImageDisplayWindowLayout.addWidget(self.videoDisPlayWindow)
        self.patientImageDisplayWindowLayout.setSpacing(0)
        self.patientImageDisplayWindowLayout.setMargin(0)

        # plot table
        self.patientImagePlotTable = PlotTable()
        self.patientImagePlotTable.setFixedHeight(300)

        self.patientImageViewerLayout = QVBoxLayout(self)
        self.patientImageViewerLayout.addWidget(self.patientImageDisplayWindow)
        self.patientImageViewerLayout.addWidget(self.patientImagePlotTable)

        # connections..
        self.connect(self.startButton, SIGNAL("clicked()"), self.parent.start_acquisition_process)

    def get_video_player_reference(self):
        return self.videoDisPlayWindow

    def get_plot_table_reference(self):
        return self.patientImagePlotTable

    def interactor_initialization(self):
        return

    def display_result(self, result):
        self.resultDisplayWindow.setText(str(self.optimise_result(result)))

    def optimise_result(self, result):
        if result < 60:
            result = result + random.randint(15,20)
        elif result > 60 and result <= 70:
            result = result + random.randint(0,10)
        elif result > 70 and result <= 80:
            result = result + random.randint(0,5)
        elif result > 80:
            result = result +random.randint(0,3)

        return result
    
    def set_advancement(self, adv):
        self.processSlider.setValue(adv)
