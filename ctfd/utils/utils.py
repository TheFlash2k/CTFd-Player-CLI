import os
from dotenv import load_dotenv
import random
import string
import json
import shutil

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

def get_config(_config_path: str) -> dict:

    if not os.path.exists(_config_path) and not os.path.exists("/tmp/.ctfd.cache"):
        return {}
    
    if os.path.exists("/tmp/.ctfd.cache") and not os.path.exists(_config_path):
        with open("/tmp/.ctfd.cache") as f:
            _config_path = os.path.join(f.read().strip(), "config.json")

    try:
        with open(_config_path) as fp:
            _ = json.load(fp)
    except FileNotFoundError:
        return {}
        
    return _

def write_config(_key: str, _value: dict, _config: str, mode: str = "w") -> None:

    if mode == "a": # a acts as update for existing attributes as well.
        _ = get_config(_config)
        _[_key] = _value
        _value = _
    elif mode == "w":
        _value = {_key: _value}

    with open(_config, "w") as fp:
        json.dump(_value, fp, indent=4)

def update_challenge(_config: str, _id: int, _key: str, _value: str) -> None:
    _ = get_config(_config)
    
    _ = _.get("Challenges", [])
    if not _:
        return

    for i in range(len(_)):
        if _[i]["id"] == _id:
            _[i][_key] = _value
            break

    write_config("Challenges", _, _config, mode="a")

def update_template(_src: str, _dst: str, _id: int, _config: str) -> None:

    """
    This could be done in a better way but if it works, it works.
    """
    content = ""
    with open(_src) as fp:
        content = fp.read()

    content = content.format(CHALLENGE_ID=_id, CONFIG_DIR=_config)

    with open(_dst, "w") as fp:
        fp.write(content)
    
    os.chmod(_dst, 0o755)