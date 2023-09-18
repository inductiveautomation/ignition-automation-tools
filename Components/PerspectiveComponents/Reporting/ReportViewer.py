from typing import Union, Optional, List, Tuple

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Helpers.IAExpectedConditions import IAExpectedConditions as IAec


class ReportViewer(BasicPerspectiveComponent):
    """A Perspective Report Viewer Component."""
    _REPORT_CONTENTS_LOCATOR = (By.CSS_SELECTOR, 'div.react-pdf__Page__textContent')
    _ZOOM_LEVEL_LOCATOR = (By.CSS_SELECTOR, 'div.iaSelectCommon select')
    _FIRST_PAGE_LOCATOR = (By.CSS_SELECTOR, 'div.first-action')
    _PREVIOUS_PAGE_LOCATOR = (By.CSS_SELECTOR, 'div.previous-action')
    _NEXT_PAGE_LOCATOR = (By.CSS_SELECTOR, 'div.next-action')
    _LAST_PAGE_LOCATOR = (By.CSS_SELECTOR, 'div.last-action')
    _CURRENT_PAGE_LOCATOR = (By.CSS_SELECTOR, 'div.page-display input')
    _TOTAL_PAGE_LOCATOR = (By.CSS_SELECTOR, 'div.page-display span.page-count')
    _DOWNLOAD_LOCATOR = (By.CSS_SELECTOR, 'a.download-action')
    _TAB_OPEN_LOCATOR = (By.CSS_SELECTOR, 'a.open-in-tab-action')
    _COMPONENT_MESSAGE_LOCATOR = (By.CSS_SELECTOR, 'div.message-primary')
    _SPINNER_LOCATOR = (By.CSS_SELECTOR, 'svg.loading-spinner')

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 2,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._contents = ComponentPiece(
            locator=self._REPORT_CONTENTS_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._zoom_level_select = ComponentPiece(
            locator=self._ZOOM_LEVEL_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._first_page_action = ComponentPiece(
            locator=self._FIRST_PAGE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._previous_page_action = ComponentPiece(
            locator=self._PREVIOUS_PAGE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._next_page_action = ComponentPiece(
            locator=self._NEXT_PAGE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._last_page_action = ComponentPiece(
            locator=self._LAST_PAGE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._current_page_action = ComponentPiece(
            locator=self._CURRENT_PAGE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._total_pages_label = ComponentPiece(
            locator=self._TOTAL_PAGE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._download_link = ComponentPiece(
            locator=self._DOWNLOAD_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._open_in_new_tab_link = ComponentPiece(
            locator=self._TAB_OPEN_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._message = ComponentPiece(
            locator=self._COMPONENT_MESSAGE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._loading_spinner = ComponentPiece(
            locator=self._SPINNER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)

    def click_first_page_button(self) -> None:
        """Click the 1st page button in the Report Viewer."""
        self._click_page_action_when_enabled(action=self._first_page_action)

    def click_previous_page_button(self) -> None:
        """Click the previous page button in the Report Viewer."""
        self._click_page_action_when_enabled(action=self._previous_page_action)

    def click_next_page_button(self) -> None:
        """Click the next page button in the Report Viewer."""
        self._click_page_action_when_enabled(action=self._next_page_action)

    def click_last_page_button(self) -> None:
        """Click the last page button in the Report Viewer."""
        self._click_page_action_when_enabled(action=self._last_page_action)

    def click_download_button(self) -> None:
        """
        Click the download button in the Report Viewer.

        :raises TimeoutException: If the Report Viewer could not be found, or if the ability to download is not
        enabled for the Report Viewer in use.
        """
        self._download_link.click()

    def download_button_is_displayed(self) -> bool:
        """
        Determine the visibility state of the download button of the Report Viewer.

        :returns: True, if the button which allows for downloading the Report is displayed - False otherwise.
        """
        try:
            return self._download_link.find().is_displayed()
        except TimeoutException:
            return False

    def tab_open_button_is_displayed(self) -> bool:
        """
        Determine the visibility state of the open-in-new-tab button of the Report Viewer.

        :returns: True, if the button which allows for opening the Report in a new tab is displayed - False otherwise.
        """
        try:
            return self._open_in_new_tab_link.find().is_displayed()
        except TimeoutException:
            return False

    def click_tab_open_button(self) -> None:
        """Click the open-in-new-tab button."""
        self._open_in_new_tab_link.scroll_to_element()
        self._open_in_new_tab_link.click()

    def input_page_number(self, page_number: Union[int, str]) -> None:
        """
        Type a page number for the Report Viewer to display.

        :param page_number: The page you would like to type into the Report Viewer in order to view the supplied page.
        """
        self._current_page_action.click(binding_wait_time=0.5)
        self._current_page_action.find().clear()
        self._current_page_action.find().send_keys(str(page_number))

    def get_page_number(self) -> int:
        """
        Obtain the page number currently being displayed by the report.

        :returns: The number of the page currently displayed to the user.
        """
        return int(self._current_page_action.find().get_attribute('value'))

    def get_page_count(self) -> int:
        """
        Obtain a count of how many pages the displayed report contains.

        :returns: A count of pages contained within the report.
        """
        return int(float(self._total_pages_label.get_text().split(' ')[-1]))

    def get_displayed_report_contents(self, _attempted_already=False) -> Optional[str]:
        """
        Obtain the text content of the report. This function will retry one time in the event of a failure.

        :param _attempted_already: Used internal to this function in an effort to retry in the event the Report Viewer
            updates during our first attempt. Should always be supplied as False.

        :raises StaleElementReferenceException: If the function has encountered a StaleElementReferenceException
            twice; such an exception can be encountered if the report is updated during querying.
        """
        try:
            WebDriverWait(driver=self.driver, timeout=5).until(
                IAec.function_returns_true(
                    custom_function=self._report_content_is_not_empty,
                    function_args={}))
            spans = WebDriverWait(driver=self.driver, timeout=3).until(
                ec.presence_of_element_located(self._REPORT_CONTENTS_LOCATOR)).find_elements(*(By.CSS_SELECTOR, 'span'))
            return " ".join([span.text for span in spans])
        except TimeoutException:
            return None
        except StaleElementReferenceException as sere:
            if not _attempted_already:
                return self.get_displayed_report_contents(_attempted_already=True)
            else:
                raise sere

    def get_component_message(self) -> str:
        """
        Obtain the text of any Component Error message.

        :raises TimeoutException: If no Component Error message is found.
        """
        self.spinner_appeared()
        self.spinner_was_removed(wait_timeout=5)
        return self._message.find(wait_timeout=3).text

    def spinner_appeared(self, wait_timeout: float = 2) -> bool:
        """
        Wait until the loading spinner has appeared.

        :param wait_timeout: How long to wait for the spinner to appear.

        :returns: True, once the spinner has appeared - False, if the spinner never appeared.
        """
        try:
            return WebDriverWait(driver=self.driver, timeout=wait_timeout).until(
                IAec.function_returns_true(
                    custom_function=self._spinner_appeared,
                    function_args={}))
        except TimeoutException:
            return False

    def spinner_was_removed(self, wait_timeout: float = 2) -> bool:
        """
        Wait until the loading spinner has been removed.

        :param wait_timeout: How long to wait for the spinner to be removed.

        :returns: True, once the spinner has been removed - False, if the spinner remains in place.
        """
        try:
            return WebDriverWait(driver=self.driver, timeout=wait_timeout).until(
                IAec.function_returns_true(
                    custom_function=self._spinner_disappeared,
                    function_args={}))
        except TimeoutException:
            return False

    def _click_page_action_when_enabled(self, action: ComponentPiece) -> None:
        """
        Wait for a Report Viewer page action to become enabled before clicking it.

        :raises TimeoutException: If the page action (button) never becomes enabled.
        """
        WebDriverWait(driver=self.driver, timeout=3).until(IAec.function_returns_true(
            custom_function=action.find().is_enabled,
            function_args={}))
        action.click()

    def _spinner_disappeared(self) -> bool:
        """
        Determine if the spinner has been removed.

        :returns: True, if the spinner is no longer present - False if the spinner remains in place.
        """
        try:
            return self._loading_spinner.find(wait_timeout=0) is None
        except TimeoutException:
            return True

    def _spinner_appeared(self) -> bool:
        """
        Determine if the spinner is displayed.

        :returns: True, if the spinner is displayed - False otherwise.
        """
        try:
            return self._loading_spinner.find(wait_timeout=0).is_displayed()
        except TimeoutException:
            return False

    def _report_content_is_not_empty(self, wait_timeout: float = 3) -> bool:
        """
        Waits until the Report Viewer is displaying any content other than the spinner.

        :param wait_timeout: The amount of time to wait for the Report Viewer to display any report content.

        :returns: True if the Report Viewer is displaying any content before the specified wait period has lapsed -
            False otherwise.
        """
        try:
            report_contents = WebDriverWait(driver=self.driver, timeout=wait_timeout).until(
                ec.presence_of_element_located(
                    self._REPORT_CONTENTS_LOCATOR)).get_attribute('innerHTML')
            return report_contents is not None and len(report_contents) > 0
        except TimeoutException:
            return False
