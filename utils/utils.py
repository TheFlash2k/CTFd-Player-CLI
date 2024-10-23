import os
from dotenv import load_dotenv
import random
import string
from configparser import ConfigParser

def random_string(length: int = 10) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_env(key: str, curr: str = None, default: str = None, err_msg: str = None) -> str:
    load_dotenv()
    if curr != None:
        return curr
    value = os.getenv(key, default)
    if value is None or value == "" or len(value) == 0:
        raise Exception(f"{err_msg}")
    return value

def fix_url(url: str) -> str:
    if url.endswith("/"):
        url = url[:-1]
        
    if (not url.startswith("http://")) and (not url.startswith("https://")):
        url = f"http://{url}"

    return url

def get_config(_config) -> ConfigParser:

    if not os.path.exists(_config):
        return None
    config = ConfigParser()
    config.read(_config)
    return config

def write_config(_key: str, _value: dict, _config: str):
    config = ConfigParser()
    config[_key] = _value
    with open(_config, "w") as fp:
        config.write(fp)