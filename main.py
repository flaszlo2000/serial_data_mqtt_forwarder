from queue import Queue
from signal import SIGINT, signal
from threading import Event, Thread
from typing import Final

from dotenv import load_dotenv

from config import Config
from mqtt_handler import MqttDataForwarder, MqttDataInputDTO


def mqtt_thread(config: Config, msg_queue: "Queue[MqttDataInputDTO]", stop_event: Event, *, polling_interval: float = 0.1) -> None:
    "Forwards data to mqtt based on the given queue. This is designed to be run on a separate thread"
    mqtt_data_forwarder = MqttDataForwarder()

    while not stop_event.wait(polling_interval):
        if msg_queue.empty(): continue
        
        while not msg_queue.empty():
            mqtt_data_forwarder.send(msg_queue.get_nowait())

def _gracefulExit(stop_event: Event) -> None:
    stop_event.set()

def main() -> None:
    config: Final[Config] = Config()
    message_queue: Queue[MqttDataInputDTO] = Queue(maxsize = config.msg_queue_size)
    stop_event = Event()

    mqtt_handler_thread = Thread(target = mqtt_thread, args = [config, message_queue, stop_event])


    signal(SIGINT, lambda _, __: _gracefulExit(stop_event))
    mqtt_handler_thread.start()

if __name__ == "__main__":
    load_dotenv()
    main()