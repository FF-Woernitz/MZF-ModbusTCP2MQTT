from pyModbusTCP.server import DataBank

from config import Config
from consts import *

logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class ModbusDataBank(DataBank):

    def __init__(self, mqtt_queue, backup_config=None):
        self.mqtt_queue = mqtt_queue
        self.config = Config()

        super().__init__(coils_size=self.config[CONF_MODBUS_COIL_SIZE], d_inputs_size=self.config[CONF_MODBUS_DINP_SIZE], h_regs_size=0,
                         i_regs_size=0)
        if backup_config is not None:
            self.set_coils(0, backup_config["coils"])
            self.set_discrete_inputs(0, backup_config["dinps"])

    def on_coils_change(self, address, from_value, to_value, srv_info):
        logger.info(f'Modbus change on Coil [{from_value} => {to_value}] at {address}')
        self.mqtt_queue.put([MQTT_STATE_TOPIC.format(self.config[CONF_MQTT_BASE_TOPIC], "coil", str(address)), to_value])

    def init(self):
        for i in range(self.config[CONF_MODBUS_COIL_SIZE]):
            self.mqtt_queue.put([MQTT_STATE_TOPIC.format(self.config[CONF_MQTT_BASE_TOPIC], "coil", str(i)), self.get_coils(i)[0]])
        for i in range(self.config[CONF_MODBUS_DINP_SIZE]):
            self.mqtt_queue.put(
                [MQTT_STATE_TOPIC.format(self.config[CONF_MQTT_BASE_TOPIC], "dinp", str(i)), self.get_discrete_inputs(i)[0]])

    def get_backup_config(self):
        conf = {
            "coils": self.get_coils(0, self.config[CONF_MODBUS_COIL_SIZE]),
            "dinps": self.get_discrete_inputs(0, self.config[CONF_MODBUS_DINP_SIZE])
        }
        return conf
