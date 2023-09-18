from selenium.webdriver.remote.webdriver import WebDriver

from Pages.Perspective.TerminalStates.TerminalStatePageObject import TerminalStatePageObject


class PageClosed(TerminalStatePageObject):
    """
    The PageClosed Terminal State Page is to be expected when a PerspectivePage has been forcibly closed by the
    Gateway.
    """

    def __init__(self, driver: WebDriver):
        super().__init__(
            driver=driver,
            expected_page_header_text='Page Closed')
