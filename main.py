__author__ = 'Cheng'


import sys
import os

from PyQt4.QtGui import *

from IHM.AnalyserMainWindow import AnalyserMainWindow
from Context.Context import Context
from Controller import Controller


def main():
    app = QApplication(sys.argv)

    # create system default folder
    username = os.environ['USERNAME']
    workspace_path = 'C:\Users\\' + username + '\Documents\HeartRateAnalyser\\'
    people_files_path = workspace_path + 'peoples\\'

    if not os.path.exists(workspace_path):
        os.mkdir(workspace_path)
        os.mkdir(people_files_path)

    # context at the background to save detector's data set
    context = Context()

    # schedule the interaction between IHM & context
    controller = Controller(context)

    # Interface Human-Machine
    analyser_window = AnalyserMainWindow(controller)
    analyser_window.show()

    app.exec_()


if __name__ == '__main__':
    main()