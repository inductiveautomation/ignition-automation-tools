from typing import Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Pages.BasicPageObject import BasicPageObject


class IgnitionPageObject(BasicPageObject):
    """
    The Ignition Page Object is intended to encompass the final pieces shared among all Pages which would belong to an
    Ignition instance.
    """

    def __init__(
            self,
            driver: WebDriver,
            gateway_address: str,
            destination_path: str,
            wait_timeout: float = 10,
            primary_locator: Tuple[By, str] = None):
        """
        :param driver: The WebDriver being used to control the browser.
        :param gateway_address: The address (including port) of your Gateway. Expects scheme, all domains, and port.
        :param destination_path: The "subdirectory" and "path" pieces of the URL of this page resource, including a
            leading slash - eg: "/path/to/my/page"
        :param wait_timeout: The amount of time (in seconds) this page resource should implicitly wait when needed.
        :param primary_locator: A locator which describes an HTML element unique to this page.
        """
        self._PATH = destination_path
        self.url = gateway_address + destination_path
        BasicPageObject.__init__(
            self, driver=driver, url=self.url, wait_timeout=wait_timeout, primary_locator=primary_locator)
