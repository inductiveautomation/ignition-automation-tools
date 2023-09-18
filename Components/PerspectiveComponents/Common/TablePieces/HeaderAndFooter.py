from typing import List, Optional, Tuple
from typing import Union

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece
from Components.Common.Button import CommonButton
from Components.Common.TextInput import CommonTextInput
from Components.PerspectiveComponents.Common.ComponentModal import ComponentModal
from Components.PerspectiveComponents.Common.DateRangeSelector \
    import CommonDateRangeSelector, HistoricalRange, PerspectiveDate
from Components.PerspectiveComponents.Common.Dropdown import CommonDropdown
from Helpers.CSSEnumerations import CSS
from Helpers.IAAssert import IAAssert
from Helpers.IAExpectedConditions.IAExpectedConditions import TextCondition
from Helpers.Point import Point

_COMMON_CELL_LOCATOR = (By.CSS_SELECTOR, "div.tc")


class FilterModal(ComponentModal):
    """
    The modal available while filtering Table columns. Currently only available to the Table Component.

    This class will not be able to raise any assertion errors when attempting to apply filters because we can't
    possibly know about the expected results of whatever is applied. The Table class utilizing this FilterModal might
    be able to make some assertions regarding application and removal.
    """
    _INPUT_FIELD_CLASS = "ia_inputField"
    _CONDITION_DROPDOWN_LOCATOR = (By.CSS_SELECTOR, f"div.{CommonDropdown.COMMON_CLASS}")
    _BASIC_VALUE_INPUT_LOCATOR = (By.CSS_SELECTOR, f"input.{_INPUT_FIELD_CLASS}")
    _REMOVE_FILTER_SPAN_LOCATOR = (By.CSS_SELECTOR, "span.dataTypeFilter__actionsContainer__removeAction")
    _APPLY_BUTTON_LOCATOR = (By.CSS_SELECTOR, "button.dataTypeFilter__actionsContainer__applyAction")
    _MAXIMUM_RANGE_INPUT_LOCATOR = (By.CSS_SELECTOR, f'{_BASIC_VALUE_INPUT_LOCATOR[1]}[name="max"]')
    _MINIMUM_RANGE_INPUT_LOCATOR = (By.CSS_SELECTOR, f'{_BASIC_VALUE_INPUT_LOCATOR[1]}[name="min"]')
    _DATE_RANGE_PICKER_LOCATOR = (By.CSS_SELECTOR, "div.iaDateRangeTimePicker")

    def __init__(self, driver: WebDriver, description: Optional[str] = None):
        super().__init__(driver=driver, wait_timeout=1, description=description)
        self._condition_dd = CommonDropdown(
            locator=self._CONDITION_DROPDOWN_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1)
        self._basic_value_input = CommonTextInput(
            locator=self._BASIC_VALUE_INPUT_LOCATOR, driver=driver, parent_locator_list=self.locator_list)
        self._remove_filter_link = ComponentPiece(
            locator=self._REMOVE_FILTER_SPAN_LOCATOR, driver=driver, parent_locator_list=self.locator_list)
        self._apply_button = CommonButton(
            locator=self._APPLY_BUTTON_LOCATOR, driver=driver, parent_locator_list=self.locator_list)
        self._min_value_input = CommonTextInput(
            locator=self._MINIMUM_RANGE_INPUT_LOCATOR, driver=driver, parent_locator_list=self.locator_list)
        self._max_value_input = CommonTextInput(
            locator=self._MAXIMUM_RANGE_INPUT_LOCATOR, driver=driver, parent_locator_list=self.locator_list)
        self._date_range_picker = CommonDateRangeSelector(driver=driver)

    def apply_button_is_enabled(self) -> bool:
        """
        Determine if the Apply button is enabled in the modal.

        :returns: True, if the Apply button is enabled - False otherwise.

        :raises TimeoutException: if the Apply button is not present.
        """
        return self._apply_button.find().is_enabled()

    def click_apply_button(self) -> None:
        """
        Click the Apply button in the filter modal.

        :raises TimeoutException: If the Apply button is not present.
        """
        self._apply_button.click()

    def click_remove_filter(self) -> None:
        """
        Click The 'Remove Filter' link in the filter modal.

        :raises TimeoutException: If the 'Remove Filter' link is not present.
        """
        self._remove_filter_link.scroll_to_element(align_to_top=True)
        self._remove_filter_link.click()
        
    def end_time_hours_input_is_enabled(self) -> bool:
        """
        Determine if the input for hours for the ending date is currently enabled.
        
        :returns: True, if the input which drives the hours of the ending date is currently enabled - False otherwise.
        
        :raises TimeoutException: If the hours input for the ending date is not present.
        """
        return self._date_range_picker.end_time_hour_input_is_enabled()
    
    def end_time_minutes_input_is_enabled(self) -> bool:
        """
        Determine if the input for minutes for the ending date is currently enabled.
        
        :returns: True, if the input which drives the minutes of the ending date is currently enabled - False otherwise.
        
        :raises TimeoutException: If the minutes input for the ending date is not present.
        """
        return self._date_range_picker.end_time_minute_input_is_enabled()
    
    def end_time_seconds_input_is_enabled(self) -> bool:
        """
        Determine if the input for seconds for the ending date is currently enabled.
        
        :returns: True, if the input which drives the seconds of the ending date is currently enabled - False otherwise.
        
        :raises TimeoutException: If the seconds input for the ending date is not present.
        """
        return self._date_range_picker.end_time_second_input_is_enabled()

    def get_available_conditions(self) -> List[str]:
        """
        Obtain all options available to the user in the condition dropdown.

        :returns: A list which contains the text of every option in the dropdown of available conditions.

        :raises TimeoutException: If the dropdown which contains available conditions is not present.
        """
        return self._condition_dd.get_available_options()

    def get_enabled_days_from_picker(self) -> List[int]:
        """
        Obtain all days available for selection in the current month.

        :returns: A list with the numbers of all available days within the current month.

        :raises TimeoutException: If the date picker (calendar) is not present.
        """
        return self._date_range_picker.get_enabled_days()

    def get_remove_filter_link_text(self) -> str:
        """
        Obtain the text of the link which would remove the filter for the column. Useful for checking translations.

        :returns: The text of the 'Remove Filter' link, after any potential translation.

        :raises TimeoutException: If the link which removes the current filter is not present.
        """
        return self._remove_filter_link.get_text()

    def get_apply_button_text(self) -> str:
        """
        Obtain the text of the Apply button. Useful for checking translations.

        :returns: The text of the Apply button, after any potential translation.

        :raises TimeoutException: If the Apply button is not present.
        """
        return self._apply_button.get_text()

    def get_current_selected_condition(self) -> Optional[str]:
        """
        Obtain the current filter condition selection.

        :returns: The text of the currently selected filter condition, or None if no selection has been selected yet.
        """
        try:
            return self._condition_dd.get_selected_options_as_list()[0]
        except IndexError:
            return None
    
    def hour_input_is_displayed(self) -> bool:
        """
        Determine if the hours input is displayed. This should not be used when dealing with a time condition of 
        "between", because multiple hour inputs might be present.
        
        :returns: True, if any hour input is displayed.
        """
        try:
            return self._date_range_picker.hour_input_is_displayed()
        except TimeoutException:
            return False
    
    def hour_input_is_enabled(self) -> bool:
        """
        Determine if the hours input is enabled. This should not be used when dealing with a time condition of 
        "between", because multiple hour inputs might be present.
        
        :returns: True, if the hour input field is enabled.
        """
        try:
            return self._date_range_picker.hour_input_is_enabled()
        except TimeoutException:
            return False

    def is_displayed(self) -> bool:
        """
        Determine if the filter modal is currently displayed.

        :returns: True, if the filter modal is currently displayed - False otherwise.
        """
        try:
            return self._condition_dd.find().is_displayed()
        except TimeoutException:
            return False
    
    def minute_input_is_displayed(self) -> bool:
        """
        Determine if the minutes input is displayed. This should not be used when dealing with a time condition of 
        "between", because multiple minute inputs might be present.
        
        :returns: True, if any minute input is displayed.
        """
        try:
            return self._date_range_picker.minute_input_is_displayed()
        except TimeoutException:
            return False
    
    def minute_input_is_enabled(self) -> bool:
        """
        Determine if the minutes input is enabled. This should not be used when dealing with a time condition of 
        "between", because multiple minute inputs might be present.
        
        :returns: True, if the minute input field is enabled.
        """
        try:
            return self._date_range_picker.minute_input_is_enabled()
        except TimeoutException:
            return False

    def seconds_input_is_displayed(self) -> bool:
        """
        Determine if the seconds input is displayed. Distinct from :func:`end_time_seconds_input_is_displayed`, which is
        used for date ranges.

        :returns: True, if the seconds input is displayed - False otherwise.

        :raises TimeoutException: If the seconds input is not present.
        """
        return self._date_range_picker.seconds_input_is_displayed()

    def seconds_input_is_enabled(self) -> bool:
        """
        Determine if the seconds input is enabled. Distinct from :func:`end_time_seconds_input_is_enabled`, which is
        used for date ranges.

        :returns: True, if the seconds input is enabled - False otherwise.

        :raises TimeoutException: If the seconds input is not present.
        """
        return self._date_range_picker.seconds_input_is_enabled()

    def select_date_and_apply(self, date: PerspectiveDate, apply: bool = True) -> None:
        """
        Select a date, and potentially apply that date.

        :param date: The date to select in the filter modal.
        :param apply: If True, click the apply button. If False, take no action after selecting the date.

        :raises TimeoutException: If the date picker (calendar) is not present, or if the Apply button is not present.
        """
        self._date_range_picker.select_date(date=date)
        if apply:
            self._apply_button.click()

    def select_range(self, historical_range: HistoricalRange) -> None:
        """
        Apply a historical range (start AND end date) to the filter modal and then click the Apply button.

        :param historical_range: An object containing the start and end dates to be applied to the filter modal.

        :raises TimeoutException: If the date picker (calendar) is not present, or if the Apply button is not present.
        """
        self._date_range_picker.set_historical_range(historical_range=historical_range, apply=True)

    def set_condition(self, condition: str) -> None:
        """
        Select a condition from the dropdown.

        :param condition: The text of the condition to select.

        :raises TimeoutException: If the condition dropdown is not present.
        :raises AssertionError: If we fail to select the supplied condition.
        """
        self._condition_dd.select_option_by_text_if_not_selected(option_text=condition)
        IAAssert.is_equal_to(
            actual_value=self._condition_dd.get_selected_options_as_list()[0],
            expected_value=condition,
            failure_msg=f"We failed to select the '{condition}' option in the condition dropdown of the filter modal.")

    def set_maximum_range_value(self, text: Union[int, str]) -> None:
        """
        Set the maximum value in use by the filter.

        :param text: The maximum value the filter should use.

        :raises TimeoutException: if the maximum value input field is not present.
        :raises AssertionError: If we fail to set the input to the supplied value.
        """
        self._max_value_input.set_text(text=text)
        IAAssert.is_equal_to(
            actual_value=self._max_value_input.wait_on_text_condition(
                text_to_compare=text, condition=TextCondition.EQUALS),
            expected_value=text,
            as_type=str,
            failure_msg="We failed to set the maximum value within the filter modal.")

    def set_minimum_range_value(self, text: Union[int, str]) -> None:
        """
        Set the minimum value in use by the filter.

        :param text: The minimum value the filter should use.

        :raises TimeoutException: if the minimum value input field is not present.
        :raises AssertionError: If we fail to set the input to the supplied value.
        """
        self._min_value_input.set_text(text=text)
        IAAssert.is_equal_to(
            actual_value=self._min_value_input.wait_on_text_condition(
                text_to_compare=text, condition=TextCondition.EQUALS),
            expected_value=text,
            as_type=str,
            failure_msg="We failed to set the minimum value within the filter modal.")

    def set_value_for_condition(self, text: Union[int, str]) -> None:
        """
        Set the value for the condition. This function should be sued for condition which do not include ranges of any
        type.

        :param text: The value of the condition.

        :raises TimeoutException: if the value input field is not present.
        :raises AssertionError: If we fail to set the input to the supplied value.
        """
        self._basic_value_input.set_text(text=text, binding_wait_time=1)
        IAAssert.is_equal_to(
            actual_value=self._basic_value_input.wait_on_text_condition(
                text_to_compare=text, condition=TextCondition.EQUALS),
            expected_value=text,
            as_type=str,
            failure_msg="We failed to set the condition value within the filter modal.")
        
    def start_time_hours_input_is_enabled(self) -> bool:
        """
        Determine if the hours input of the start time is enabled.
        
        :returns: True, if the hours input of the start time is enabled - False otherwise.
        
        :raises TimeoutException: If the hours input is not present.
        """
        return self._date_range_picker.start_time_hour_input_is_enabled()
        
    def start_time_minutes_input_is_enabled(self) -> bool:
        """
        Determine if the minutes input of the start time is enabled.
        
        :returns: True, if the minutes input of the start time is enabled - False otherwise.
        
        :raises TimeoutException: If the minutes input is not present.
        """
        return self._date_range_picker.start_time_minute_input_is_enabled()
        
    def start_time_seconds_input_is_enabled(self) -> bool:
        """
        Determine if the seconds input of the start time is enabled.
        
        :returns: True, if the seconds input of the start time is enabled - False otherwise.
        
        :raises TimeoutException: If the seconds input is not present.
        """
        return self._date_range_picker.start_time_second_input_is_enabled()

    def value_input_is_enabled(self) -> bool:
        """
        Determine if the basic value input field in the filter modal is enabled.

        :returns: True, if the value input is enabled - False otherwise.

        :raises TimeoutException: If the value input field is not present.
        """
        return self._basic_value_input.find().is_enabled()


