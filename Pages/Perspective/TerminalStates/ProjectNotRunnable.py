from selenium.webdriver.remote.webdriver import WebDriver

from Pages.Perspective.TerminalStates.TerminalStatePageObject import TerminalStatePageObject


class ProjectNotRunnable(TerminalStatePageObject):
    """
    The ProjectNotRunnable Terminal State Page is to be expected when a user attempts to visit any path which would
    belong to a project that is configured as not runnable (inheritable, or disabled).
    """

    def __init__(self, driver: WebDriver):
        super().__init__(
            driver=driver,
            expected_page_header_text='Project Not Runnable')
