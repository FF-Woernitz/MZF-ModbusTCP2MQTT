import os

import yaml
import argparse

from src.consts import *
from src.modbus2mqtt import main

logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def load_config_file(path, create):
    """Load configuration from yaml file."""
    try:
        with open(path, "r") as infile:
            logger.info(f"Loading configuration from {path}")
            try:
                configuration = yaml.safe_load(infile)
                if not configuration:
                    logger.error(f"Error during loading configuration file {path}")
                    quit(1)
                config = CONF_SCHEMA(configuration)
            except vol.MultipleInvalid as error:
                logger.error(f"In configuration file {path}: {error}")
                quit(1)
    except FileNotFoundError:
        if create:
            logger.info("No configuration file found, creating a new one")
            try:
                with open(path, "w", encoding="utf8") as outfile:
                    yaml.dump(CONF_SCHEMA({}), outfile, default_flow_style=False, allow_unicode=True)
            except Exception as err:
                logger.error(f"Could not save configuration: {err}")
            logger.info("Example configuration has been created. Please edit the configuration now!")
            quit(0)
        else:
            logger.info("No configuration file found. Skipping configuration file.")
            config = CONF_SCHEMA({})
    return config


parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
parser.add_argument(f"--{CONF_CONFIG}", help="configuration file", default=DEFAULT_CONFIG_FILE)
parser.add_argument(
    f"--{CONF_CONFIG_EXAMPLE.replace('_', '-')}", help="create configuration file example", action='store_true',
    default=False
)
parser.add_argument(f"--{CONF_BACKUP_FILE.replace('_', '-')}", help="backup file")
parser.add_argument(f"--{CONF_MQTT_SERVER.replace('_', '-')}", help="MQTT server")
parser.add_argument(f"--{CONF_MQTT_PORT.replace('_', '-')}", help="MQTT port", type=int)
parser.add_argument(f"--{CONF_MQTT_USERNAME.replace('_', '-')}", help="MQTT username")
parser.add_argument(f"--{CONF_MQTT_PASSWORD.replace('_', '-')}", help="MQTT password")
parser.add_argument(f"--{CONF_MQTT_BASE_TOPIC.replace('_', '-')}", help="MQTT base topic")
parser.add_argument(f"--{CONF_MODBUS_COIL_SIZE.replace('_', '-')}", help="Count of Coils", type=int)
parser.add_argument(f"--{CONF_MODBUS_DINP_SIZE.replace('_', '-')}", help="Count of DInputs", type=int)
parser.add_argument(f"--{CONF_MODBUS_ALLOWED_IPS.replace('_', '-')}", help="Allowed IPs for modbus", action='append')
parser.add_argument(f"--{CONF_LOG_LEVEL.replace('_', '-')}", help="Log level", choices=ALL_SUPPORTED_LOG_LEVELS)
parser.add_argument(f"--{CONF_LOG_COLOR.replace('_', '-')}", help="Coloring output", action="store_true")

args = parser.parse_args()
args = vars(args)

CONFIG = load_config_file(args[CONF_CONFIG], args[CONF_CONFIG_EXAMPLE])

for _x in os.environ:
    if _x.startswith(ENV_PREFIX):
        env_prefix_len = len(ENV_PREFIX)
        if _x[env_prefix_len:].lower() not in CONFIG:
            logger.error(f"Invalid env parameter {_x}")
            exit(1)
        if CONFIG.get(_x[env_prefix_len:].lower()) != os.environ[_x]:
            if _x[env_prefix_len:].upper() in LIST_CONFS:
                CONFIG[_x[env_prefix_len:].lower()] = [s.strip() for s in os.environ[_x].split(",")]
                continue
            if type(CONFIG[_x[env_prefix_len:].lower()]) is int:
                CONFIG[_x[env_prefix_len:].lower()] = int(os.environ[_x])
            if type(CONFIG[_x[env_prefix_len:].lower()]) is bool:
                CONFIG[_x[env_prefix_len:].lower()] = bool(os.environ[_x])
            else:
                CONFIG[_x[env_prefix_len:].lower()] = os.environ[_x]

args.pop(CONF_CONFIG)
args.pop(CONF_CONFIG_EXAMPLE)
for key in args:
    if CONFIG.get(key) != args[key]:
        CONFIG[key] = args[key]

main(CONFIG)
