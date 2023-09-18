from enum import Enum
from typing import List, Optional, Tuple, Union

from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from Components.BasicComponent import ComponentPiece
from Helpers.IAAssert import IAAssert
from Helpers.IAExpectedConditions import IAExpectedConditions as IAec


class Pager(ComponentPiece):

    class Location(Enum):
        BOTTOM = "bottom"
        TOP = "top"

    """The pager available to most Table components."""
    _ACTIVE_PAGE_CSS_LOCATOR = (By.CSS_SELECTOR, 'div.page.active')
    _ACTUAL_PAGE_JUMP_INPUT = (By.CSS_SELECTOR, 'div.jump input')
    _FIRST_PAGE_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'div.first')
    _LAST_PAGE_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'div.last')
    _NEXT_PAGE_CHEVRON_LOCATOR = (By.CSS_SELECTOR, 'div.next')
    _PAGER_LOCATOR = (By.CSS_SELECTOR, 'div.pager-container')
    _PAGE_JUMP_LOCATOR = (By.CSS_SELECTOR, 'div.jump input')
    _PREVIOUS_PAGE_CHEVRON_LOCATOR = (By.CSS_SELECTOR, 'div.prev')
    _SELECT_SIZE_OPTIONS_LOCATOR = (By.CSS_SELECTOR, 'div.size-options select')
    _DISPLAYED_PAGE_NUMBERS_CSS_LOCATOR = (By.CSS_SELECTOR, 'div.center div.page')
    _ACTIVE_PAGE_NUMBER_LOCATOR = (By.CSS_SELECTOR, "div.ia_pager__page--active")

    def __init__(
            self,
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=self._PAGER_LOCATOR,
            driver=driver,
            parent_locator_list=parent_locator_list,
            description=description,
            poll_freq=poll_freq)
        self._active_page = ComponentPiece(
            locator=self._ACTIVE_PAGE_CSS_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._page_jump_input = ComponentPiece(
            locator=self._PAGE_JUMP_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._first_page_button = ComponentPiece(
            locator=self._FIRST_PAGE_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._last_page_button = ComponentPiece(
            locator=self._LAST_PAGE_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._previous_page_chevron = ComponentPiece(
            locator=self._PREVIOUS_PAGE_CHEVRON_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._next_page_chevron = ComponentPiece(
            locator=self._NEXT_PAGE_CHEVRON_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._row_count_select = ComponentPiece(
            locator=self._SELECT_SIZE_OPTIONS_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._page_numbers = ComponentPiece(
            locator=self._DISPLAYED_PAGE_NUMBERS_CSS_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._active_page_number = ComponentPiece(
            locator=self._ACTIVE_PAGE_NUMBER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)

    def click_first_page_button(self) -> None:
        """
        Click the option in the Page which would take a user to the 'first' page.

        :raises TimeoutException: If the 'First' page option is not present in the Pager.
        :raises AssertionError: If clicking the 'First' page button does result in the Table displaying the first page.
        """
        self._first_page_button.click(binding_wait_time=0.5)
        if len(self.get_all_listed_pages()) > 0:
            IAAssert.is_equal_to(
                actual_value=self.get_active_page(),
                expected_value=1,
                as_type=int,
                failure_msg="We failed to get back to the first page of the Table.")

    def click_last_page_button(self) -> None:
        """
        Click the option in the Page which would take a user to the 'last' page.

        :raises TimeoutException: If the 'Last' page option is not present in the Pager.
        """
        self._last_page_button.click(binding_wait_time=0.5)
        # unable to assert destination page number because of the dynamic length of data.

    def click_next_page_chevron(self, binding_wait_time: float = 0.5) -> None:
        """
        Click the chevron which would take the user to the next page.

        :param binding_wait_time: The amount of time (in seconds) after clicking the next page chevron before allowing
            code to continue.

        :raises TimeoutException: If the 'next' chevron does not exist, or if no page numbers exist in the Pager.
        """
        original_page_number = self.get_active_page()
        self._next_page_chevron.click(binding_wait_time=binding_wait_time)
        IAAssert.is_equal_to(
            actual_value=self.get_active_page(),
            expected_value=original_page_number + 1,
            as_type=int,
            failure_msg="We failed to get to the next page after clicking the next page chevron.")

    def click_page_number(self, desired_page: Union[int, str]) -> None:
        """
        Click a page number within the Pager.

        :param desired_page: The page number you wish to click.

        :raises TimeoutException: If no page numbers are present in the Pager.
        :raises IndexError: If the specified page number is not present in the Pager.
        :raises AssertionError: If the Table does not end up displaying the specified page number.
        """
        list(filter(lambda e: e.text == str(desired_page), self._page_numbers.find_all()))[0].click()
        IAAssert.is_equal_to(
            actual_value=self.get_active_page(),
            expected_value=desired_page,
            as_type=int,
            failure_msg=f"After clicking the option for page {desired_page}, we failed to display that page.")

    def click_previous_page_chevron(self, binding_wait_time: float = 0.5) -> None:
        """
        Click the chevron which would take the user to the previous page.

        :param binding_wait_time: The amount of time (in seconds) after clicking the previous page chevron before
            allowing code to continue.

        :raises TimeoutException: If the 'previous' chevron does not exist.
        """
        original_page_number = self.get_active_page()
        self._previous_page_chevron.click(binding_wait_time=binding_wait_time)
        IAAssert.is_equal_to(
            actual_value=self.get_active_page(),
            expected_value=original_page_number - 1,
            as_type=int,
            failure_msg="We failed to get to the previous page after clicking the previous page chevron.")

    def first_page_button_is_displayed(self) -> bool:
        """
        Determine if the 'First' page option is displayed in the Pager.

        :returns: True, if a user can see the 'First' page option in the Pager.
        """
        try:
            return self._first_page_button.find().is_displayed()
        except TimeoutException:
            return False

    def first_page_button_is_enabled(self) -> bool:
        """
        Determine if the 'First' page option is enabled in the Pager.

        :returns: True, if the 'First' page option in the Pager is enabled.

        :raises TimeoutException: If the 'First' page option is not present in the Pager.
        """
        return 'disabled' not in self._first_page_button.find().get_attribute("class")

    def get_active_page(self) -> int:
        """
        Obtain the number of the currently displayed page of the Table.

        :returns: The number of the currently displayed page.

        :raises TimeoutException: If no page numbers are present.
        """
        return int(self._active_page.get_text())

    def get_all_listed_pages(self) -> List[int]:
        """
        Obtain all displayed page numbers.

        :returns: All page numbers available for clicking in the Pager, including the current (disabled) page.
        """
        try:
            return [int(_.text) for _ in self._page_numbers.find_all()]
        except TimeoutException:
            return []

    def get_all_row_display_options(self) -> List[str]:
        """
        Obtain all selection options form the dropdown which controls how many rows may be displayed in the Table.

        :returns: A list of strings, where each entry is an option available for selection to drive the count of rows
            displayed by the Table.

        :raises TimeoutException: If the row count dropdown is not present.
        """
        return [_.text for _ in Select(webelement=self._row_count_select.find()).options]

    def get_last_displayed_page_number(self) -> int:
        """
        Obtain the number of the last page available in the Pager. This value may not be the count of Pages of data,
        but is the last number a user sees displayed.

        Example: A Table may have 40 pages, but the pager may only allow for quick navigation to pages 1, 2, 3, 4, or 5
        before then displaying the 'Last' page option, or a 'next set of pages' option.

        :returns: The last visible page number available for clicking in the Pager.

        :raises TimeoutException: If no pages numbers are present.
        """
        return int(self._page_numbers.find_all()[-1].text)

    def get_selected_row_count_option_from_dropdown(self) -> int:
        """
        Obtain the currently selected VALUE from the dropdown which dictates how many rows are displayed.

        :returns: The currently selected count of rows which should be displayed. If "25 rows" is selected, this will
            return 25.

        :raises TimeoutException: If the row count dropdown is not present. This dropdown/select piece is only present
            while the Table is wider than 700px.
        """
        return int(Select(webelement=self._row_count_select.find()).first_selected_option.text.split(" ")[0])

    def jump_input_is_displayed(self) -> bool:
        """
        Determine if the input which allows for a user to type a page number is displayed.

        :returns: True, if the user is able to type a page number into the Pager - False otherwise.
        """
        try:
            return self._page_jump_input.find().is_displayed()
        except TimeoutException:
            return False

    def jump_to_page(self, page_to_jump_to: Union[int, str], binding_wait_time: float = 1) -> None:
        """
        Use the page jump input field to go to a specific page in the Table.

        :param page_to_jump_to: The page of the Table to go to.
        :param binding_wait_time: The amount of time (in seconds) to wait after supplying the page number before
            allowing code to continue.

        :raises TimeoutException: If the page jump input is not present.
        :raises AssertionError: If the Table does not end up on the supplied page.
        """
        self._page_jump_input.find().click()
        self.driver.execute_script('arguments[0].value = ""', self._page_jump_input.find())
        self._page_jump_input.find().send_keys(str(page_to_jump_to) + Keys.ENTER)
        self._page_jump_input.wait_on_binding(binding_wait_time)
        # we can only manage the following assertion if page numbers are listed
        if len(self.get_all_listed_pages()) > 0:
            IAAssert.is_equal_to(
                actual_value=self.get_active_page(),
                expected_value=page_to_jump_to,
                as_type=int,
                failure_msg=f"Failed to jump to the specified page ({page_to_jump_to}).")

    def last_page_button_is_displayed(self) -> bool:
        """
        Determine if the 'Last' page option is displayed in the Pager.

        :returns: True, if a user can see the 'Last' page option in the Pager.
        """
        try:
            return self._last_page_button.find().is_displayed()
        except TimeoutException:
            return False

    def last_page_button_is_enabled(self) -> bool:
        """
        Determine if the 'Last' page option is enabled in the Pager.

        :returns: True, if the 'Last' page option in the Pager is enabled.

        :raises TimeoutException: If the 'Last' page option is not present in the Pager.
        """
        try:
            return WebDriverWait(self.driver, 2).until(IAec.function_returns_true(
                custom_function=self._last_page_button_is_enabled,
                function_args={}))
        except TimeoutException:
            return False

    def next_page_chevron_is_enabled(self) -> bool:
        """
        Determine if the next page chevron is enabled.

        :returns: True, if the next page chevron is enabled - False otherwise.
        """
        # .is_enabled() does not work here because it's just a <div>
        return "disabled" not in self._next_page_chevron.find().get_attribute("class")

    def is_displayed(self, location: Location = Location.BOTTOM) -> bool:
        """
        Determine if the specified Pager is displayed within the Table.

        :returns: True, if the Pager is visible to the user - False otherwise.
        """
        try:
            # use the parent locator list instead of our own locator list so that we don't duplicate the pager locator
            # used in our own init step.
            return ComponentPiece(
                locator=(By.CSS_SELECTOR, f'{self._PAGER_LOCATOR[1]}.{location.value}'),
                driver=self.driver,
                parent_locator_list=self._parent_locator_list,
                wait_timeout=0,
                poll_freq=self.poll_freq).find().is_displayed()
        except TimeoutException:
            return False

    def is_hidden(self) -> bool:
        """
        Determine if the Pager is currently hidden.

        :returns: True, if the Pager exists but is currently out of sight of the user - False otherwise.

        :raises TimeoutException: If the Pager is not present at all.
        """
        return self.is_present() and 'hide' in self.find().get_attribute('class')

    def is_present(self) -> bool:
        """
        Determine if the specified Pager exists within the Table. Note that this does not reflect the VISIBILITY of the
        Pager.

        :returns: True, if the Pager exists - False otherwise.
        """
        try:
            return self.find(wait_timeout=0.5) is not None
        except TimeoutException:
            return False

    def page_number_is_displayed(self, desired_page: Union[int, str]) -> bool:
        """
        Determine if a specific page number is currently displayed.

        :param desired_page: The number of the page for which we will verify display status.

        :returns: True, if the supplied page number is currently displayed - False otherwise.

        :raises TimeoutException: If no page numbers are displayed in the Pager.
        """
        return str(desired_page) in [_.text for _ in self._page_numbers.find_all()]

    def previous_page_chevron_is_enabled(self) -> bool:
        """
        Determine if the previous page chevron is enabled.

        :returns: True, if the previous page chevron is enabled - False otherwise.

        :raises TimeoutException: If the previous page chevron is not present.
        """
        return "disabled" not in self._previous_page_chevron.find().get_attribute("class")

    def row_select_dropdown_is_displayed(self) -> bool:
        """
        Determine if the dropdown which allows for specifying a row count to display is displayed.

        :returns: True, if the row count dropdown is displayed - False otherwise.
        """
        try:
            return self._row_count_select.find().is_displayed()
        except (TimeoutException, StaleElementReferenceException):
            return False

    def set_displayed_row_count(self, count_of_rows: Union[int, str], attempted=False) -> None:
        """
        Set the number of displayed rows in the Table. The count of rows must be a valid value from the
        dropdown (Select) in the Pager.

        :param count_of_rows: The desired count of rows (this must be one of the available values in the dropdown).
        :param attempted: Has the function been tried already, if False and counts do not match try to set the dropdown
            value once more.

        :raises TimeoutException: If the row count dropdown is not present.
        :raises AssertionError: If unable to set the row count dropdown to the supplied row count.
        """
        Select(webelement=self._row_count_select.find()).select_by_value(str(count_of_rows))
        self.wait_on_binding(time_to_wait=1)
        if str(count_of_rows) != str(self.get_selected_row_count_option_from_dropdown()):
            if not attempted:
                self.set_displayed_row_count(count_of_rows, attempted=True)
            else:
                # already tried once...
                pass
        IAAssert.is_equal_to(
            actual_value=self.get_selected_row_count_option_from_dropdown(),
            expected_value=count_of_rows,
            as_type=int,
            failure_msg="We failed to specify a count of rows to select.")

    def _last_page_button_is_enabled(self) -> bool:
        """Determine if the 'Last' page button is enabled."""
        return 'disabled' not in self._last_page_button.find().get_attribute('class')
