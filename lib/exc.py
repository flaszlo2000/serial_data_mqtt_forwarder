from serial import SerialException

# TODO: make proper exception files 


class IncorrectFallbackTypeException(Exception):
    ...


class ConfigurationException(Exception):
    ...

class MissingConfigurationException(ConfigurationException):
    ...

class IncorrectConfigurationException(ConfigurationException):
    ...


class DataForwarderConnectionException(Exception):
    ...


class SerialDeviceNotFoundException(FileNotFoundError):
    ...

class IncompatibleSerialDeviceException(SerialException):
    ...


class SchedulerConfigException(Exception):
    ...
