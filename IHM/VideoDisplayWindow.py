__author__ = 'Cheng'

from PyQt4.QtGui import *
from PyQt4.QtCore import *


#  ---------------------------------------------------------------------------------------------------------------------
#  class : PatientInformationBoard
#  ---------------------------------------------------------------------------------------------------------------------
class VideoDisplayWindow(QWidget):
    def __init__(self, parent=None):
        super(VideoDisplayWindow, self).__init__(parent)
        self.setStyleSheet('background-color:AliceBlue')
        self.myLayout = QVBoxLayout()
        #self.configurationBar = QFrame()
        #self.configurationBar.setFixedSize(640, 50)
        self.ImagePlayer = QLabel()
        self.ImagePlayer.setFixedSize(640, 480)

        self.setLayout(self.myLayout)
        #self.myLayout.addWidget(self.configurationBar)
        self.myLayout.addWidget(self.ImagePlayer)
        self.myLayout.setSpacing(0)
        self.myLayout.setMargin(0)

    def update_image(self, image):
        self.ImagePlayer.setPixmap(QPixmap.fromImage(image))