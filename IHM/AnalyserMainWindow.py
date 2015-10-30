from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PatientImageViewer import PatientImageViewer

import cv2
import cv
import threading
import numpy as np

from Image.qrc_resources import *
# cmd for convert png files to resource code: pyrcc4.exe -o qrc_resources.py resource.qrc

from scipy import signal
from sklearn.decomposition import FastICA

import statsmodels.api as sm


#  ---------------------------------------------------------------------------------------------------------------------
#  class : AnalyserMainWindow
#  ---------------------------------------------------------------------------------------------------------------------
class AnalyserMainWindow(QMainWindow):
    def __init__(self, controller=None):
        QMainWindow.__init__(self)
        self.setWindowTitle("HeartRateAnalyser")
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        # self.setWindowOpacity(0.97)
        self.setMouseTracking(True)
        self.setAutoFillBackground(True)
        self.draw_background()

        self.cascade = cv.Load("C:\Python27\haarcascade_frontalface_alt2.xml")

        #  -------------------------------------------------------------------------------------------------------------
        #  Initialization variable
        #  -------------------------------------------------------------------------------------------------------------
        self.controller = controller

        self.framesTreated = []
        self.frames = []
        self.np_result = []
        self.results = []

        self.capture = cv.CaptureFromCAM(0)

        self.min_size = (15, 15)
        self.heartRate = 0
        # self.capture = 0
        self.frameMaximumNumber = 180
        self.image_scale = 2
        self.haar_scale = 1.2
        self.min_neighbors = 2
        self.haar_flags = 0
        self.processingTime = 0
        self.faces_number = 0
        self.counter = 0
        self.faceDetectingCapacity = 1
        self.testCounter = 0

        self.needToBeRestart = False
        self.acquisitionFlag = True

        self.frameToBeDisplayed = None
        self.acquisitionTask = None

        self.timestamps = [x for x in range(self.frameMaximumNumber)]

        self.timer = QTimer(self)

        #  menuBar
        # self.fileMenu = self.menuBar().addMenu("&File")
        # self.editMenu = self.menuBar().addMenu("&Edit")
        # self.helpMenu = self.menuBar().addMenu("&Help")

        #  define the menu bar's action
        file_new_action = self.create_action("&New...", self.file_new, QKeySequence.New, "filenew", "Create an image file")
        file_open_action = self.create_action("&Open...", self.file_open, QKeySequence.Open, "fileopen", "Open an existing image file")
        file_save_action = self.create_action("&Save", self.file_save, QKeySequence.Save, "filesave", "Save the image")
        file_save_as_action = self.create_action("Save &As...", self.start_acquisition_process, icon="filesaveas",tip="Save the image using a new name")

        #  add the tool bar
        # file_tool_bar = self.addToolBar("File")
        # edit_tool_bar = self.addToolBar("Edit")
        # self.add_actions(file_tool_bar, (file_new_action, file_open_action, file_save_action, file_save_as_action))
        # self.add_actions(edit_tool_bar, ())

        #  add the action into the menu
        # self.add_actions(self.fileMenu, (file_new_action, file_open_action, file_save_action, file_save_as_action))

        self.patientImageViewer = PatientImageViewer(self)
        self.displayWindow = self.patientImageViewer.get_video_player_reference()

        self.windowsContainer = QWidget()
        central_layout = QHBoxLayout(self.windowsContainer)
        central_layout.addWidget(self.patientImageViewer)
        central_layout.setSpacing(0)
        central_layout.setMargin(0)

        self.setCentralWidget(self.windowsContainer)
        self.setFixedSize(1200, 800)

        # set connections
        self.connect(self.timer, SIGNAL("timeout()"), self.do_signals_processing)

    def create_action(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def file_new(self):
        return

    def file_open(self):
        return

    def load_file(self, fname=None):
        return

    def add_recent_file(self, fname):
        return

    def file_save(self):
        return

    def stop_video_capture_task(self):
        return

    def apply_on_the_page(self):
        #  process after display finished.....
        curve = self.generate_peoples_results_files()
        self.patientImageViewer.get_plot_table_reference().showData(self.timestamps, curve)
        self.patientImageViewer.display_result(self.heartRate)
        self.stop_video_capture_task()

    def face_detecting(self, frame):
        # start = time.time()
        self.processingTime += 1

        image_size = cv.GetSize(frame)
        gray = cv.CreateImage(image_size, 8, 1)
        small_img = cv.CreateImage(
            (cv.Round(frame.width / self.image_scale), cv.Round(frame.height / self.image_scale)), 8, 1)
        cv.CvtColor(frame, gray, cv.CV_BGR2GRAY)
        cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)
        cv.EqualizeHist(small_img, small_img)
        faces = cv.HaarDetectObjects(small_img, self.cascade, cv.CreateMemStorage(0), self.haar_scale,
                                     self.min_neighbors, self.haar_flags,
                                     self.min_size)
        self.faces_number = len(faces)

        if self.processingTime is 1:
            if self.faces_number < 1:
                self.needToBeRestart = True
                self.processingTime = 0
                return None

        faces_count = 0
        if self.faces_number is self.faceDetectingCapacity:
            for ((x, y, w, h), n) in faces:
                sum_pixlevalue_b = 0
                sum_pixlevalue_g = 0
                sum_pixlevalue_r = 0

                if self.processingTime is 1:
                    self.faceDetectingCapacity = self.faces_number
                    rgb = {'green': [], 'red': [], 'blue': []}
                    self.results.append(rgb)

                x1, y1 = (int(x * self.image_scale), int(y * self.image_scale))
                x2, y2 = (int((x + w) * self.image_scale), int((y + h) * self.image_scale))
                x11 = int((8 * x1 + 2 * x2) / 10)
                y11 = int(y1)
                x22 = int((2 * x1 + 8 * x2) / 10)
                y22 = int(y2)
                pt1 = (x11, y11)
                pt2 = (x22, y22)
                cv.Rectangle(frame, pt1, pt2, cv.RGB(0, 255, 0), 3, 8, 0)
                # end = time.time()
                # print (start - end)
                Rectangle_width = x22 - x11 + 1
                Rectangle_height = y22 - y11 + 1
                sum_pixleNumber = Rectangle_width * Rectangle_height

                for i in range(y11, y22):
                    for j in range(x11, x22):
                        tmpbgr = cv.Get2D(frame, i, j)
                        sum_pixlevalue_b += tmpbgr[0]
                        sum_pixlevalue_g += tmpbgr[1]
                        sum_pixlevalue_r += tmpbgr[2]

                self.results[faces_count]['blue'].append(sum_pixlevalue_b / sum_pixleNumber)
                self.results[faces_count]['green'].append(sum_pixlevalue_g / sum_pixleNumber)
                self.results[faces_count]['red'].append(sum_pixlevalue_r / sum_pixleNumber)

                faces_count += 1

        else:
            self.needToBeRestart = True
            self.processingTime = 0
        return frame

    def generate_peoples_results_files(self):

        self.np_result = np.c_[self.results[0]['blue'], self.results[0]['green'], self.results[0]['red']]
        list_number = len(self.results[0]['blue'])

        #  ICA
        ica = FastICA(n_components=3, fun='logcosh', max_iter=2000)
        ica_transformed = ica.fit_transform(self.np_result)
        component_all = ica_transformed.ravel([1])
        component_1 = component_all[:list_number]
        component_2 = component_all[list_number:(2 * list_number)]
        component_3 = component_all[(2 * list_number):(3 * list_number)]

        #  butter_smooth
        N = 8
        Wn = [1.6 / 30, 4.0 / 30]
        t = np.linspace(1 / 30, list_number / 30, list_number)
        b, a = signal.butter(N, Wn, 'bandpass', analog=False)
        filter_1 = signal.filtfilt(b, a, component_1)
        filter_2 = signal.filtfilt(b, a, component_2)
        filter_3 = signal.filtfilt(b, a, component_3)
        lowess_1 = sm.nonparametric.lowess(filter_1, t, frac=10.0 / list_number)
        lowess_2 = sm.nonparametric.lowess(filter_2, t, frac=10.0 / list_number)
        lowess_3 = sm.nonparametric.lowess(filter_3, t, frac=10.0 / list_number)

        smooths = []
        smooth_1 = lowess_1[:, 1]
        smooth_2 = lowess_2[:, 1]
        smooth_3 = lowess_3[:, 1]
        smooths.append(smooth_1)
        smooths.append(smooth_2)
        smooths.append(smooth_3)

        # FFT and spectrum
        fft_1 = np.fft.fft(smooth_1, 256)
        fft_2 = np.fft.fft(smooth_2, 256)
        fft_3 = np.fft.fft(smooth_3, 256)
        spectrum_1 = list(np.abs(fft_1) ** 2)
        spectrum_2 = list(np.abs(fft_2) ** 2)
        spectrum_3 = list(np.abs(fft_3) ** 2)
        max1 = max(spectrum_1)
        max2 = max(spectrum_2)
        max3 = max(spectrum_3)
        num_spec1 = spectrum_1.index(max(spectrum_1))
        if num_spec1 > (list_number / 2):
            num_spec1 = 256 - num_spec1
        num_spec2 = spectrum_2.index(max(spectrum_2))
        if num_spec2 > (list_number / 2):
            num_spec2 = 256 - num_spec2
        num_spec3 = spectrum_3.index(max(spectrum_3))
        if num_spec3 > (list_number / 2):
            num_spec3 = 256 - num_spec3
        num_spec = [num_spec1, num_spec2, num_spec3]
        max_all = [max1, max2, max3]
        max_num = max_all.index(max(max_all))
        self.heartRate = int(num_spec[max_num] * 1800 / 256) + 1
        return smooths[max_num]

    def do_signals_processing(self):
        if self.acquisitionFlag:
            if self.frameToBeDisplayed is not None:
                self.displayWindow.update_image(QImage(self.frameToBeDisplayed.tostring(),
                                                       self.frameToBeDisplayed.width,
                                                       self.frameToBeDisplayed.height,
                                                       QImage.Format_RGB888).rgbSwapped())
        else:
            self.timer.stop()
            cv2.VideoCapture(0).release()
            self.apply_on_the_page()
            self.testCounter += 1

    def do_images_acquisition(self):
        self.counter = 0
        while self.acquisitionFlag:
            self.patientImageViewer.set_advancement(self.counter)
            frame = cv.QueryFrame(self.capture)
            self.frameToBeDisplayed = self.face_detecting(frame)
            self.frames.append(self.frameToBeDisplayed)

            if self.needToBeRestart:
                self.counter = -1
                self.frames = []
                self.faces_number = 0
                self.faceDetectingCapacity = 1
                self.needToBeRestart = False
                self.results = []

            self.counter += 1
            if self.counter == self.frameMaximumNumber:
                self.acquisitionFlag = False

    # do_images_acquisition()
    def init_camera(self):
        # self.capture = cv.CaptureFromCAM(0)
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FPS, 30)
        fps = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FPS)

    def start_acquisition_process(self):
        self.counter = 0
        self.frames = []
        self.faces_number = 0
        self.processingTime = 0
        self.faceDetectingCapacity = 1
        self.needToBeRestart = False
        self.results = []

        self.acquisitionFlag = True
        self.init_camera()

        self.timer.start(50)

        acquisitionTask = threading.Thread(None, self.do_images_acquisition)
        acquisitionTask.start()

    def file_print(self):
        return

    def draw_background(self):
        pixmap = QPixmap(":/pagebackground.png")
        palette = self.palette()
        palette.setBrush(QPalette.Background, QBrush(
            pixmap.scaled(QSize(self.width(), self.height()), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
        self.setPalette(palette)
        self.setMask(pixmap.mask())
        self.setAutoFillBackground(True)
