import json
import os
from queue import Queue
from time import sleep

import paho.mqtt.client as mqtt
from pyModbusTCP.server import ModbusServer, DeviceIdentification

from .ModBusDataBank import ModbusDataBank
from .ModBusDataHandler import ModbusDataHandler

from .consts import *
from .config import Config

logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def on_connect(client, userdata, flags, reason_code, properties):
    config = Config()
    client.subscribe(
        [
            (MQTT_COMMAND_TOPIC.format(config[CONF_MQTT_BASE_TOPIC], "coil", "+"), 0),
            (MQTT_COMMAND_TOPIC.format(config[CONF_MQTT_BASE_TOPIC], "dinp", "+"), 0)
        ]
    )
    client.publish(
        MQTT_PROGRAM_STATUS.format(config[CONF_MQTT_BASE_TOPIC]), MQTT_AVAILABLE, retain=True
    )


def on_message_cmd(mqtt_client, data_object, msg):
    config = Config()

    data = msg.topic.split("/")
    type = data[1]
    id = data[2]

    if not str(id).isdecimal():
        return ValueError("Invalid ID")

    id = int(id)

    if msg.payload.lower() in MQTT_PAYLOAD_ON:
        payload = True
    elif msg.payload.lower() in MQTT_PAYLOAD_OFF:
        payload = False
    else:
        return ValueError("Invalid Argument")

    if type == "coil" and id < config[CONF_MODBUS_COIL_SIZE]:
        data_object["databank"].set_coils(id, [payload])
        data_object["mqtt_queue"].put([MQTT_STATE_TOPIC.format(config[CONF_MQTT_BASE_TOPIC], "coil", str(id)), payload])
        logger.info(f"Update from MQTT: coil_{id}: {payload}")
    elif type == "dinp" and id < config[CONF_MODBUS_DINP_SIZE]:
        data_object["databank"].set_discrete_inputs(id, [payload])
        data_object["mqtt_queue"].put([MQTT_STATE_TOPIC.format(config[CONF_MQTT_BASE_TOPIC], "dinp", str(id)), payload])
        logger.info(f"Update from MQTT: dinp_{id}: {payload}")
    else:
        return ValueError("Invalid Argument")


def create_mqtt_client(databank, mqtt_queue):
    config = Config()

    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                        client_id="MZF-Modbus2MQTT",
                        userdata={
                            "databank": databank,
                            "mqtt_queue": mqtt_queue
                        }
    )

    mqttc.will_set(
        MQTT_PROGRAM_STATUS.format(config[CONF_MQTT_BASE_TOPIC]), MQTT_NOT_AVAILABLE, retain=True
    )
    mqttc.on_connect = on_connect

    mqttc.message_callback_add(
        MQTT_COMMAND_TOPIC.format(config[CONF_MQTT_BASE_TOPIC], "coil", "+"), on_message_cmd
    )
    mqttc.message_callback_add(
        MQTT_COMMAND_TOPIC.format(config[CONF_MQTT_BASE_TOPIC], "dinp", "+"), on_message_cmd
    )

    if config[CONF_MQTT_USERNAME] != '':
        mqttc.username_pw_set(config[CONF_MQTT_USERNAME], config[CONF_MQTT_PASSWORD])

    mqttc.connect(config[CONF_MQTT_SERVER], config[CONF_MQTT_PORT], 180)
    return mqttc


def main(args):
    config = Config()
    config.setup(args)

    if config[CONF_LOG_COLOR]:
        logging.addLevelName(
            logging.WARNING,
            "{}{}".format(YELLOW_COLOR, logging.getLevelName(logging.WARNING)),
        )
        logging.addLevelName(
            logging.ERROR, "{}{}".format(RED_COLOR, logging.getLevelName(logging.ERROR))
        )

    logger.setLevel(ALL_SUPPORTED_LOG_LEVELS[config[CONF_LOG_LEVEL]])

    mqttc = None
    server = None
    databank = None
    backup = None

    if config[CONF_BACKUP_FILE] != "" and os.path.isfile(config[CONF_BACKUP_FILE]):
        with open(config[CONF_BACKUP_FILE]) as f:
            backup = json.load(f)
    try:
        mqtt_queue = Queue()

        databank = ModbusDataBank(mqtt_queue, backup)
        device_identification = DeviceIdentification(vendor_name=b"FF-Woernitz", product_code=b"ModBus2MQTT",
                                                     major_minor_revision=VERSION.encode())
        server = ModbusServer(host="0.0.0.0", port=502, data_hdl=ModbusDataHandler(databank),
                              device_id=device_identification, no_block=True)

        mqttc = create_mqtt_client(databank, mqtt_queue)
        mqttc.loop_start()

        server.start()
        databank.init()

        while True:
            if not mqtt_queue.empty():
                item = mqtt_queue.get()
                mqttc.publish(item[0], "ON" if item[1] else "OFF")
            else:
                sleep(0.1)

    except KeyboardInterrupt:
        if mqttc is not None:
            mqttc.loop_stop()
        if server is not None:
            server.stop()
        if databank is not None:
            if config[CONF_BACKUP_FILE] != "" and os.path.isfile(config[CONF_BACKUP_FILE]):
                with open(config[CONF_BACKUP_FILE], "w") as f:
                    json.dump(databank.get_backup_config(), f)
        logger.info("Shutting down")

