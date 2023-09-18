from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece


class ChromePrintPreviewPage:
    """Interface for the print preview page implemented in Chrome."""
    CANCEL_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'div.controls > cr-button.cancel-button')
    PRINT_PREVIEW_APP_LOCATOR = (By.CSS_SELECTOR, 'print-preview-app')
    PRINT_PREVIEW_BUTTON_STRIP_LOCATOR = (By.CSS_SELECTOR, 'print-preview-button-strip')
    SIDE_BAR_LOCATOR = (By.ID, 'sidebar')

    def __init__(self, driver: WebDriver):
        self._driver = driver
        self._print_preview_app = ComponentPiece(
            locator=self.PRINT_PREVIEW_APP_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=1,
            poll_freq=0)

    def click_cancel_button(self, wait_timeout: float = 1) -> None:
        """
        Closes the print preview page.
        When the page is closed, the print preview's window handle will be invalid.
        This resource does not attempt to manage driver windows, so they will need to be handled elsewhere.

        :param wait_timeout: The amount of time (in seconds) to wait for the print preview tag to appear before
            returning.

        """
        self._print_preview_app.find(wait_timeout=wait_timeout).shadow_root.find_element(*self.SIDE_BAR_LOCATOR) \
            .shadow_root.find_element(*self.PRINT_PREVIEW_BUTTON_STRIP_LOCATOR).shadow_root \
            .find_element(*self.CANCEL_BUTTON_LOCATOR).click()

    def print_preview_page_is_open(self, wait_timeout: float = 1) -> bool:
        """
        Checks if the print preview page is open by attempting to find the print-preview-app tag in the DOM.

        :param wait_timeout: The amount of time (in seconds) to wait for the print preview tag to appear
            before returning.

        :returns: True, if the print-preview-app tag can be located within the timeout window - False otherwise.
        """
        try:
            return self._print_preview_app.find(wait_timeout=wait_timeout) is not None
        except TimeoutException:
            return False
