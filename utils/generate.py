import requests
import re
from .utils import fix_url, get_env
from .logger import logger
from datetime import datetime

class GenerateToken(object):
    def __init__(self, url, username, password):
        self.username = username
        self.password = password

        self.url = fix_url(
            get_env(
                key = "CTFD_URL",
                curr = url,
                err_msg = "Environment variable \"CTFD_URL\" is not set"
            ))
        self.session = requests.Session()

    def __get_csrf_nonce(self, page = ""):
        r = self.session.get(f"{self.url}{page}")
        return re.findall("'csrfNonce': \"(.*?)\"", r.text)[0]

    def _login(self):
        logger.info(f"Logging in as: {self.username}")

        r = self.session.post(f"{self.url}/login", data={
			"name": self.username,
			"password": self.password,
			"_submit": "Submit",
			"nonce": self.__get_csrf_nonce()
		})

        if r.status_code != 200 and r.status_code != 302:
            logger.error(f"Unable to login!\nError: {r.text}")
            exit(1)

        logger.info(f"Logged in successfully as {self.username}")

    def generate_token(self) -> str:
        """
        Returns:
            The Token that will be used to interact with CTFd
        """

        # Expire 1 year from now
        date_now = datetime.now()
        expiry = date_now.replace(year=(date_now.year + 1)).strftime('%Y-%m-%d')
        
        self._login()

        logger.info("Generating token.")
        r = self.session.post(
            f"{self.url}/api/v1/tokens", json = {
                "description": "Token generated by TheFlash2k's Auto CTFd",
                "expiration": expiry
            }, headers = {
                "CSRF-Token": self.__get_csrf_nonce()
            }
        )

        if r.status_code != 200:
            logger.error(f"Unable to generate token. Error: {r.text}")
            exit(1)
        
        token = r.json()["data"]["value"]
        logger.info(f"Generated token: {token}")

        return token