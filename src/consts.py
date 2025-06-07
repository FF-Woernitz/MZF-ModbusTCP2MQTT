import logging
import voluptuous as vol

"""Constants common the various modules."""
VERSION = "0.1.0"
ENV_PREFIX = "M2M_"

CONF_CONFIG = "config"
CONF_CONFIG_EXAMPLE = "config_example"
CONF_BACKUP_FILE = "backup_file"
CONF_MQTT_SERVER = "mqtt_server"
CONF_MQTT_PORT = "mqtt_port"
CONF_MQTT_USERNAME = "mqtt_username"
CONF_MQTT_PASSWORD = "mqtt_password"
CONF_MQTT_BASE_TOPIC = "mqtt_base_topic"
CONF_MODBUS_COIL_SIZE = "modbus_coil_size"
CONF_MODBUS_DINP_SIZE = "modbus_dinp_size"
CONF_MODBUS_ALLOWED_IPS = "modbus_allowed_ips"
CONF_LOG_LEVEL = "log_level"
CONF_LOG_COLOR = "log_color"

DEFAULT_CONFIG_FILE = "config.yaml"
DEFAULT_BACKUP_FILE = "backup.json"
DEFAULT_MQTT_SERVER = "127.0.0.1"
DEFAULT_MQTT_PORT = 1883
DEFAULT_MQTT_USERNAME = ""
DEFAULT_MQTT_PASSWORD = ""
DEFAULT_MQTT_BASE_TOPIC = "modbus2mqtt"
DEFAULT_MODBUS_COIL_SIZE = 16
DEFAULT_MODBUS_DINP_SIZE = 16
DEFAULT_MODBUS_ALLOWED_IPS = []
DEFAULT_LOG_LEVEL = "info"
DEFAULT_LOG_COLOR = False

LIST_CONFS = ["MODBUS_ALLOWED_IPS"]

ALL_SUPPORTED_LOG_LEVELS = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}

RESET_COLOR = "\x1b[0m"
RED_COLOR = "\x1b[31;21m"
YELLOW_COLOR = "\x1b[33;21m"
LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s{}".format(RESET_COLOR)

CONF_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_BACKUP_FILE, default=DEFAULT_BACKUP_FILE): str,
        vol.Required(CONF_MQTT_SERVER, default=DEFAULT_MQTT_SERVER): str,
        vol.Optional(CONF_MQTT_PORT, default=DEFAULT_MQTT_PORT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=65535)
        ),
        vol.Optional(CONF_MQTT_USERNAME, default=DEFAULT_MQTT_USERNAME): str,
        vol.Optional(CONF_MQTT_PASSWORD, default=DEFAULT_MQTT_PASSWORD): str,
        vol.Optional(CONF_MQTT_BASE_TOPIC, default=DEFAULT_MQTT_BASE_TOPIC): str,

        vol.Required(CONF_MODBUS_COIL_SIZE, default=DEFAULT_MODBUS_COIL_SIZE): int,
        vol.Required(CONF_MODBUS_DINP_SIZE, default=DEFAULT_MODBUS_DINP_SIZE): int,
        vol.Optional(CONF_MODBUS_ALLOWED_IPS, default=DEFAULT_MODBUS_ALLOWED_IPS): [str],
        vol.Optional(CONF_LOG_LEVEL, default=DEFAULT_LOG_LEVEL): vol.In(
            ALL_SUPPORTED_LOG_LEVELS
        ),
        vol.Optional(CONF_LOG_COLOR, default=DEFAULT_LOG_COLOR): bool,
    },
    extra=False,
)

MQTT_PROGRAM_STATUS = "{}/status"
MQTT_STATE_TOPIC = "{}/{}/{}/value"
MQTT_COMMAND_TOPIC = "{}/{}/{}/set"

MQTT_PAYLOAD_ON = [b"on", b"an", b"1", b"true"]
MQTT_PAYLOAD_OFF = [b"off", b"aus", b"0", b"false"]
MQTT_AVAILABLE = "online"
MQTT_NOT_AVAILABLE = "offline"


class SetupError(Exception):
    pass
