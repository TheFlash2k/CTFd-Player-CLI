from .logger import logger
from .handler import RequestHandler, Mode
from .utils import get_env, fix_url

class CTFd:
    def __init__(self, instance: str, token: str, check_token = True, check_conn = True):
        
        self.ctfd_instance = get_env(key="CTFD_URL", curr=instance, err_msg="Environment variable \"CTFD_URL\" is not set")

        if check_token:
            self.ctfd_token    = get_env(key="CTFD_TOKEN", curr=token, err_msg="Environment variable \"CTFD_TOKEN\" is not set")

        else:
            return

        if len(self.ctfd_instance) == 0:
            if len(self.ctfd_token) == 0 and check_token:
                logger.error("CTFd token is not set.")
            else:
                logger.error("CTFd instance is not set.")
            exit(1)

        self.ctfd_instance = fix_url(url=self.ctfd_instance)

        logger.info(f"CTFd url: {self.ctfd_instance}")

        if check_conn:
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
    
class CTFd_Handler:
    """ This class' methods will be used for interaction with the CTFd instance. """
    def __init__(self, instance: str, token: str):
        self.ctfd = CTFd(instance=instance, token=token)
    
    def get_challenges(self) -> list:
        """ Returns the list of all the challenges currently deployed
        """
        return RequestHandler.MakeRequest(
            mode=Mode.GET,
            url=f"{self.ctfd.ctfd_instance}/api/v1/challenges",
            token=self.ctfd.ctfd_token
        ).json()["data"]