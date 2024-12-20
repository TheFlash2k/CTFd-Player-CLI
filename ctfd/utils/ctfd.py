from .logger import logger
from .handler import RequestHandler, Mode, requests
from .utils import get_env, fix_url

class CTFd:
    """
    Class to interact with the CTFd instance.

    Attributes:
        ctfd_instance: The URL of the CTFd instance
        ctfd_token: The token to interact with the CTFd instance

    Methods:
        is_working: Checks if the CTFd instance is working
    """

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

    def is_working(self) -> bool:
        """
        Checks if the CTFd instance
        is working or not by making a request
        to the /api/v1/users endpoint.

        Returns:
            True if the CTFd instance is working
            False otherwise
        """
        r = RequestHandler.MakeRequest(
            mode=Mode.GET,
            url=f"{self.ctfd_instance}/api/v1/users",
            token=self.ctfd_token
        )
        return r.status_code == 200

class ChallengeModel:
    """
    Simple model for the challenges deployed on the CTFd instance.

    Attributes:
        id: The id of the challenge
        name: The name of the challenge
        category: The category of the challenge
        type: The type of the challenge
        is_downloaded: Whether the challenge is downloaded or not
    """
    def __init__(self, id: int, name: str, category: str, type: str, is_downloaded: bool = False, **kwargs):
        self.id = id
        self.name = name
        self.category = category
        self.type = type
        self.is_downloaded = is_downloaded

    def __str__(self):
        return f"Challenge: {self.name} ({self.id})"
    
    def __repr__(self):
        return f"Challenge: {self.name} ({self.id})"

    def __dict__(self, no_id: bool = False):
        _ = {
            "name": self.name,
            "category": self.category,
            "type": self.type,
            "is_downloaded": self.is_downloaded
        }
        if not no_id: _["id"] = self.id
        return _

class CTFd_Handler:
    """
    Class to interact with the CTFd instance.

    Attributes:
        ctfd: The CTFd object

    Methods:

        # Challenges
        get_challenges: Returns the list of all the challenges currently deployed
        get_challenge: Returns the challenge with the given id
        download_file: Downloads the file from the given url

        # Flags
        submit_flag: Submits the flag for the challenge with the given id

        # Instances
        start_instance: Starts the challenge instance
        extend_instance: Extends the challenge instance
        stop_instance: Stops the challenge instance
    """
    def __init__(self, instance: str, token: str, skip: bool = False):
        self.ctfd = CTFd(instance=instance, token=token, skip=skip)
    
    def get_challenges(self) -> list:
        """
        Returns the list of all the challenges currently deployed.

        Returns:
            List of all the challenges currently deployed
        """
        return RequestHandler.MakeRequest(
            mode=Mode.GET,
            url=f"{self.ctfd.ctfd_instance}/api/v1/challenges",
            token=self.ctfd.ctfd_token
        ).json()["data"]

    def get_challenge(self, chal_id: int) -> dict:
        """
        Fetches the challenge with the given id.

        Returns:
            The challenge information with the given id
        """
        _ = RequestHandler.MakeRequest(
            mode=Mode.GET,
            url=f"{self.ctfd.ctfd_instance}/api/v1/challenges/{chal_id}",
            token=self.ctfd.ctfd_token
        ).json()
        if "message" in _.keys():
            return {}
        return _["data"]
    
    def download_file(self, endpoint: str, filename: str) -> None:
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

        Returns:
            The response from the CTFd instance
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

        Returns:
            The response from the CTFd instance
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

        Returns:
            The response from the CTFd instance
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
    
        Returns:
            The response from the CTFd instance
        """
        return RequestHandler.MakeRequest(
            mode=Mode.POST,
            url=f"{self.ctfd.ctfd_instance}/containers/api/stop",
            token=self.ctfd.ctfd_token,
            json={"chal_id": chal_id}
        ).json()
    
    def get_scoreboard(self, n: int = 10) -> dict:
        """
        Fetches the scoreboard from the CTFd instance.

        Returns:
            The response from the CTFd instance
        """
        return RequestHandler.MakeRequest(
            mode=Mode.GET,
            url=f"{self.ctfd.ctfd_instance}/api/v1/scoreboard/top/{n}",
            token=self.ctfd.ctfd_token,
        ).json()["data"]
    
    def get_solves(self, chal_id: int) -> dict:
        """
        Fetches the solves for the challenge with the given id.

        Returns:
            The response from the CTFd instance
        """
        return RequestHandler.MakeRequest(
            mode=Mode.GET,
            url=f"{self.ctfd.ctfd_instance}/api/v1/challenges/{chal_id}/solves",
            token=self.ctfd.ctfd_token
        ).json()["data"]