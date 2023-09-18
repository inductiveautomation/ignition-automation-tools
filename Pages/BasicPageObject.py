import logging
from time import sleep
from typing import Tuple, Union

from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from Helpers.IAExpectedConditions import IAExpectedConditions as IAec
from Pages.PagePiece import PagePiece


class BasicPageObject(PagePiece):
    """
    This Page Object may be used to interact with any page outside of Ignition.
    """

    def __init__(
            self,
            driver: WebDriver,
            url: str,
            wait_timeout: float = 10,
            primary_locator: Tuple[Union[By, str], str] = None):
        """
        :param driver: The WebDriver in use for the browser window.
        :param url: The URL of this page.
        :param wait_timeout: The amount of time (in seconds) to implicitly wait.
        :param primary_locator: A Tuple which describes how to locate a unique element on the page, if there is one.
        """
        PagePiece.__init__(
            self,
            driver=driver,
            wait_timeout=wait_timeout,
            primary_locator=primary_locator)
        self.url = url
        self._navigation_string = f'Navigated to {self.url}'

    def navigate_to(self, force: bool = False) -> None:
        """
        Navigate to this page in the browser.

        :param force: Dictates whether the navigation should happen even if you are already on the page. Potentially
            forces a pseudo-refresh.
        """
        self._wait_on_driver()
        if force or not self.is_current_page():
            try:
                for i in range(3):
                    self.driver.get(self.url)
                    if self.is_current_page():
                        break
            except WebDriverException as wde:
                logging.error(f'Encountered a WebDriverException while attempting to navigate to {self.url} .\n'
                              f'The error was ignored and we are going to continue.\n'
                              f'{wde.msg}')
            self._log_navigation()
            self._wait_for_page()

    def get_page_url(self) -> str:
        """
        Obtain the configured URL of this page. To obtain the URL currently in use by the browser, use self.driver.url.

        :return: The URL configured for this Page resource.
        """
        return self.url

    def is_current_page(self) -> bool:
        """
        Determine if this Page is the page currently displayed in your browser tab.

        :return: True if the PageObject's URL matches the current URL, without any parameters. If the
            Page being checked has also specified a primary locator, this value also implies that the locator
            is present.
        """
        try:
            return WebDriverWait(driver=self.driver, timeout=3).until(IAec.function_returns_true(
                custom_function=self._is_current_page,
                function_args={}))
        except TimeoutException:
            return False

    def _is_current_page(self) -> bool:
        """
        Determine if the URL configured for this page resource matches the URL in use in the browser, sans any URL
            parameters.

        :return: True, if the PageObject's URL matches the current URL, without any parameters - False otherwise. If the
            Page being checked has also specified a primary locator, this value also implies that the locator
            is present.
        """
        # Home pages may or may not have a trailing slash, so naively strip any trailing slash
        page_url = self.url.rstrip('/')
        displayed_url = self.driver.current_url.split('?')[0].rstrip('/')
        # if no primary locator is supplied, naively assume that portion as succeeding
        primary_locator_check = self.primary_locator is None
        try:
            # if a primary locator WAS supplied, we must check it is present
            if self.primary_locator is not None:
                primary_locator_check = self.driver.find_element(*self.primary_locator) is not None
        except NoSuchElementException:
            primary_locator_check = False
        except WebDriverException:
            primary_locator_check = False
        return (page_url == displayed_url) and primary_locator_check

    def _log_navigation(self) -> None:
        self.py_logger.info(msg=self._navigation_string)

    def _wait_for_page(self) -> None:
        """
        It's the responsibility of the inheriting class to Override this method if a better approach is available.
        """
        if self.primary_locator is not None:
            try:
                self.wait.until(ec.presence_of_element_located(self.primary_locator))
            except TimeoutException:
                pass
            except WebDriverException:
                pass
        else:
            msg = f'This class ({self.__class__.__name__}) is using the default \'_wait_for_page\' ' \
                  f'method in {BasicPageObject.__name__}.\n' \
                  f'Check to see if there is a better way to wait for the page to load.'
            logging.warning(msg)
            sleep(3)  # hard-coded wait to be used when no primary locator is supplied.

    def _wait_on_driver(self, time_to_wait=3) -> None:
        """
        Wait for the webdriver to know about itself.

        :raise TimeoutException: If the driver takes too long to become usable.
        """
        try:
            WebDriverWait(self.driver, time_to_wait).until(IAec.driver_is_ready(driver=self.driver))
        except TimeoutException as toe:
            raise TimeoutException(msg="The driver did not respond in a timely manner.") from toe
