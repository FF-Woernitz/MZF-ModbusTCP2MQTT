from pyModbusTCP.constants import EXP_ILLEGAL_FUNCTION
from pyModbusTCP.server import DataHandler

from .consts import *
from .config import Config

logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class ModbusDataHandler(DataHandler):
    def __init__(self):
        super()
        self.config = Config()
        logger.setLevel(ALL_SUPPORTED_LOG_LEVELS[self.config[CONF_LOG_LEVEL]])

    def read_coils(self, address, count, srv_info):
        logger.debug(f"Client {srv_info.client.address} read coils. Start: {address} Count: {count}")
        if srv_info.client.address in self.config[CONF_MODBUS_ALLOWED_IPS]:
            return super().read_coils(address, count, srv_info)
        else:
            logger.warning(f"Refused client from {srv_info.client.address}! Not in whitelist.")
            return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)

    def write_coils(self, address, bits_l, srv_info):
        logger.debug(f"Client {srv_info.client.address} write coils. Start: {address} Bits: {bits_l}")
        if srv_info.client.address in self.config[CONF_MODBUS_ALLOWED_IPS]:
            return super().write_coils(address, bits_l, srv_info)
        else:
            logger.warning(f"Refused client from {srv_info.client.address}! Not in whitelist.")
            return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)

    def read_d_inputs(self, address, count, srv_info):
        logger.debug(f"Client {srv_info.client.address} read dinputs. Start: {address} Count: {count}")
        if srv_info.client.address in self.config[CONF_MODBUS_ALLOWED_IPS]:
            return super().read_d_inputs(address, count, srv_info)
        else:
            logger.warning(f"Refused client from {srv_info.client.address}! Not in whitelist.")
            return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)

    def read_h_regs(self, address, count, srv_info):
        return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)

    def write_h_regs(self, address, words_l, srv_info):
        return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)

    def read_i_regs(self, address, count, srv_info):
        return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION
)