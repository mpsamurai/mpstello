__author__ = 'Junya Kaneko <junya@mpsamurai.org>'


import sys
import logging
import inspect


logger = logging.getLogger(__name__)


class ExecutorThreadDoesNotExist(Exception):
    pass


class ExecutorThreadAlreadyExist(Exception):
    pass


class Type:
    CONTROL = 'control'
    READ = 'read'
    SET = 'set'


class Command:
    name = ''
    command_type = ''
    return_type = str

    def __init__(self, socket, addr, response_manager, timeout):
        self._socket = socket
        self._addr = addr
        self._response_manager = response_manager
        self._timeout = timeout

    def construct(self, *args):
        command = self.name + ' ' + ' '.join([str(arg) for arg in args])
        return command.strip()

    def execute(self, *args):
        self._response_manager.create(self, args, self._timeout)
        command = self.construct(*args)
        logger.debug('send %s' % command)
        self._socket.sendto(command.encode(), self._addr)

    def __call__(self, *args):
        return self.execute(*args)


class CommandMode(Command):
    name = 'command'
    return_type = str
    command_type = Type.CONTROL

    def execute(self):
        return super().execute()


class Takeoff(Command):
    name = 'takeoff'
    return_type = str
    command_type = Type.CONTROL

    def execute(self):
        return super().execute()


class Land(Command):
    name = 'land'
    return_type = str
    command_type = Type.CONTROL

    def execute(self):
        return super().execute()


class Up(Command):
    name = 'up'
    return_type = str
    command_type = Type.CONTROL

    def execute(self, x):
        return super().execute(x)


class Down(Command):
    name = 'down'
    return_type = str
    command_type = Type.CONTROL

    def execute(self, x):
        return super().execute(x)


class Forward(Command):
    name = 'forward'
    return_type = str
    command_type = Type.CONTROL

    def execute(self, x):
        return super().execute(x)


class Back(Command):
    name = 'back'
    return_type = str
    command_type = Type.CONTROL

    def execute(self, x):
        return super().execute(x)


class Left(Command):
    name = 'left'
    return_type = str
    command_type = Type.CONTROL

    def execute(self, x):
        return super().execute(x)


class Right(Command):
    name = 'right'
    return_type = str
    command_type = Type.CONTROL

    def execute(self, x):
        return super().execute(x)


class ClockWise(Command):
    name = 'cw'
    return_type = str
    command_type = Type.CONTROL

    def execute(self, x):
        return super().execute(x)


class CounterClockWise(Command):
    name = 'ccw'
    return_type = str
    command_type = Type.CONTROL

    def execute(self, x):
        return super().execute(x)


class Go(Command):
    name = 'go'
    return_type = str
    command_type = Type.CONTROL

    def execute(self, x, y, z, speed):
        return super().execute(x, y, z, speed)


class Stop(Command):
    name = 'stop'
    return_type = str
    command_type = Type.CONTROL

    def execute(self):
        return super().execute()


class StreamOn(Command):
    name = 'streamon'
    return_type = str
    command_type = Type.CONTROL


class StreamOff(Command):
    name = 'streamoff'
    return_type = str
    command_type = Type.CONTROL


class Executor:
    def __init__(self, socket, addr, response_manager, timeout):
        self._commands = self._load_commands(socket, addr, response_manager, timeout)

    @staticmethod
    def _load_commands(socket, addr, response_manager, timeout):
        commands = {}
        for name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
            if name == 'Command':
                continue
            elif issubclass(cls, Command):
                commands[cls.name] = cls(socket, addr, response_manager, timeout)
        logging.debug('loaded commands: %s' % commands)
        return commands

    def execute(self, name, *args):
        self._commands[name](args)

    def __getattr__(self, name):
        if name in self._commands:
            return self._commands[name]
