from .logger import logger
from .handler import RequestHandler, Mode, requests
from .utils import get_env, fix_url

class CTFd:
    def __init__(self, instance: str, token: str, skip: bool = False):
        
        self.ctfd_instance = get_env(key="CTFD_URL", curr=instance, err_msg="Environment variable \"CTFD_URL\" is not set")
        self.ctfd_token = get_env(key="CTFD_TOKEN", curr=token, err_msg="Environment variable \"CTFD_TOKEN\" is not set")

        if len(self.ctfd_instance) == 0 or len(self.ctfd_token) == 0:
            logger.error("CTFd instance/token is not set.")
            exit(1)

        self.ctfd_instance = fix_url(url=self.ctfd_instance)

        if not skip:
            logger.info(f"CTFd url: {self.ctfd_instance}")
            logger.info(f"Checking connection to CTFd version.")
            if not self.is_working():
                logger.error("CTFd instance is not working.")
                exit(1)
            else:
                logger.info("CTFd instance is working.")

    def is_working(self):
        r = RequestHandler.MakeRequest(
            mode=Mode.GET,
            url=f"{self.ctfd_instance}/api/v1/users",
            token=self.ctfd_token
        )
        return r.status_code == 200

class ChallengeModel:
    """
    Simple model for the challenges deployed on the CTFd instance.
    """
    def __init__(self, id: int, name: str, category: str, type: str, is_downloaded = False, **kwargs):
        self.id = id
        self.name = name
        self.category = category
        self.type = type
        self.is_downloaded = is_downloaded

    def __str__(self):
        return f"Challenge: {self.name} ({self.id})"
    
    def __repr__(self):
        return f"Challenge: {self.name} ({self.id})"

    def __dict__(self, no_id=False):
        _ = {
            "name": self.name,
            "category": self.category,
            "type": self.type,
            "is_downloaded": self.is_downloaded
        }
        if not no_id: _["id"] = self.id
        return _

class CTFd_Handler:
    """ This class' methods will be used for interaction with the CTFd instance. """
    def __init__(self, instance: str, token: str, skip: bool = False):
        self.ctfd = CTFd(instance=instance, token=token, skip=skip)
    
    def get_challenges(self) -> list:
        """
        Returns the list of all the challenges currently deployed
        """
        return RequestHandler.MakeRequest(
            mode=Mode.GET,
            url=f"{self.ctfd.ctfd_instance}/api/v1/challenges",
            token=self.ctfd.ctfd_token
        ).json()["data"]

    def get_challenge(self, chal_id: int) -> dict:
        """
        Returns the challenge with the given id.
        """
        _ = RequestHandler.MakeRequest(
            mode=Mode.GET,
            url=f"{self.ctfd.ctfd_instance}/api/v1/challenges/{chal_id}",
            token=self.ctfd.ctfd_token
        ).json()
        if "message" in _.keys():
            return {}
        return _["data"]
    
    def download_file(self, endpoint, filename) -> bytes:
        """
        Downloads the file from the given url.
        """
        with requests.get(f"{self.ctfd.ctfd_instance}{endpoint}", stream=True, allow_redirects=True) as r:
            r.raise_for_status()
            total_length = int(r.headers.get('content-length'))
            downloaded = 0
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    print(f"\r[\x1b[32;20mDOWNLOADING\x1b[0m] {downloaded}/{total_length} bytes downloaded", end="")
            print("\r", end="")
            logger.info(f"File downloaded to {filename}")

    def submit_flag(self, chal_id: int, flag: str) -> dict:
        """
        Submits the flag for the challenge with the given id.
        """
        return RequestHandler.MakeRequest(
            mode=Mode.POST,
            url=f"{self.ctfd.ctfd_instance}/api/v1/challenges/attempt",
            token=self.ctfd.ctfd_token,
            json={"challenge_id": chal_id, "submission": flag}
        ).json()["data"]
    
    def start_instance(self, chal_id: int) -> dict:
        """
        Starts the challenge instance.
        """
        return RequestHandler.MakeRequest(
            mode=Mode.POST,
            url=f"{self.ctfd.ctfd_instance}/containers/api/request",
            token=self.ctfd.ctfd_token,
            json={"chal_id": chal_id}
        ).json()
    
    def extend_instance(self, chal_id: int) -> dict:
        """
        Extends the challenge instance.
        """
        return RequestHandler.MakeRequest(
            mode=Mode.POST,
            url=f"{self.ctfd.ctfd_instance}/containers/api/renew",
            token=self.ctfd.ctfd_token,
            json={"chal_id": chal_id}
        ).json()
    
    def stop_instance(self, chal_id: int) -> dict:
        """
        Stops the challenge instance.
        """
        return RequestHandler.MakeRequest(
            mode=Mode.POST,
            url=f"{self.ctfd.ctfd_instance}/containers/api/stop",
            token=self.ctfd.ctfd_token,
            json={"chal_id": chal_id}
        ).json()