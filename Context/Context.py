__author__ = 'Cheng'


class Context:
    def __init__(self):

        self.dectections = list()

        self.counter = 0
        self.frames = []
        self.faces_number = 0
        self.processingTime = 0
        self.faceDetectingCapacity = 1
        self.needToBeRestart = False
        self.results = []
