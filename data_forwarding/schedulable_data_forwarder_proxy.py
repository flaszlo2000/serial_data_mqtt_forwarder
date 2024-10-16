from data_forwarding import T_DTO, DataForwarderBase, DataForwarderProxyBase
from data_forwarding.scheduling.forwarding_scheduler import ConfiguredScheduler


class SchedulableDataForwarderProxy(DataForwarderProxyBase[T_DTO]):
    """
    Schedulable data forwarder is needed when a sensor sends it's data in different intervals then we would like to forward it.
    Important: We can't assume every connected sensor's data sending interval can be fine-tuned or even just modified.

    With the given scheduler we can decide and even fine-tune the data sending rate 
    (which way it becomes modifyable from outside thus we could configure the responsiveness of our applications)
    """
    def __init__(self, data_forwarder: DataForwarderBase[T_DTO], configured_scheduler: ConfiguredScheduler) -> None:
        super().__init__(data_forwarder)

        self.configured_scheduler = configured_scheduler

    def send(self, data_dto: T_DTO) -> bool:
        ...
    
    def connect(self) -> bool:
        return self.data_forwarder.connect()
