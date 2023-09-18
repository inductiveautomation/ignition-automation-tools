from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec

from Pages.Perspective.TerminalStates.TerminalStatePageObject import TerminalStatePageObject


class Forbidden(TerminalStatePageObject):
    """
    The Forbidden Terminal State Page is to be expected when a user does not have the Security Level required by a
    project.
    """
    _SIGN_OUT_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'a.terminal-state-link-inverted')

    def __init__(self, driver: WebDriver):
        super().__init__(
            driver=driver,
            expected_page_header_text='Forbidden')

    def click_sign_out(self) -> None:
        """
        Click the Sign Out button.
        """
        self.wait.until(
            ec.presence_of_element_located(
                self._SIGN_OUT_BUTTON_LOCATOR)).click()
