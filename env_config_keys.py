from enum import Enum


class EnvConfigKey(str, Enum):
    MSG_QUEUE_SIZE = "msg_queue_size"
    
    MQTT_USERNAME = "mqtt_username"
    MQTT_PASSWORD = "mqtt_password"
    MQTT_IP = "mqtt_ip"
    MQTT_PORT = "mqtt_port"
    MQTT_KEEPALIVE = "mqtt_keepalive"