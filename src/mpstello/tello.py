import socket
import logging
from mpstello import data
from mpstello import receivers
from mpstello import commands


logging.basicConfig(level=logging.DEBUG)


class Tello:
    def __init__(self, tello_addr=('192.168.10.1', 8889), video_addr=('192.168.10.2', 11111), local_addr=('', 8890),
                 timeout=5, buff_size=100, video_buff_size=10):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(local_addr)
        self._state_receiver = receivers.StateReceiver(
            sock, data.StateManager(buff_size=buff_size), data.ResponseManager(buff_size=buff_size))
        self._video_receiver = receivers.VideoReceiver(video_addr, data.VideoManager(buff_size=video_buff_size))
        self._command_executor = commands.Executor(sock, tello_addr, self._state_receiver.responses, timeout)

    @property
    def commands(self):
        return self._command_executor

    @property
    def frame(self):
        return self._video_receiver.video.latest

    @property
    def state(self):
        return self._state_receiver.states.latest

    @property
    def response(self):
        return self._state_receiver.responses.latest

    @property
    def video(self):
        return self._video_receiver.video.latest

    def start(self):
        self._state_receiver.start()

    def stop(self):
        self._state_receiver.stop()

    @property
    def is_started(self):
        return self._state_receiver.is_receiving

    def start_video(self):
        self._video_receiver.start()

    def stop_video(self):
        self._video_receiver.stop()

    @property
    def is_video_started(self):
        return self._video_receiver.is_receiving

    def join(self):
        if self._state_receiver.is_receiving:
            self._state_receiver.join()
        if self._video_receiver.is_receiving:
            self._video_receiver.join()

    def stop_all(self):
        self.stop()
        self.stop_video()