class Footer(ComponentPiece):
    """
    The Footer of a table, as distinct from the Header. Headers are far more likely to be used so default to checking
    those.
    """
    _FOOTER_CONTAINER_LOCATOR = (By.CSS_SELECTOR, "div.tf-container")
    _FOOTER_ROW_LOCATOR = (By.CSS_SELECTOR, "div.tr.footer")

    def __init__(
            self,
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 1,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=self._FOOTER_CONTAINER_LOCATOR,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._footer_rows = ComponentPiece(
            locator=self._FOOTER_ROW_LOCATOR, driver=driver, parent_locator_list=self.locator_list, poll_freq=poll_freq)
        self._footer_cells = ComponentPiece(
            locator=_COMMON_CELL_LOCATOR,
            driver=driver,
            parent_locator_list=self._footer_rows.locator_list,
            poll_freq=poll_freq)

    def get_column_names(self) -> List[str]:
        """
        Obtain all column names displayed in the Footer.

        :returns: A list which contains all column names displayed in the Footer.

        :raises TimeoutException: If no Footer is present.
        """
        return [_.text for _ in self._footer_cells.find_all()]

    def footer_is_present(self) -> bool:
        """
        Determine if the Table is currently displaying a Footer.

        :returns: True, if the Table is currently displaying a Footer - False otherwise.
        """
        try:
            return self.find().is_displayed()
        except TimeoutException:
            return False


class Header(ComponentPiece):
    _HEADER_CONTAINER_LOCATOR = (By.CSS_SELECTOR, "div.th-container")
    _HEADER_ROW_LOCATOR = (By.CSS_SELECTOR, "div.tr.header")

    def __init__(
            self,
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 1,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=self._HEADER_CONTAINER_LOCATOR,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._header_rows = ComponentPiece(
            locator=self._HEADER_ROW_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._header_cells = ComponentPiece(
            locator=_COMMON_CELL_LOCATOR,
            driver=driver,
            parent_locator_list=self._header_rows.locator_list,
            poll_freq=poll_freq)
        self.__header_cell = {}
        self._filter_cells = {}
        self._header_cell_dict = {}

    def descending_sort_is_active(self, column_id: str) -> Optional[bool]:
        """
        Determine if the current sort order of the column is 'descending'.

        :returns: True, if the sort order is descending. False, if the sort or is ascending. None, if no sort order is
            applied to the column.

        :raises TimeoutException: If no column exists with the specified column id.
        """
        try:
            descending_arrow = self._get_header_cell_by_id(
                column_id=column_id).find().find_element(By.CSS_SELECTOR, 'div.sort-down')
            return 'active' in descending_arrow.get_attribute('class')
        except NoSuchElementException:
            return None

    def get_column_ids(self) -> List[str]:
        """
        Obtain the ids of all columns in the Table. Column ids map directly to the keys of the underlying data of the
        Table.

        :returns: A list which contains the ids of all columns in the Table.
        """
        try:
            # don't return the "select" column, AND remove any potential sorting value for the column
            return [_.get_attribute('data-column-id') for _ in self._header_cells.find_all() if _.text != ""]
        except TimeoutException:
            return []

    def get_column_index(self, column_id: str) -> int:
        """
        Obtain the index of a column based off of the id of the column. Note that the id is derived from the underlying
        data of the table, and is not necessarily the displayed name of the column.

        :returns: The zero-based display index of the column with the supplied id.

        :raises TimeoutException: If the supplied column id does not match any column in the Table.
        """
        return int(self._get_header_cell_by_id(column_id=column_id).find().get_attribute("data-column-index"))

    def get_column_names(self) -> List[str]:
        """
        Obtain the names of all columns in the Table. Column names are for display purposes ONLY, and are not a
        guaranteed way to reference columns. Be wary of functions which require a column id.

        :returns: A list which contains the names of all columns in the Table.
        """
        try:
            # don't return the "select" column, AND remove any potential sorting value for the column
            return [str(_.text).splitlines()[0] for _ in self._header_cells.find_all() if _.text != ""]
        except TimeoutException:
            return []

    def get_column_max_width(self, column_id: str, include_units: bool = False) -> str:
        """
        Obtain the max width available to a column.

        :param column_id: The id of the column for which you would like the max width.
        :param include_units: Dictates whether the returned value contains the units of measurement (almost
            always 'px').

        :raises TimeoutException: If no column exists with the specified id.
        """
        try:
            header = self._get_header_cell_by_id(column_id=column_id)
            width = header.get_css_property(property_name=CSS.MAX_WIDTH)
            return width if include_units else width.split("px")[0]
        except IndexError:
            return "-1"

    def get_column_width(self, column_id: str, include_units: bool = False) -> str:
        """
        Obtain the width of a column.

        :param column_id: The id of the column for which you would like the width.
        :param include_units: Dictates whether the returned value contains the units of measurement (almost
            always 'px').

        :raises TimeoutException: If no column exists with the specified id.
        """
        return self._get_header_cell_by_id(
            column_id=column_id).get_computed_width(include_units=include_units)

    def get_count_of_columns(self) -> int:
        """
        Obtain a count of all displayed columns.

        :raises TimeoutException: If no header is displayed, or if the Table has no data.
        """
        return len(self._header_cells.find_all())

    def get_origin_of_column(self, column_index: int) -> Point:
        """
        Obtain the positioning information of the beginning of a column.

        :param column_index: The numeric index of the column you would like positional data for.

        :returns: A two-dimensional point which represents the top-left corner of the header cell for the specified
            column.

        :raises TimeoutException: If no column exists with the specified index.
        """
        return self._get_header_cell_by_index(column_index=column_index).get_origin()

    def get_sort_order_number_of_column(self, column_id: str) -> Optional[int]:
        """
        Obtain the sort order of a column.

        :param column_id: The id of the column for which you would like the sort order.

        :returns: The sort order of the column as a number, or None if no sorting is applied.

        :raises TimeoutException: If no column exists with the specified id.
        """
        try:
            return int(self._get_header_cell_by_id(
                column_id=column_id).find().find_element(
                By.CSS_SELECTOR,
                'div.sort-order-mini').text)
        except NoSuchElementException:
            return None

    def get_termination_of_column(self, column_index: int) -> Point:
        """
        Obtain the positioning information of the ending of a column.

        :param column_index: The numeric index of the column you would like positional data for.

        :returns: A two-dimensional point which represents the bottom-right corner of the header cell for the specified
            column.

        :raises TimeoutException: If no column exists with the specified index.
        """
        return self._get_header_cell_by_index(column_index=column_index).get_termination()

    def header_is_present(self) -> bool:
        """
        Determine if a header is currently displayed for the Table.

        :returns: True, if a header is currently displayed for the Table - False otherwise.
        """
        try:
            return self.find().is_displayed()
        except TimeoutException:
            return False

    def hover_over_column_in_header(self, column_index: int) -> None:
        """
        Hover over the header cell of a column of the Table.

        :param column_index: The zero-based index of the column of which you would like to hover over the header cell.

        :raises TimeoutException: If no column exists with the specified index.
        """
        self._get_header_cell_by_index(column_index=column_index).hover()

    def _get_header_cell_by_index(self, column_index: int) -> ComponentPiece:
        """
        Obtain the header cell (as a ComponentPiece) of the column with the specified index.
        """
        header_cell = self._header_cell_dict.get(column_index)
        if not header_cell:
            header_cell = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'{_COMMON_CELL_LOCATOR[1]}[data-column-index="{column_index}"]'),
                driver=self.driver,
                parent_locator_list=self._header_rows.locator_list,
                poll_freq=self.poll_freq)
            self._header_cell_dict[column_index] = header_cell
        return header_cell

    def _get_header_cell_by_id(self, column_id: str) -> ComponentPiece:
        """
        Obtain the header cell (as a ComponentPiece) of the column with the specified column id.
        """
        header_cell = self._header_cell_dict.get(column_id)
        if not header_cell:
            header_cell = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'{_COMMON_CELL_LOCATOR[1]}[data-column-id="{column_id}"]'),
                driver=self.driver,
                parent_locator_list=self._header_rows.locator_list,
                poll_freq=self.poll_freq)
            self._header_cell_dict[column_id] = header_cell
        return header_cell
