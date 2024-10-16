from serial import SerialException

# TODO: make proper exception files 


class IncorrectFallbackTypeException(Exception):
    ...

class MissingConfigurationException(Exception):
    ...

class DataForwarderConnectionException(Exception):
    ...

class SerialDeviceNotFoundException(FileNotFoundError):
    ...

class IncompatibleSerialDeviceException(SerialException):
    ...

class SchedulerConfigException(Exception):
    ...
