from logging import Logger

from data_forwarding.data_forwarder_proxy import DataForwarderProxyBase
from data_forwarding.data_forwarding_base import T_DTO, DataForwarderBase
from scheduling.scheduler_base import ConfiguredScheduler


class SchedulableDataForwarderProxy(DataForwarderProxyBase[T_DTO]):
    """
    Schedulable data forwarder is needed when a sensor sends it's data in different intervals then we would like to forward it.
    Important: We can't assume every connected sensor's data sending interval can be fine-tuned or even just modified.

    With the given scheduler we can decide and even fine-tune the data sending rate 
    (which way it becomes modifyable from outside thus we could configure the responsiveness of our applications)
    """
    def __init__(self, data_forwarder: DataForwarderBase[T_DTO], configured_scheduler: ConfiguredScheduler[T_DTO], logger: Logger) -> None:
        super().__init__(data_forwarder)

        self.configured_scheduler = configured_scheduler
        self.logger = logger

    def __schedulerCallback(self, data_dto: T_DTO) -> None:
        success = self.data_forwarder.send(data_dto)

        if success:
            self.logger.info(f"Successfully forwarder message from scheduler to {data_dto.destination}!")
        else:
            self.logger.warning(f"Message ({data_dto}) from scheduler could not be sent, retrying")

            self.data_forwarder.retySend(data_dto)

    def send(self, data_dto: T_DTO) -> bool:
        self.configured_scheduler.schedule(data_dto, self.__schedulerCallback)
 
        self.logger.info("Data scheduled to be forwarded!")
        
        return False
    
    def connect(self) -> bool:
        return self.data_forwarder.connect()

    def retySend(self, data_dto: T_DTO) -> None:
        pass # intentionally left empty, real retrySend calls will be handled in the data_forwarder
