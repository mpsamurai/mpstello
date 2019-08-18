__author__ = 'Junya Kaneko<junya@mpsamurai.org>'


import logging
import threading
import cv2
from mpstello.data import VideoManager


logger = logging.getLogger(__name__)


class ReceiverThreadDoesNotExists(Exception):
    pass


class ReceiverThreadAlreadyExists(Exception):
    pass


class Receiver:
    def __init__(self):
        self._callbacks = []
        self._thread = None
        self._is_receiving = False

    @property
    def is_receiving(self):
        return self._is_receiving

    def _receive(self):
        raise NotImplementedError

    def add_callback(self, callback):
        logger.debug('add callback: %s' % callback.__name__)
        self._callbacks.append(callback)

    def start(self):
        logger.debug('start receiver thread: %s' % self.__class__.__name__)
        if self._thread is not None:
            raise ReceiverThreadAlreadyExists
        self._is_receiving = True
        self._thread = threading.Thread(target=self._receive)
        self._thread.start()
        logger.debug('started receiver thread: %s' % self.__class__.__name__)

    def join(self):
        logger.debug('join receiver thread: %s' % self.__class__.__name__)
        self._thread.join()

    def stop(self):
        if self._thread is not None:
            self._is_receiving = False
            self._thread = None
            logger.debug('stop receiver thread: %s' % self.__class__.__name__)


class StateReceiver(Receiver):
    def __init__(self, socket, state_manager, response_manager, response_timeout=15):
        super().__init__()
        self._socket = socket
        self.states = state_manager
        self.responses = response_manager
        self._response_timeout = response_timeout

    def _receive(self):
        while True:
            if not self._is_receiving:
                break
            data, addr = self._socket.recvfrom(1024)
            data = data.decode()
            if ';' in data:
                # logging.debug('create state: %s' % data)
                self.states.create(data, addr)
            else:
                logger.debug('create response: %s' % data)
                self.responses.latest.set(data, addr)
            for callback in self._callbacks:
                callback(data, addr)
        logger.debug('receiver thread exit: %s' % self.__class__.__name__)


class VideoReceiver(Receiver):
    def __init__(self, addr, video_manager=VideoManager):
        super().__init__()
        self._addr = addr
        self._cap = None
        self.video = video_manager

    def _receive(self):
        logger.debug("udp://%s:%s" % self._addr)
        self._cap = cv2.VideoCapture("udp://%s:%s?overrun_nonfatal=1&fifo_size=50000000" % self._addr, cv2.CAP_FFMPEG)
        while self._is_receiving:
            ret, frame = self._cap.read()
            if ret:
                self.video.create(frame, self._addr)
        self._cap.release()
        logger.debug('receiver thread exit: %s' % self.__class__.__name__)

