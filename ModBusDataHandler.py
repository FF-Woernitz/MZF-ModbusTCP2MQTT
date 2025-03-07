from pyModbusTCP.constants import EXP_ILLEGAL_FUNCTION
from pyModbusTCP.server import DataHandler

from config import ALLOWED_IPS


class ModbusDataHandler(DataHandler):
    def read_coils(self, address, count, srv_info):
        if srv_info.client.address in ALLOWED_IPS:
            return super().read_coils(address, count, srv_info)
        else:
            print(f"Refused client from {srv_info.client.address}! Not in whitelist.")
            return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)

    def write_coils(self, address, bits_l, srv_info):
        if srv_info.client.address in ALLOWED_IPS:
            return super().write_coils(address, bits_l, srv_info)
        else:
            print(f"Refused client from {srv_info.client.address}! Not in whitelist.")
            return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)

    def read_d_inputs(self, address, count, srv_info):
        if srv_info.client.address in ALLOWED_IPS:
            return super().read_d_inputs(address, count, srv_info)
        else:
            print(f"Refused client from {srv_info.client.address}! Not in whitelist.")
            return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)

    def read_h_regs(self, address, count, srv_info):
        return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)

    def write_h_regs(self, address, words_l, srv_info):
        return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)

    def read_i_regs(self, address, count, srv_info):
        return DataHandler.Return(exp_code=EXP_ILLEGAL_FUNCTION)