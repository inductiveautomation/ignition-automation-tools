from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Pages.Perspective.TerminalStates.TerminalStatePageObject import TerminalStatePageObject


class MobileLicense(TerminalStatePageObject):
    """
    The MobileLicense Page is to be expected when the applied license of the Gateway only allows for Perspective to be
    accessed via mobile device.
    """
    _SIGN_OUT_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'a.terminal-state-link-inverted')
    _MESSAGE_LOCATOR = (By.CSS_SELECTOR, 'section.new-trial p')

    def __init__(self, driver: WebDriver):
        super().__init__(
            driver=driver,
            expected_page_header_text='Mobile License Only')
