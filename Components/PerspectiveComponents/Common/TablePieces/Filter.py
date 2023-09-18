from typing import List, Tuple, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec

from Components.BasicComponent import ComponentPiece
from Components.Common.TextInput import CommonTextInput
from Helpers.IAAssert import IAAssert
from Helpers.IAExpectedConditions.IAExpectedConditions import TextCondition


class Filter(ComponentPiece):
    """
    The text filter available above the header of Table components.
    """
    _FILTER_LOCATOR = (By.CSS_SELECTOR, '.filterCommon input')
    _RESULTS_LABEL_LOCATOR = (By.CSS_SELECTOR, "div.filterResults")

    def __init__(
            self,
            driver: WebDriver,
            parent_locator_list: List[Tuple[By, str]] = None,
            wait_timeout: float = 1,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=(By.CSS_SELECTOR, 'div[class*="Filter"]'),
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._filter_input = CommonTextInput(
            locator=self._FILTER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=wait_timeout,
            poll_freq=poll_freq)
        self._results_label = ComponentPiece(
            locator=self._RESULTS_LABEL_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=wait_timeout,
            poll_freq=poll_freq)

    def get_results_text(self) -> str:
        """
        Obtain the text of the label which provides feedback on the results of the filter.

        :raises TimeoutException: If the feedback filter is not present.
        """
        return self._results_label.get_text()

    def is_present(self) -> bool:
        """
        Determine if the filter for the table exists.

        :returns: True, if the filter for the table exists - False otherwise. This function makes no claims about
            visibility.
        """
        try:
            return self._filter_input.find() is not None
        except TimeoutException:
            return False

    def results_text_content_is_displayed(self) -> bool:
        """
        Determine if information about filtered results is present.

        :returns: True, if a breakdown regarding filtered results is displayed.
        """
        try:
            return len(self.get_results_text()) > 0
        except TimeoutException:
            return False

    def set_filter_text(self, text: str, binding_wait_time: float = 0) -> None:
        """
        Set the text filter to contain some text.

        :param text: The text you want to supply to the filter of the Table.
        :param binding_wait_time: how long (in seconds) after applying the text to the filter you would like to wait
            before allowing code to continue.

        :raises TimeoutException: If the filter input is not present.
        :raises AssertionError: If the supplied text is not successfully applied to the filter.
        """
        if self._filter_input.get_text() != text:
            self.wait.until(ec.element_to_be_clickable(self._filter_input.get_full_css_locator()))
            text_accounting_for_empty_str = Keys.SPACE + Keys.BACK_SPACE + Keys.ENTER if text == '' else text
            self._filter_input.set_text(
                text=text_accounting_for_empty_str,
                binding_wait_time=binding_wait_time)
        IAAssert.is_equal_to(
            actual_value=self._filter_input.wait_on_text_condition(
                text_to_compare=text, condition=TextCondition.EQUALS),
            expected_value=text,
            as_type=str,
            failure_msg="We failed to apply the supplied text to the filter of the Table.")
