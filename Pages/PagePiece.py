import logging
from typing import Tuple, Union

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from Helpers.IASelenium import IASelenium


class PagePiece(object):
    """
    A PagePiece is the smallest, most basic concept of any browser page. While pages in general are free to specify
    any number of unique locators/Component/WebElements, Page Pieces are understood to build out collections of shared
    structure which may be re-used across various scopes. Even Pages may be considered "Page Pieces" as they are a
    collection of shared structures or pieces which are re-used.
    """

    def __init__(
            self,
            driver: WebDriver,
            wait_timeout: float = 10,
            primary_locator: Tuple[Union[By, str], str] = None):
        """
        :param driver: The WebDriver instance which is controlling the browser.
        :param wait_timeout: The amount of time this page should implicitly wait when using functions which would wait.
        :param primary_locator: The locator which defines a known unique element within this content.
        """
        self.driver = driver
        self._wait_timeout = wait_timeout
        self.wait = WebDriverWait(self.driver, self._wait_timeout)
        self.primary_locator = primary_locator
        self.selenium = IASelenium(driver=self.driver)
        self.py_logger = logging.getLogger(self.__class__.__name__)

    def is_present(self) -> bool:
        """
        Determine if this Page Piece is currently located within the Document Object Model (DOM).

        :return: True, if the Page Piece could be located - False otherwise.

        :raises AssertionError: If no primary locator was supplied for the Page Piece. A locator is required for
            checking for the presence of the Page Piece.
        """
        assert self.primary_locator is not None, "Unable to check presence of view without a primary locator."
        return self.driver.find_element(*self.primary_locator) is not None
