from typing import Optional, List, Tuple

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from Components.BasicComponent import BasicPerspectiveComponent
from Components.Common.TextInput import CommonTextInput


class TextField(BasicPerspectiveComponent, CommonTextInput):
    """A Perspective Text Field Component."""

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 10,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        BasicPerspectiveComponent.__init__(
            self,
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        CommonTextInput.__init__(
            self,
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self.no_wait_text_input = CommonTextInput(
            locator=self._locator,
            driver=self.driver,
            parent_locator_list=self._parent_locator_list,
            wait_timeout=0)

    def get_text(self) -> str:
        self.find()
        original_wait = self.wait
        try:
            # Wait no time here so that a TOE is immediate.
            self.wait = WebDriverWait(self.driver, timeout=0)
            text = CommonTextInput.get_text(self)
        except TimeoutException:
            # We've hit a TOE (which MUST be because the overlay has been removed), so try again and allow any
            # potential TOE to be raised.
            text = CommonTextInput.get_text(self)
        finally:
            # Regardless of exception state, we need to reset the original 'wait'.
            self.wait = original_wait
        return text
