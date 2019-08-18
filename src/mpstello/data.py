__author__ = 'Junya Kaneko <junya@mpsamurai.org>'

from datetime import datetime, timedelta
import logging
import numpy as np
from mpstello.commands import Type


logger = logging.getLogger(__name__)


class Response:
    def __init__(self, command, command_args, timeout=15):
        self._command = command
        self._command_args = command_args
        self._addr = None
        self._body = None
        self._timestamp = datetime.now()
        self._duration = None
        self._timeout = timedelta(seconds=timeout)

    @property
    def command(self):
        return self._command.name

    @property
    def command_args(self):
        return self._command_args

    @property
    def command_type(self):
        return self._command.command_type

    def set(self, body, addr):
        if isinstance(body, bytes):
            body = body.decode()
        self._body = self._command.return_type(body)
        self._addr = addr
        self._duration = datetime.now() - self._timestamp

    @property
    def body(self):
        return self._body

    @property
    def addr(self):
        return self._addr

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def is_success(self):
        if self._body is None:
            return False
        elif self._command.command_type in [Type.CONTROL, Type.SET]:
            return self._body == 'ok'
        else:
            return True

    @property
    def is_set(self):
        return self.body is not None

    @property
    def is_timeout(self):
        return self._timestamp + self._timeout < datetime.now()

    def tostring(self):
        return '\n'.join([
            'type: %s' % self._command.command_type,
            'command: %s' % self._command.construct(self._command_args),
            'address: %s:%s' % (self._addr[0], self._addr[1]),
            'body: %s' % str(self._body),
            'timestamp: %s' % str(self._timestamp),
            'duration: %s' % str(self._duration),
        ])


class State:
    types = {
        'mid': int, 'x': int, 'y': int, 'z': int,
        'mpry': lambda x: np.array([float(i) for i in x.split(',')]),
        'pitch': int, 'roll': int, 'yaw': int,
        'vgx': int, 'vgy': int, 'vgz': int,
        'templ': int, 'temph': int,
        'tof': int,
        'h': int,
        'bat': int,
        'baro': float,
        'time': int,
        'agx': float, 'agy': float, 'agz': float,
    }

    def __init__(self, data, addr):
        if isinstance(data, bytes):
            data = data.decode()
        self._states = {item[0]: self.types[item[0]](item[1]) for item
                        in [state.split(':') for state in data.strip().split(';')] if item[0] != ''}
        self._states['timestamp'] = datetime.now()
        self._states['addr'] = addr

    def __getattr__(self, name):
        if name in self._states:
            return self._states[name]

    def tostring(self):
        return '\n'.join(['%s: %s' % (key, value) for key, value in self._states.items()])


class VideoFrame:
    def __init__(self, data, addr):
        self._body = data
        self._timestamp = datetime.now()
        self._addr = addr

    @property
    def body(self):
        return self._body

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def addr(self):
        return self._addr

    def tostring(self):
        return '\n'.join([
            'timestamp: %s' % self.timestamp,
            'address: %s' % self.addr,
            'frame: %s' % self.body,
        ])


class Manager:
    def __init__(self, managed_class, buff_size=100):
        self._managed_class = managed_class
        self._items = []
        self._buff_size = buff_size

    @property
    def latest(self):
        if len(self._items) == 0:
            return None
        else:
            return self._items[-1]

    def append(self, item):
        self._items.append(item)
        while len(self._items) > self._buff_size:
            self._items.pop(0)
        # logger.debug('number of items in %s: %s' % (self.__class__.__name__, len(self._items)))

    def create(self, *args):
        # logger.debug('create item: %s' % self.__class__.__name__)
        item = self._managed_class(*args)
        self.append(item)
        return item


class ResponseManager(Manager):
    def __init__(self, managed_class=Response, buff_size=100):
        super().__init__(managed_class, buff_size)


class StateManager(Manager):
    def __init__(self, managed_class=State, buff_size=100):
        super().__init__(managed_class, buff_size)


class VideoManager(Manager):
    def __init__(self, managed_class=VideoFrame, buff_size=10):
        super().__init__(managed_class, buff_size)
