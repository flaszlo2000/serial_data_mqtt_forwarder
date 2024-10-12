from serial import SerialException


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
