from selenium.webdriver.remote.webdriver import WebDriver

from Pages.Perspective.TerminalStates.TerminalStatePageObject import TerminalStatePageObject


class ProjectNotFound(TerminalStatePageObject):
    """
    The ProjectNotFound Terminal State Page is only expected to be present when a project is deleted from the Gateway
    while an active Perspective Session was using a Page from the deleted project. In general, attempts to visit a
    project which does not exist will instead encounter a generic 404 page.
    """

    def __init__(self, driver: WebDriver):
        super().__init__(
            driver=driver,
            expected_page_header_text='Project Not Found')
