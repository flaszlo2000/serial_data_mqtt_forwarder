from data_forwarding.data_forwarding import T_DTO, DataForwarderBase


class DataForwarderProxyBase(DataForwarderBase[T_DTO]):
    "Base class for data forwarder proxies"

    def __init__(self, data_forwarder: DataForwarderBase[T_DTO]) -> None:
        super().__init__()

        self.data_forwarder = data_forwarder
