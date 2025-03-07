from pyModbusTCP.server import DataBank

from config import MODBUS_COIL_SIZE, MODBUS_DINPUTS_SIZE, MQTT_BASETOPIC
from consts import MQTT_STATE_TOPIC


class ModbusDataBank(DataBank):

    def __init__(self, mqtt_queue, backup_config=None):
        self.mqtt_queue = mqtt_queue

        if backup_config is None:
            super().__init__(coils_size=MODBUS_COIL_SIZE, d_inputs_size=MODBUS_DINPUTS_SIZE, h_regs_size=0,
                             i_regs_size=0)
        else:
            super().__init__(coils_size=len(backup_config["coils"]), d_inputs_size=len(backup_config["dinput"]),
                             h_regs_size=0, i_regs_size=0)
            self.set_coils(0, backup_config["coils"])
            self.set_discrete_inputs(0, backup_config["dinput"])

    def on_coils_change(self, address, from_value, to_value, srv_info):
        msg = 'change in coil space [{0!r:^5} > {1!r:^5}] at @ 0x{2:04X}'
        print(msg.format(from_value, to_value, address))
        self.mqtt_queue.put([MQTT_STATE_TOPIC.format(MQTT_BASETOPIC, f"coil_{address}"), to_value])

    def init(self):
        for i in range(MODBUS_COIL_SIZE):
            self.mqtt_queue.put([MQTT_STATE_TOPIC.format(MQTT_BASETOPIC, f"coil_{i}"), self.get_coils(i)[0]])
        for i in range(MODBUS_DINPUTS_SIZE):
            self.mqtt_queue.put(
                [MQTT_STATE_TOPIC.format(MQTT_BASETOPIC, f"dinput_{i}"), self.get_discrete_inputs(i)[0]])

    def get_backup_config(self):
        conf = {
            "coils": self.get_coils(0, MODBUS_COIL_SIZE),
            "dinput": self.get_discrete_inputs(0, MODBUS_DINPUTS_SIZE)
        }
        return conf
