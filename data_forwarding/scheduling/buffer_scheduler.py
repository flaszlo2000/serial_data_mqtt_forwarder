from typing import Any, Dict, Optional

from data_forwarding.scheduling import (ConfiguredScheduler,
                                        SchedulerConfiguration)


class BufferScheduler(ConfiguredScheduler):
    def __init__(self, config: SchedulerConfiguration, data_buffer: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)

        self.__topic_data_buffer: Dict[str, Any] = data_buffer or dict()
    