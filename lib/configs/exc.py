from serial import SerialException


class ConfigurationException(Exception):
    ...

class MissingConfigurationException(ConfigurationException):
    ...

class IncorrectConfigurationException(ConfigurationException):
    ...


class SerialDeviceNotFoundException(FileNotFoundError):
    ...

class IncompatibleSerialDeviceException(SerialException):
    ...
