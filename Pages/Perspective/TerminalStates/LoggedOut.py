from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec

from Pages.Perspective.TerminalStates.TerminalStatePageObject import TerminalStatePageObject


class LoggedOut(TerminalStatePageObject):
    """
    The Logged Out Terminal State Page is expected when a user has logged out of a project and that project requires
    Authentication. Projects which do not require authentication typically log the user out but leave them on
    whichever page they were on before having been logged out.
    """
    _LOGGER_NAME = 'LoggedOutTerminalStatePage'
    _BACK_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'a.terminal-state-link')

    def __init__(self, driver: WebDriver):
        super().__init__(
            driver=driver,
            expected_page_header_text='Logged Out')

    def click_back_button(self) -> None:
        """
        Click the BACK button. This should take the user to the interstitial "Continue to log in" Page.
        """
        self.wait.until(
            ec.presence_of_element_located(
                self._BACK_BUTTON_LOCATOR)).click()
        try:
            self.wait.until(ec.invisibility_of_element_located(self._BACK_BUTTON_LOCATOR))
        except TimeoutException:
            pass

    def click_launch_gateway(self) -> None:
        """
        :raise NotImplementedError: The LoggedOut Terminal State Page does not have a Launch Gateway button.
        """
        raise NotImplementedError("The LoggedOut Page does not have a Launch Gateway button.")

    def get_launch_gateway_button_text(self) -> str:
        """
        :raise NotImplementedError: The LoggedOut Terminal State Page does not have a Launch Gateway button.
        """
        raise NotImplementedError("The LoggedOut Page does not have a Launch Gateway button.")
