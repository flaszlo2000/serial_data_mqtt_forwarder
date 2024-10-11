from queue import Queue
from signal import SIGINT, signal
from threading import Event, Thread
from typing import Final

from dotenv import load_dotenv

from config import Config
from data_forwarding import DataForwarderBase, DataInputDTO
from mqtt_handler import MqttDataForwarder, MqttDataInputDTO


def data_forwarder_thread(data_forwarder: DataForwarderBase[DataInputDTO], msg_queue: "Queue[DataInputDTO]", stop_event: Event, *, polling_interval: float = 0.1) -> None:
    "Forwards data thru the data_forwarder on the given queue. This is designed to be run on a separate thread"

    while not stop_event.wait(polling_interval):
        if msg_queue.empty(): continue
        
        while not msg_queue.empty():
            sent = data_forwarder.send(msg_queue.get_nowait())

            if not sent:
                #! TODO: logging + retry
                pass

def _gracefulExit(stop_event: Event) -> None:
    stop_event.set()

def main() -> None:
    config: Final[Config] = Config()
    message_queue: Queue[MqttDataInputDTO] = Queue(maxsize = config.msg_queue_size)
    stop_event = Event()
    mqtt_data_forwarder = MqttDataForwarder(config.getMqttConfig())

    mqtt_handler_thread = Thread(target = data_forwarder_thread, args = [mqtt_data_forwarder, message_queue, stop_event])


    signal(SIGINT, lambda _, __: _gracefulExit(stop_event))
    mqtt_handler_thread.start()

if __name__ == "__main__":
    load_dotenv()
    main()