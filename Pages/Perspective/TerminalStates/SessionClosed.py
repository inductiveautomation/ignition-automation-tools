from selenium.webdriver.remote.webdriver import WebDriver

from Pages.Perspective.TerminalStates.TerminalStatePageObject import TerminalStatePageObject


class SessionClosed(TerminalStatePageObject):
    """
    The SessionClosed Terminal State Page is to be expected when the Gateway has forcibly closed an entire Session.
    """

    def __init__(self, driver: WebDriver):
        super().__init__(
            driver=driver,
            expected_page_header_text='Session Closed')
