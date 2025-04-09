import json
import os
from queue import Queue
from time import sleep

import paho.mqtt.client as mqtt
from pyModbusTCP.server import ModbusServer, DeviceIdentification

from ModBusDataBank import ModbusDataBank
from ModBusDataHandler import ModbusDataHandler
from config import *
from consts import *


def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe(
        [
            (MQTT_COMMAND_TOPIC.format(MQTT_BASETOPIC, "coil", "+"), 0),
            (MQTT_COMMAND_TOPIC.format(MQTT_BASETOPIC, "dinput", "+"), 0)
        ]
    )
    client.publish(
        MQTT_PROGRAM_STATUS.format(MQTT_BASETOPIC), MQTT_AVAILABLE, retain=True
    )


def on_message_cmd(mqtt_client, data_object, msg):
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

    if type == "coil" and id < MODBUS_COIL_SIZE:
        data_object["databank"].set_coils(id, [payload])
        data_object["mqtt_queue"].put([MQTT_STATE_TOPIC.format(MQTT_BASETOPIC, "coil", str(id)), payload])
        print(f"Update from MQTT: coil_{id}: {payload}")
    elif type == "dinput" and id < MODBUS_DINPUTS_SIZE:
        data_object["databank"].set_discrete_inputs(id, [payload])
        data_object["mqtt_queue"].put([MQTT_STATE_TOPIC.format(MQTT_BASETOPIC, "dinput", str(id)), payload])
        print(f"Update from MQTT: dinput_{id}: {payload}")
    else:
        return ValueError("Invalid Argument")


def create_mqtt_client(databank, mqtt_queue):
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                        client_id="MZF-ModbusRTU2MQTT",
                        userdata={
                            "databank": databank,
                            "mqtt_queue": mqtt_queue
                        }
    )

    mqttc.will_set(
        MQTT_PROGRAM_STATUS.format(MQTT_BASETOPIC), MQTT_NOT_AVAILABLE, retain=True
    )
    mqttc.on_connect = on_connect

    mqttc.message_callback_add(
        MQTT_COMMAND_TOPIC.format(MQTT_BASETOPIC, "coil", "+"), on_message_cmd
    )
    mqttc.message_callback_add(
        MQTT_COMMAND_TOPIC.format(MQTT_BASETOPIC, "dinput", "+"), on_message_cmd
    )

    if MQTT_USER != '':
        mqttc.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    mqttc.connect(MQTT_SERVER, MQTT_PORT, 180)
    return mqttc


def main():
    mqttc = None
    server = None
    databank = None
    backup = None

    if os.path.isfile(BACKUP_FILE):
        with open(BACKUP_FILE) as f:
            backup = json.load(f)
    try:
        mqtt_queue = Queue()

        databank = ModbusDataBank(mqtt_queue, backup)
        device_identification = DeviceIdentification(vendor_name=b"FF-Woernitz", product_code=b"ModBus2MQTT", major_minor_revision=b"1.0.0", product_name=b"test1", objects_id={0: b'test1', 2: b'test2'})
        server = ModbusServer(host="0.0.0.0", port=502, data_hdl=ModbusDataHandler(databank), device_id=device_identification, no_block=True)

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
            with open(BACKUP_FILE, "w") as f:
                json.dump(databank.get_backup_config(), f)
        print("Shutting down")


if __name__ == "__main__":
    main()
