from typing import List, Union, Optional, Tuple

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException, \
    ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from Components.BasicComponent import ComponentPiece, BasicPerspectiveComponent
from Components.PerspectiveComponents.Common.Checkbox import CommonCheckbox
from Components.PerspectiveComponents.Common.ComponentModal import ComponentModal
from Components.PerspectiveComponents.Common.DateRangeSelector import \
    CommonDateRangeSelector, DateRangeSelectorTab, DateRangeSelectorTimeUnit, HistoricalRange
from Components.PerspectiveComponents.Common.Table import Table
from Components.PerspectiveComponents.Common.TablePieces.Body import Body
from Components.PerspectiveComponents.Common.TablePieces.Filter import Filter
from Components.PerspectiveComponents.Common.TablePieces.HeaderAndFooter import Header
from Components.PerspectiveComponents.Common.TablePieces.Pager import Pager
from Helpers.IAAssert import IAAssert
from Helpers.IAExpectedConditions import IAExpectedConditions as IAec
from Helpers.IASelenium import IASelenium
from Helpers.Ignition.Alarm import AlarmPriority, AlarmState, AlarmStatusTableAlarmState
from Helpers.Point import Point


class AlarmTableColumn:
    """
    An Alarm Table Column definition, which contains insight into both the name of the column, as well as the id
    used to designate that column in the DOM.
    """
    
    def __init__(self, data_column_id: str, name: str):
        self.data_column_id = data_column_id
        self.name = name


class StandardAlarmTableColumns:
    """
    Standard columns available to both the Alarm Status Table and Alarm Journal Table.
    """
    ACK_NOTES = AlarmTableColumn(data_column_id='ackNotes', name='Ack Notes')
    ACK_USER = AlarmTableColumn(data_column_id='ackUser', name='Ack User')
    ACK_PIPELINE = AlarmTableColumn(data_column_id='ackPipeline', name='Ack Pipeline')
    ACK_TIME = AlarmTableColumn(data_column_id='ackTime', name='Ack Time')
    ACTIVE_DURATION = AlarmTableColumn(data_column_id='activeDuration', name='Active Duration')
    ACTIVE_TIME = AlarmTableColumn(data_column_id='activeTime', name='Active Time')
    CLEAR_PIPELINE = AlarmTableColumn(data_column_id='clearPipeline', name='Clear Pipeline')
    CLEAR_TIME = AlarmTableColumn(data_column_id='clearTime', name='Clear Time')
    DEADBAND = AlarmTableColumn(data_column_id='deadband', name='Deadband')
    DISPLAY_PATH = AlarmTableColumn(data_column_id='displayPath', name='Display Path')
    EVENT_ID = AlarmTableColumn(data_column_id='eventId', name='Event Id')
    EVENT_STATE = AlarmTableColumn(data_column_id='eventState', name='Event State')
    EVENT_TIME = AlarmTableColumn(data_column_id='eventTime', name='Event Time')
    EVENT_VALUE = AlarmTableColumn(data_column_id='eventValue', name='Event Value')
    EXPIRES = AlarmTableColumn(data_column_id='expires', name='Expires')
    IS_ACKED = AlarmTableColumn(data_column_id='isAcked', name='Is Acked')
    IS_ACTIVE = AlarmTableColumn(data_column_id='isActive', name='Is Active')
    IS_CLEAR = AlarmTableColumn(data_column_id='isClear', name='Is Clear')
    IS_SYSTEM_EVENT = AlarmTableColumn(data_column_id='isSystemEvent', name='Is System Event')
    LABEL = AlarmTableColumn(data_column_id='label', name='Label')
    NAME = AlarmTableColumn(data_column_id='name', name='Name')
    PRIORITY = AlarmTableColumn(data_column_id='priority', name='Priority')
    SHELVED_BY = AlarmTableColumn(data_column_id='shelvedBy', name='Shelved By')
    SOURCE = AlarmTableColumn(data_column_id='source', name='Source')
    SOURCE_PATH = AlarmTableColumn(data_column_id='sourcePath', name='Source Path')
    STATE = AlarmTableColumn(data_column_id='state', name='State')
    NOTES = AlarmTableColumn(data_column_id='notes', name='Notes')
    UNACK_DURATION = AlarmTableColumn(data_column_id='unackDuration', name='Unack Duration')

    def get_all_permanent_columns(self) -> List[AlarmTableColumn]:
        """
        Obtain all columns which are always available for configuration within the Alarm Tables.
        """
        return [
            self.ACK_NOTES,
            self.ACK_USER,
            self.ACK_PIPELINE,
            self.ACK_TIME,
            self.ACTIVE_DURATION,
            self.ACTIVE_TIME,
            self.CLEAR_PIPELINE,
            self.CLEAR_TIME,
            self.DEADBAND,
            self.DISPLAY_PATH,
            self.EVENT_ID,
            self.EVENT_STATE,
            self.EVENT_TIME,
            self.EVENT_VALUE,
            self.EXPIRES,
            self.IS_ACKED,
            self.IS_ACTIVE,
            self.IS_CLEAR,
            self.IS_SYSTEM_EVENT,
            self.LABEL,
            self.NAME,
            self.PRIORITY,
            self.SHELVED_BY,
            self.SOURCE,
            self.SOURCE_PATH,
            self.STATE,
            self.NOTES,
            self.UNACK_DURATION
        ]


class AssociatedDataAlarmTableColumn(AlarmTableColumn):
    """A Column which may be configured for appearance, but only exists due to the custom configuration of an alarm."""
    
    def __init__(self, associated_data_column_name: str):
        """
        :param associated_data_column_name: The case-sensitive name of the Associated Data field.
        """
        super().__init__(data_column_id=associated_data_column_name, name=associated_data_column_name)
        

class _AlarmTable(Table, BasicPerspectiveComponent):
    """A common definition of an Alarm Table in Perspective.

    Important terminology:
    Prefilter: Conditional filters - like State and Priority - which may be applied to the table in order to filter
        the displayed results to only those alarm entries which match at least one of the applied conditions.
    """

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: List[Tuple[By, str]],
            wait_timeout: float = 10,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        Table.__init__(
            self,
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        BasicPerspectiveComponent.__init__(
            self,
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            poll_freq=poll_freq
        )
        self._alarm_table_toolbar = _AlarmTableToolbar(
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._alarm_table_body = _AlarmTableBody(
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._alarm_table_filter = _AlarmTableFilter(
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._alarm_table_header = _AlarmTableHeader(
            driver=driver,
            parent_locator_list=parent_locator_list,
            poll_freq=poll_freq)
        self._pager = Pager(
            driver=driver, 
            parent_locator_list=self.locator_list, 
            poll_freq=poll_freq)

    def apply_filter_string(self, filter_string: str, wait_for_filtered_results: float = 2) -> None:
        """
        Expand the text filter located at the top of the Alarm Table, and then type a supplied string into the input.

        :param filter_string: The string to type into the filter input.
        :param wait_for_filtered_results: The amount of time (in seconds) to wait for the filtered result count to
            change before allowing code to continue.

        :raises TimeoutException: If the text filter is not present.
        """
        self._alarm_table_filter.set_filter_text(text=filter_string, binding_wait_time=wait_for_filtered_results)

    def apply_prefilters(
            self,
            prefilter_list: List[Union[AlarmState, AlarmPriority]],
            close_modal_after: bool = True) -> None:
        """
        Expand the popover/modal which contains the Alarm States and Priorities, and then apply the supplied
            States/Priorities to the Alarm table.

        :param prefilter_list: A list of the Alarm States and/or Alarm Priorities you would like to have applied as
            a condition for display of an alarm.
        :param close_modal_after: Dictates whether the popover/modal which contains the states and priorities is
            closed after the selections are made.

        :raises AssertionError: If unsuccessful in applying all supplied States/Priorities.
        :raises TimeoutException: If the icon required to expand the conditional prefilter popover/modal is not present.
        """
        self.open_prefilter_popover()
        self._alarm_table_toolbar.apply_prefilters(
            prefilter_list=prefilter_list)
        if close_modal_after:
            self.close_any_open_popover_or_modal()
        self._alarm_table_toolbar.wait_on_binding(time_to_wait=1)

    def apply_show_all_events_prefilter(self) -> None:
        """
        Expand the Prefilter modal, select the 'Show All' option under 'Events' (NOT PRIORITY), and then close the
        modal.

        :raises TimeoutException: If the Prefilter icon is not present in the toolbar of the Alarm Table.
        """
        if not self._alarm_table_toolbar.prefilter_popover_or_modal_is_displayed():
            self._alarm_table_toolbar.click_prefilter_icon()
        self._alarm_table_toolbar.apply_show_all_events_prefilter()
        self._alarm_table_toolbar.click_popover_or_modal_close_icon()

    def cards_are_displayed(self) -> bool:
        """
        Determine if the Alarm Table is displaying cards as part of a responsive layout.

        :returns: True, if the Alarm Table is currently displaying cards for each alarm entry instead of rows False
            otherwise.
        """
        return self._alarm_table_body.cards_are_displayed()

    def click(self, **kwargs) -> None:
        """:raises NotimplementedError: Because there's no reason you should blindly click the Alarm Table."""
        raise NotImplementedError('Please do not blindly click the Alarm Table.')

    def click_column_configuration_icon(self) -> None:
        """
        Click the icon which opens the Column Configuration modal.

        :raises TimeoutException: If the Column Configuration (gear) icon is not present.
        """
        self._alarm_table_toolbar.click_column_configuration_icon()

    def click_details_for_row(
            self,
            identifying_text: str,
            column_with_identifying_text: AlarmTableColumn) -> None:
        """
        Click the Details hover icon for a row based on unique text in a column.

        :param identifying_text: The text used to identify the row we will click the Details hover icon for.
        :param column_with_identifying_text: The Alarm Table Column which contains the identifying text.

        :raises TimeoutException: If no row contains the identifying text in the specified column, or if the Details
            hover icon never becomes visible.
        """
        self._alarm_table_body.click_details_for_row(
            column_text=identifying_text, column_with_identifying_text=column_with_identifying_text)
        
    def click_first_page_button(self) -> None:
        """
        Within the Pager, click the option which has text of 'First'. This does not mean the '1' option.

        :raises TimeoutException: If the 'First' option is not present.
        :raises AssertionError: If unsuccessful in getting the Alarm Table to page 1.
        """
        self._pager.click_first_page_button()
        IAAssert.is_equal_to(
            actual_value=self.get_active_page(),
            expected_value=1,
            as_type=int,
            failure_msg="Failed to get the Alarm Table to page 1 by clicking the 'First' option in the Pager.")

    def click_prefilter_icon(self) -> None:
        """
        Click the icon which opens the Conditional Prefilter popover/modal.

        :raises TimeoutException: If the Prefilter icon is not present.
        """
        self._alarm_table_toolbar.click_prefilter_icon()
        
    def click_last_page_button(self) -> None:
        """
        Within the Pager of the Alarm Table, click the 'Last' option.

        :raises TimeoutException: If the 'Last' option is not available.
        """
        self._pager.click_last_page_button()
        IAAssert.is_not_true(
            value=self.last_page_button_is_enabled(),
            failure_msg="Failed to get the Alarm Table to the last page by clicking the 'Last' option within the "
                        "Pager.")

    def click_gear_icon(self) -> None:
        """
        Click the icon which opens the Column Configuration modal. This function is just an 'alias', and redirects to
        :func:`click_column_configuration_icon`

        :raises TimeoutException: If the Column Configuration (gear) icon is not present.
        """
        self.click_column_configuration_icon()
        
    def click_next_page_chevron(self, binding_wait_time: float = 0) -> None:
        """
        Within the Pager, click the '>' option in order to go to the next page.

        :param binding_wait_time: How long to wait (in seconds) after clicking the '>' option before allowing code to
            continue.

        :raises TimeoutException: If the '>' option is not present.
        :raises AssertionError: If unsuccessful in advancing the Alarm Table to the next page.
        """
        original_page_number = self.get_active_page()
        self._pager.find().click()
        self._pager.click_next_page_chevron(binding_wait_time=binding_wait_time)
        IAAssert.is_equal_to(
            actual_value=self.get_active_page(),
            expected_value=original_page_number + 1,
            failure_msg="Failed to increment the page of the Alarm Table by clicking the '>' option within the Pager; "
                        "the '>' option may have been disabled.")
        
    def click_page_number(self, page_number: int) -> None:
        """
        Within the Pager of the Alarm Table, click a page number.

        :raises TimeoutException: If the supplied page number is not present.
        :raises AssertionError: If unsuccessful in setting the Alarm Table to display the supplied page.
        """
        self._pager.click_page_number(desired_page=page_number)
        IAAssert.is_equal_to(
            actual_value=self.get_active_page(),
            expected_value=page_number,
            as_type=int,
            failure_msg=f"Failed to set the Alarm Table to display page {page_number} by clicking that page number "
                        f"within the Pager.")
        
    def click_previous_page_chevron(self, binding_wait_time: float = 0) -> None:
        """
        Within the Pager, click the '<' option in order to go to the previous page.

        :param binding_wait_time: How long to wait (in seconds) after clicking the '<' option before allowing code to
            continue.

        :raises TimeoutException: If the '<' option is not present.
        :raises AssertionError: If unsuccessful in advancing the Alarm Table to the previous page.
        """
        original_page_number = self.get_active_page()
        self._pager.click_previous_page_chevron(binding_wait_time=binding_wait_time)
        IAAssert.is_equal_to(
            actual_value=self.get_active_page(),
            expected_value=original_page_number - 1,
            failure_msg="Failed to decrement the page of the Alarm Table by clicking the '<' option within the Pager; "
                        "the '<' option may have been disabled.")

    def click_remove_all_prefilters_button(self) -> None:
        """
        Click the 'Remove All' button in order to remove all Conditional Prefilters currently applied to the Alarm
        Table.

        :raises TimeoutException: If the 'Remove All' button is not present.
        :raises AssertionError: If unsuccessful in removing all applied Prefilters.
        """
        self._alarm_table_toolbar.click_remove_all_prefilters_button()
        IAAssert.is_equal_to(
            actual_value=self.get_count_of_applied_prefilters(),
            expected_value=0,
            failure_msg="Failed to remove all applied Prefilters by clicking the 'Remove All' button.")

    def click_show_all_for_events(self) -> None:
        """
        Click the 'Show All' option for the EVENT category.

        :raises TimeoutException: If the Prefilter popover/modal is not currently displayed.
        :raises IndexError: If the EVENT category is not present.
        """
        self._alarm_table_toolbar.click_show_all_for_events()

    def click_show_all_for_priorities(self) -> None:
        """
        Click the 'Show All' option for the PRIORITY category.

        :raises TimeoutException: If the Prefilter popover/modal is not currently displayed.
        :raises IndexError: If the PRIORITY category is not present.
        """
        self._alarm_table_toolbar.click_show_all_for_priorities()

    def close_any_open_popover_or_modal(self) -> None:
        """
        Close any open popover or modal.

        :raises TimeoutException: If no popover or modal is open.
        :raises AssertionError: If unsuccessful in closing all open popovers or modals.
        """
        self._alarm_table_toolbar.click_popover_or_modal_close_icon()
        IAAssert.is_not_true(
            value=self.column_configuration_popover_or_modal_is_open(),
            failure_msg="The Column Configuration popover/modal is still open after our attempt to close all open "
                        "popovers and/or modals.")
        IAAssert.is_not_true(
            value=self.prefilter_popover_or_modal_is_open(),
            failure_msg="The Prefilter popover/modal is still open after our attempt to close all open popovers "
                        "and/or modals.")
        IAAssert.is_not_true(
            value=self.details_modal_is_open(),
            failure_msg="The Details modal is still open after our attempt to close all open popovers and/or modals.")

    def collapse_text_filter(self) -> None:
        """
        Collapse the text filter of the Alarm Table. No action is taken if the filter is already collapsed.

        :raises AssertionError: If unsuccessful in collapsing the text filter.
        """
        self._alarm_table_filter.collapse_text_filter()

    def column_configuration_is_enabled(self) -> bool:
        """
        Determine if the user is able to access the Column Configuration (gear) icon.

        :returns: True, if the Column Configuration (gear) icon is present - False otherwise.
        """
        return self._alarm_table_toolbar.column_configuration_icon_is_present()

    def column_configuration_popover_or_modal_is_open(self) -> bool:
        """
        Determine if the Column Configuration popover/modal is open.

        :returns: True, if the Column Configuration popover/modal is open - False otherwise.
        """
        return self._alarm_table_toolbar.column_configuration_popover_or_modal_is_open()

    def column_is_present_in_column_configuration_popover(self, column: AlarmTableColumn) -> bool:
        """
        Determine if a column is present as a menu item in the Column Configuration popover/modal. Requires that the
        Column Configuration popover/modal already be open.

        :param column: The column to verify the presence of within the Column Configuration popover/modal.

        :returns: True, if the supplied column's name is present as an option in the Column Configuration
            popover/modal - False otherwise.

        :raises TimeoutException: If the Column Configuration popover/modal is not already open.
        """
        return self._alarm_table_toolbar.column_is_present_in_column_configuration_popover(column=column)

    def details_are_enabled(self) -> bool:
        """
        Determine if the Alarm Table allows for viewing details of an alarm entry.

        :returns: True, if after hovering over an alarm entry within the Alarm Table the Details hover icon appears
            - False otherwise.
        """
        return self._alarm_table_body.details_are_enabled()

    def details_modal_is_open(self) -> bool:
        """
        Determine if the modal which contains details about an Alarm entry is open.

        :returns: True, if a modal is open which contains information about the details of an Alarm - False otherwise.
        """
        return self._alarm_table_body.details_modal_is_open()

    def dismiss_prefilter_pill(self, prefilter: Union[AlarmState, AlarmPriority]) -> None:
        """
        Remove an applied Prefilter from being used as a condition for an Alarm to be displayed.

        :param prefilter: The applied State or Priority you would like to remove from use as a conditional filter.

        :raises TimeoutException: If the supplied prefilter is not already applied.
        :raises AssertionError: If unsuccessful in removing the supplied prefilter.
        """
        self._alarm_table_toolbar.dismiss_prefilter_pill(
            prefilter=prefilter)
        IAAssert.does_not_contain(
            iterable=self.get_text_of_applied_prefilters(),
            expected_value=prefilter.name,
            failure_msg=f"Failed to remove the {prefilter.name} prefilter from the applied filters.")

    def filtered_results_are_displayed(self) -> bool:
        """
        Determine if the applied filters are resulting in a displayed count of matching results.

        :returns: True, if the applied filters result in the display of a count of matching results - False otherwise.
        """
        return self._alarm_table_toolbar.filtered_results_are_displayed()
    
    def first_page_button_is_enabled(self) -> bool:
        """
        Determine if the Pager has a 'First' option which is enabled. This does not include the '1' option.

        :returns: True, if there is an enabled 'First' option within the Pager of the Alarm Table.
        """
        return self._pager.first_page_button_is_enabled()

    def get_notes_from_details_modal(self) -> str:
        """
        In an open Details modal, click the Notes tab and obtain the Notes from panel. Requires that the Details modal
        already be open.

        :returns: The notes supplied for the Alarm within the Notes tab.

        :raises TimeoutException: If the Details modal is not already open.
        """
        return self._alarm_table_body.get_notes_from_details_modal()

    def get_all_prefilter_options(self) -> List[str]:
        """
        Open the Prefilter popover/modal, obtain all available prefilters which could be selected by a user, and close
        the open modal.

        :returns: A list, where each entry is string representing an available Prefilter a user could select. These
            include the 'Show All' option, which will appear once for States and once for Priority.

        :raises TimeoutException: If the Prefilter icon is not present.
        :raises AssertionError: If unsuccessful in closing out the Prefilter modal.
        """
        try:
            if not self.prefilter_popover_or_modal_is_open():
                self.click_prefilter_icon()
            return self._alarm_table_toolbar.get_all_prefilter_options()
        finally:
            self.close_any_open_popover_or_modal()
            IAAssert.is_not_true(
                value=self.prefilter_popover_or_modal_is_open(),
                failure_msg="Failed to close the Prefilter popover/modal after retrieving available Prefilters.")

    def get_card_field_names(self) -> List[str]:
        """
        Obtain the field names listed within the displayed cards of the Alarm Table. Requires the Alarm table already
        be in a responsive layout, where it is rendering row content as cards.

        :returns: A list, where each item is the name of a field in the displayed cards, where the fields could be
            interpreted as being equivalent to a column from a row.

        :raises TimeoutException: If the Alarm Table is not in a responsive layout.
        """
        return self._alarm_table_body.get_card_column_names()

    def get_color_of_first_row_which_matches_criteria(self, text_criteria: str, column: AlarmTableColumn) -> str:
        """
        Obtain the color in use for the background of the first row which meets the criteria set forth within arguments.
        Note that this color may come back in different formats (RGB vs hex) depending on the type of browser being
        used.

        :param text_criteria: The 'unique' text found in the specified column.
        :param column: The Alarm table Column which contains the supplied unique text.

        :returns: The color in use for the first row which has the supplied text in the specified column.

        :raises TimeoutException: If no row contains the supplied text in the specified column.
        """
        return self._alarm_table_body.get_color_of_first_row_which_matches_criteria(
            text_criteria=text_criteria, column=column)

    def get_column_index(self, alarm_table_column: AlarmTableColumn) -> int:
        """
        Obtain the index of the specified column. Note that the Alarm Status Table has a selection column which is
        always the 0th column.

        :param alarm_table_column: The Alarm Table Column of which you would like the index.

        :returns: The index of the specified row.

        :raises TimeoutException: If the specified row is not present in the Alarm Table.
        """
        return self._alarm_table_header.get_column_index(column_id=alarm_table_column.data_column_id)

    def get_column_width(self, alarm_table_column: AlarmTableColumn, include_units: bool = False) -> str:
        """
        Obtain the width of the specified column.

        :param alarm_table_column: The Alarm Table Column you would like the width of.
        :param include_units: Dictates whether the returned value contains units of measurement.

        :returns: The width of the specified column, with the option of units of measurement.

        :raises TimeoutException: If the requested column is not present in the Alarm Table.
        """
        # Tables expect each column id to be the name, whereas Alarm Tables construct a camel-cased id.
        return super().get_column_width(column_id=alarm_table_column.data_column_id, include_units=include_units)

    def get_column_value_from_first_row_with_text_in_column(
            self,
            desired_column: AlarmTableColumn,
            sibling_column_text: str,
            sibling_column: AlarmTableColumn) -> str:
        """
        Obtain the value of a column within a row based on the value present in a sibling column.

        :param desired_column: The column you want a value from.
        :param sibling_column_text: The (string) value present in a sibling column of the same row.
        :param sibling_column: The sibling column which contains the supplied known text.

        :returns: The string value of the cell identified by the specified column within the row which has the supplied
            text in the specified sibling column.

        :raises TimeoutException: If no sibling cell has the supplied text in the specified column, or if either of the
            columns is not present in the Alarm Table.
        """
        self._alarm_table_body.wait_until_column_is_present(column=desired_column)
        return self._alarm_table_body.get_cell_data_by_other_cell_text(
            desired_column=desired_column, sibling_cell_text=sibling_column_text, sibling_column=sibling_column)

    def get_column_value_by_row_index(self, row_index: int, column: AlarmTableColumn) -> str:
        """
        Obtain the string value of the cell identified by the intersection of the provided row index and Alarm Table
        Column.

        :param row_index: The zero-based row index which has the desired cell.
        :param column: The Alarm Table Column under which the desired cell resides.

        :returns: The string value of the cell identified by the intersection of the supplied row index and column.

        :raises TimeoutException: If the row index is not displayed, or the supplied column is not present in the Alarm
            Table.
        """
        return self._alarm_table_body.get_column_value_by_row_index(row_index=row_index, column=column)

    def get_count_of_applied_prefilters(self) -> int:
        """
        Obtain a count of prefilters applied to the Alarm Table.

        :returns: The number of Prefilters currently applied to the Alarm Table.
        """
        try:
            return len(self.get_text_of_applied_prefilters())
        except TimeoutException:
            return 0

    def get_count_of_displayed_rows(self) -> int:
        """
        Obtain a count of rows visually displayed within the Alarm Table. This is not a count of total rows - this is
        a count of rows the user can see on the current page, including after scrolling.

        :returns: The count of rows displayed on the current page of the Alarm Table.
        """
        # alarm tables have no concept of subview, so explicitly exclude subviews from the count
        return self._alarm_table_body.get_row_count(
            include_expanded_subviews_in_count=False)

    def get_count_of_results_matching_text_filter(self) -> int:
        """
        Obtain a count of how many results match all applied filtering.

        :returns: A count of results which match all applied filters.
        """
        return self._alarm_table_toolbar.get_count_of_results_matching_text_filter()
    
    def get_active_page(self) -> int:
        """
        Obtain the number of the page the user is currently viewing.

        :returns: The page number the user is currently viewing.

        :raises TimeoutException: If the Alarm Table does not have an enabled Pager.
        """
        return self._pager.get_active_page()

    def get_last_displayed_page_number(self) -> int:
        """
        Obtain the number of the last page number displayed to the user within the Pager. This may not be the last page
        a user could get to.

        :returns: The current last displayed page number within the Pager.

        :raises TimeoutException: If the Alarm Table does not have an enabled Pager.
        """
        return self._pager.get_last_displayed_page_number()

    def get_empty_message_text(self) -> str:
        """
        Obtain the message displayed to the user when the Alarm Table has no results which match the applied filters.

        :returns: The text displayed to the user when the Alarm Table has no results which match the applied filters.

        :raises TimeoutException: If the message is not present.
        """
        return self._alarm_table_body.get_empty_message_text()

    def get_field_from_details_modal(self, field_name: str) -> str:
        """
        Obtain the value of a field within the Details modal. Requires that the Details modal already be open.

        :param field_name: The case-sensitive field to retrieve from the Details modal.

        :returns: The text value of the requested field.

        :raises NoSuchElementException: If the value for the field is missing.
        :raises NullPointerException: If the supplied field does not exist.
        :raises TimeoutException: If the Details modal is not present.
        """
        return self._alarm_table_body.get_field_from_details_modal(field_name=field_name)

    def get_origin_of_remove_all_prefilters_button(self) -> Point:
        """
        Obtain the location of the upper-left corner of the 'Remove All' button.

        :returns: A two-dimensional point which represents the location of the upper-left corner of the 'Remove All'
            button.

        :raises TimeoutException: If the 'Remove All' button is not present.
        """
        return self._alarm_table_toolbar.get_origin_of_remove_all_prefilters_button()

    def get_text_of_alarm_events_label(self) -> str:
        """
        Obtain the full text of the filtered results label.

        :returns: The full text of the label which describes the count of filtered results.

        :raises TimeoutException: If no filtering is applied.
        """
        return self._alarm_table_toolbar.get_text_of_filter_results()

    def get_text_of_all_columns_in_popover(self) -> List[str]:
        """
        Obtain all columns available for display from within the column configuration popover/modal.

        :returns: A list, where each item is the text of a column which is available for display in the Alarm Table.

        :raises TimeoutException: If the column configuration popover/modal is not already open.
        """
        return self._alarm_table_toolbar.get_text_of_all_columns_in_popover()

    def get_text_of_applied_filters_label(self) -> str:
        """
        Obtain the text of the label preceding the applied conditional filters, which usually appears as 'FILTERS (X):'
        (after any translations have been applied).

        :returns: The text of the label which describes how many conditional filters are currently applied.

        :raises TimeoutException: If no conditional filters are currently applied.
        """
        return self._alarm_table_toolbar.get_text_of_applied_filter_count_label()

    def get_text_of_applied_prefilters(self) -> List[str]:
        """
        Obtain the text of all applied State and Priority conditional filters.

        :returns: A list which contains the text of all applied conditional (State/Priority) filters. An empty list
            implies no prefilters are applied.
        """
        return self._alarm_table_toolbar.get_text_of_applied_prefilters()

    def get_text_of_remove_all_prefilters_button(self) -> str:
        """
        Obtain the text of the 'Remove All' button (after any translations have been applied).

        :returns: The text in use by the 'Remove All' button.

        :raises TimeoutException: If the 'Remove All' button is not currently in place.
        """
        return self._alarm_table_toolbar.get_text_of_remove_all_prefilters_button()

    def get_text_of_filter_results(self) -> str:
        """
        Obtain the full text of the filtered results label.

        :returns: The full text of the label which describes the count of filtered results.

        :raises TimeoutException: If no filtering is applied.
        """
        return self._alarm_table_toolbar.get_text_of_filter_results()
    
    def jump_to_page(self, page_number: int, binding_wait_time: float = 1) -> None:
        """
        Use the page jump input field to go to a specific page in the Table.

        :param page_number: The page of the Table to go to.
        :param binding_wait_time: The amount of time (in seconds) to wait after supplying the page number before
            allowing code to continue.

        :raises TimeoutException: If the page jump input is not present.
        :raises AssertionError: If the Table does not end up on the supplied page.
        """
        self._pager.jump_to_page(page_to_jump_to=page_number, binding_wait_time=binding_wait_time)

    def results_label_is_displayed(self) -> bool:
        """
        Determine if filtering of any type is in place on the Alarm Table.

        :returns: True, if any conditional or text filtering is currently applied to the Alarm Table.
        """
        return self._alarm_table_toolbar.filtered_results_are_displayed()

    def get_width_of_remove_all_prefilters_button(self, include_units: bool = False) -> str:
        """
        Obtain the width of the 'Remove All' button, with or without units.

        :param include_units: If True, the returned value will contain units of measurement, otherwise the returned
            value will be only the numeric value.

        :returns: The width of the 'Remove All' button, and potentially units.

        :raises TimeoutException: If the 'Remove All' button is not currently in place.
        """
        return self._alarm_table_toolbar.get_width_of_remove_all_prefilters_button(include_units=include_units)

    def is_in_responsive_layout(self) -> bool:
        """
        Determine if the Alarm Table is in a responsive (card) layout.

        :returns: True, if the Alarm Table is currently rendering in a responsive layout - False otherwise.
        """
        return self._alarm_table_body.is_in_responsive_layout()
    
    def last_page_button_is_enabled(self) -> bool:
        """
        Determine if the 'Last' page option is enabled in the Pager.

        :returns: True, if the 'Last' page option in the Pager is enabled.

        :raises TimeoutException: If the 'Last' page option is not present in the Pager.
        """
        return self._pager.last_page_button_is_enabled()
    
    def next_page_chevron_is_enabled(self) -> bool:
        """
        Determine if the next page chevron is enabled.

        :returns: True, if the next page chevron is enabled - False otherwise.
        """
        return self._pager.next_page_chevron_is_enabled()

    def open_prefilter_popover(self) -> None:
        """
        Open the popover/modal which contains the States and Priorities available to apply as conditional filters.

        :raises TimeoutException: If the icon required to expand the popover/modal is not present.
        """
        if not self._alarm_table_toolbar.prefilter_popover_or_modal_is_displayed():
            self._alarm_table_toolbar.click_prefilter_icon()
            
    def pager_is_hidden(self) -> bool:
        """
        Determine if the Pager exists but is currently hidden.

        :returns: True, if the Pager exists in the DOM but is currently out of sight of the user.

        :raises TimeoutException: If the Pager is not present at all.
        """
        return self._pager.is_hidden()
            
    def pager_is_present(self) -> bool:
        """
        Determine if the Pager exists within the Table. Note that this does not reflect the VISIBILITY of the
        Pager.

        :returns: True, if the Pager exists, False otherwise.
        """
        return self._pager.is_present()

    def prefilter_is_applied(self, prefilter: Union[AlarmState, AlarmPriority]) -> bool:
        """
        Determine if a Prefilter is currently applied as a conditional prefilter.

        :param prefilter: The prefilter to verify as a current conditional prefilter.

        :returns: True, if the supplied Prefilter is currently applied as a conditional filter - False otherwise.
        """
        return self._alarm_table_toolbar.prefilter_is_applied(
            prefilter=prefilter)

    def prefilter_popover_or_modal_is_open(self) -> bool:
        """
        Determine if the State and Priority conditional filter popover/modal is displayed.

        :returns: True, if the State/Priority popover/modal is currently displayed - False otherwise.
        """
        return self._alarm_table_toolbar.prefilter_popover_or_modal_is_displayed()

    def prefiltering_is_enabled(self) -> bool:
        """
        Determine if the Alarm Table allows for applying States and/or Priorities as conditional prefilters to determine
        the display state of Alarms.

        :returns: True, if the user has access to the icon which would allow for opening the State and Priority
            conditional prefilter popover/modal.
        """
        return self._alarm_table_toolbar.prefiltering_icon_is_displayed()

    def previous_page_chevron_is_enabled(self) -> bool:
        """
        Determine if the previous page chevron is enabled.

        :returns: True, if the previous page chevron is enabled - False otherwise.

        :raises TimeoutException: If the previous page chevron is not present.
        """
        return self._pager.previous_page_chevron_is_enabled()

    def set_displayed_row_count(self, desired_row_count: int) -> None:
        """
        Set the number of displayed rows in the Table. The count of rows must be a valid value from the
        dropdown (Select) in the Pager.

        :param desired_row_count: The desired count of rows (this must be one of the available values in the dropdown).

        :raises TimeoutException: If the row count dropdown is not present.
        :raises AssertionError: If unable to set the row count dropdown to the supplied row count.
        """
        self._pager.set_displayed_row_count(count_of_rows=desired_row_count)

    def set_display_state_of_alarm_table_columns(
            self,
            alarm_table_columns: List[AlarmTableColumn],
            should_be_displayed: bool) -> None:
        """
        Open the column configuration popover/modal and set the display state of multiple Alarm Table Columns.

        :param alarm_table_columns: A list of Alarm Table Columns for which we will set the display state of each.
        :param should_be_displayed: If True, the supplied columns will be set as an active selection. If False the
            supplied columns will be set as inactive selections, removing them from display.
        """
        self._alarm_table_toolbar.set_display_state_of_known_alarm_columns(
            list_of_known_alarm_columns=alarm_table_columns, should_be_displayed=should_be_displayed)

    def text_filtering_is_enabled(self) -> bool:
        """
        Determine if text filtering is enabled for the Alarm Table.

        :returns: True, if the icon (magnifying glass) which would expand the text filter is present in the DOM - False
            otherwise.
        """
        return self._alarm_table_filter.text_filtering_is_enabled()

    def toolbar_is_displayed(self) -> bool:
        """
        Determine if the Alarm Table is currently displayed.

        :returns: True, if the Alarm Table is currently displayed - False otherwise.
        """
        return self._alarm_table_toolbar.is_displayed()

    def wait_for_row_count(
            self, expected_count: Optional[int] = None):
        """
        Obtain a count of rows in the Alarm Table.

        :param expected_count: If supplied, the function will wait some short period of time until this number of rows
            appears.

        :returns: A count of rows in the Alarm Table.
        """
        return self._alarm_table_body.wait_for_row_count(
            include_expanded_subviews_in_count=False, expected_count=expected_count)


class _AlarmTableBody(Body):
    """The Body of an Alarm Table."""
    _ROW_INDEX_ATTRIBUTE = 'data-row-index'
    _COL_INDEX_ATTRIBUTE = 'data-column-index'
    _COLUMN_HEADERS_CELLS_LOCATOR = (By.CSS_SELECTOR, 'div.th div.tr.header .tc')
    _COLUMN_HEADER_CHECKBOX_LOCATOR = (By.CSS_SELECTOR, 'label.ia_checkbox svg')
    _ALARM_TABLE_ROWS_LOCATOR = (By.CSS_SELECTOR, '.tr.alarmTableBodyRow')
    _ROW_SELECTION_OVERLAY_LOCATOR = (By.CSS_SELECTOR, 'div.rowSelectedOverlay')
    _CARD_LOCATOR = (By.CSS_SELECTOR, 'div.tc div.tr')
    _DETAILS_LOCATOR = (By.CSS_SELECTOR, "div.alarmRowActionOverlay")
    _DETAILS_MODAL_LOCATOR = (By.CSS_SELECTOR, 'div.alarmDetailsModal')
    _DETAILS_MODAL_NOTES_TAB_LOCATOR = (By.CSS_SELECTOR, "div.notesTab")
    _DETAILS_MODAL_PROPERTIES_TAB_LOCATOR = (By.CSS_SELECTOR, "div.detailsTab")
    _DETAILS_MODAL_ALARM_NOTES_LOCATOR = (By.CSS_SELECTOR, "div.alarmNotesContainer textarea")
    _EMPTY_MESSAGE_LOCATOR = (
        By.CSS_SELECTOR, "div.alarmTableEmptyMessage")  # Different locator than the "common" table

    def __init__(
            self,
            driver: WebDriver,
            parent_locator_list: List[Tuple[By, str]],
            wait_timeout: float = 10,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        # OVERWRITE inherited piece
        self._rows = ComponentPiece(
            locator=self._ALARM_TABLE_ROWS_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._cards = ComponentPiece(
            locator=self._CARD_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._cells_of_column_dict = {}
        self._card_labels_dict = {}
        self._details_hover_piece = ComponentPiece(
            locator=self._DETAILS_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._details_modal = ComponentPiece(
            locator=self._DETAILS_MODAL_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            poll_freq=poll_freq)
        self._details_modal_rows = ComponentPiece(
            locator=(By.CSS_SELECTOR, "div.alarmPropertiesCategoryTableRow"),
            driver=self.driver,
            parent_locator_list=self._details_modal.locator_list,
            poll_freq=poll_freq)
        self._properties_tab_in_details_modal = ComponentPiece(
            locator=self._DETAILS_MODAL_PROPERTIES_TAB_LOCATOR,
            driver=driver,
            parent_locator_list=self._details_modal.locator_list,
            poll_freq=poll_freq)
        self._notes_tab_in_details_modal = ComponentPiece(
            locator=self._DETAILS_MODAL_NOTES_TAB_LOCATOR,
            driver=driver,
            parent_locator_list=self._details_modal.locator_list,
            poll_freq=poll_freq)
        self._notes_field = ComponentPiece(
            locator=self._DETAILS_MODAL_ALARM_NOTES_LOCATOR,
            driver=driver,
            parent_locator_list=self._details_modal.locator_list,
            poll_freq=poll_freq)
        self._selected_rows = ComponentPiece(
            locator=self._ROW_SELECTION_OVERLAY_LOCATOR,
            driver=driver,
            parent_locator_list=self._rows.locator_list,
            poll_freq=poll_freq)
        self._empty_message = ComponentPiece(
            locator=self._EMPTY_MESSAGE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)

    def cards_are_displayed(self) -> bool:
        """
        Determine if cards are displayed within the Alarm Table, as opposed to rows.

        :returns: True, if the Alarm Table is rendering results in a 'card' layout - False otherwise.
        """
        try:
            return self.get_row_count() > 0 and len(self._cards.find_all()) > 0
        except TimeoutException:
            return False

    def click_details_for_row(
            self,
            column_text: str,
            column_with_identifying_text: AlarmTableColumn) -> None:
        """
        Click the Details hover icon for the first row with a supplied value in a specified column.

        :param column_text: The text present in the specified column. This will be used to identify the row we will be
            hovering over before clicking the Details hover icon.
        :param column_with_identifying_text: The Alarm Table Column which contains the supplied text.

        :raises TimeoutException: If no row contains the supplied text in the specified column.
        """
        try:
            self.wait.until(IAec.function_returns_true(
                custom_function=self._click_details_for_row_with_text_in_column,
                function_args={"text_in_column": column_text, "column": column_with_identifying_text}))
        except TimeoutException as toe:
            raise TimeoutException(
                msg=f"Unable to click details element for row with text {column_text} in the "
                    f"{column_with_identifying_text.name} column.") from toe

    def details_are_enabled(self) -> bool:
        """
        Determine if the ability to open a Details popover/modal is enabled for the Alarm Table.

        :returns: True, if a user sees a Details hover icon when hovering over thw rows of the Alarm Table - False
            otherwise.
        """
        IASelenium(driver=self.driver).hover_over_web_element(web_element=self._rows.find_all()[0])
        try:
            return self._details_hover_piece.find() is not None
        except TimeoutException:
            return False

    def details_modal_is_open(self) -> bool:
        """
        Determine if the popover/modal which displays details for an Alarm is currently open.

        :returns: True, if the Details popover/modal is currently open - False otherwise.
        """
        try:
            return self._details_modal.find(wait_timeout=0.5) is not None
        except TimeoutException:
            return False

    def get_card_column_names(self) -> List[str]:
        """
        Obtain a list of all displayed 'column' names displayed in the cards of the Alarm Table. Requires the Table
        already be displaying in a responsive (card) layout.

        :returns: A list where each element is the name of a column displayed as a field of the card.

        :raises TimeoutException: If the Alarm Table is not already displaying in a responsive (card) layout.
        """
        return [_.text for _ in self._get_card_labels_by_row_index(zero_based_row_index=0).find_all()]

    def get_cell_data_by_other_cell_text(
            self,
            desired_column: AlarmTableColumn,
            sibling_cell_text: str,
            sibling_column: AlarmTableColumn) -> str:
        """
        Obtain the value of a cell based on information from a sibling cell in the same row.

        :param desired_column: The column from which you would like the value.
        :param sibling_cell_text: The text present in the supplied sibling column.
        :param sibling_column: The sibling column which contains the known value.

        :returns: The value of the desired column.

        :raises KeyError: If the desired column is not currently displayed.
        :raises TimeoutException: If the specified sibling column does not contain the supplied text in any row, or if
            the desired column is not displayed.
        """
        try:
            data_row_id = self._get_complex_cell(
                cell_text=sibling_cell_text,
                column=sibling_column).find().find_element(*(By.XPATH, "../../..")).get_attribute("data-row-id")
            return self._get_row_data_as_dict(
                alarm_event_id=data_row_id)[desired_column.data_column_id]
        except StaleElementReferenceException:
            return self.get_cell_data_by_other_cell_text(
                sibling_cell_text=sibling_cell_text, desired_column=desired_column, sibling_column=sibling_column)

    def get_color_of_first_row_which_matches_criteria(self, text_criteria: str, column: AlarmTableColumn) -> str:
        """
        Obtain the color of the first row which contains some supplied text in a specific column. Note that different
        browsers may return this value in different formats (RGB vs hex).

        :param text_criteria: The text which must be present in the supplied Alarm Table Column.
        :param column: The Alarm Table Column which must have the supplied text.

        :returns: The color (as a string) of the first row which contains the supplied text in the specified column.

        :raises: TimeoutException: If no row contains the supplied text in the specified column.
        """
        return self._get_complex_cell(
            cell_text=text_criteria, column=column).find().value_of_css_property('background-color')

    def get_column_value_by_row_index(self, row_index: int, column: AlarmTableColumn) -> str:
        """
        Obtain the value of a specified column within a specified row.

        :param row_index: The zero-based index of the row.
        :param column: The Alarm Table Column from which you would like the value.

        :returns: The value of the cell at the intersection of the supplied row index and column.

        :raises TimeoutException: If the row index is not currently displayed, or if the supplied column is not
            displayed.
        """
        return self._get_complex_cell(column=column, row_index=row_index).find().text

    def get_empty_message_text(self) -> str:
        """
        Obtain the message displayed to the user when the Alarm Table has no results which match the applied filters.

        :returns: The text displayed to the user when the Alarm Table has no results which match the applied filters.

        :raises TimeoutException: If the message is not present.
        """
        # This uses a different locator than the "common" table
        return self._empty_message.get_text().strip()

    def get_field_from_details_modal(self, field_name: str) -> str:
        """
        Obtain the value of a field within the Details modal. Requires that the Details modal already be open.

        :param field_name: The case-sensitive field to retrieve from the Details modal.

        :returns: The text value of the requested field.

        :raises NoSuchElementException: If the value for the field is missing.
        :raises NullPointerException: If the supplied field does not exist.
        """
        try:
            return self._get_details_modal_row(
                label_text=field_name).find_element(*(By.CSS_SELECTOR, "div.alarmPropertiesCategoryTableProp")).text
        except StaleElementReferenceException:
            return self.get_field_from_details_modal(field_name=field_name)

    def get_notes_from_details_modal(self) -> str:
        """
        Click the Notes tab and obtain the Ack Notes from the Details popover/modal. Requires the Details popover/modal
        already be open.

        :returns: The text visible in the Ack Notes field for the Alarm which is currently displaying a Details
            popover/modal.

        :raises TimeoutException: If the Details popover/modal is not already open.
        """
        self._notes_tab_in_details_modal.click(wait_timeout=1)
        return self._notes_field.find(wait_timeout=1).text

    def get_selection_state_for_rows(self, known_value: str, column_for_value: AlarmTableColumn) -> List[bool]:
        """
        Obtain the selection state of all rows which have a known value within a specified column.

        :param known_value: A value known to be present in the specified column.
        :param column_for_value: The column which contains the supplied value.

        :returns: A list, where each element in the list is a boolean value which represents the selection state of a
            row which had the known value within the specified column.

        :raises TimeoutException: If no rows contain the supplied value in the specified column.
        :raises AssertionError: If no rows contain the supplied value in the specified column.
        """
        indices = []
        for cell_web_element in self._get_complex_cell(column=column_for_value, cell_text=known_value).find_all():
            indices.append(
                int(cell_web_element.find_element(*(By.XPATH, "../..")).get_attribute(self._ROW_INDEX_ATTRIBUTE)))
        IAAssert.is_greater_than(
            left_value=len(indices),
            right_value=0,
            failure_msg=f"No rows contained {known_value} in the {column_for_value.name} column.")
        return self.wait.until(IAec.function_returns_true(
            custom_function=self._get_selection_state_for_rows,
            function_args={
                "indices": indices
            }
        ))

    def is_in_responsive_layout(self) -> bool:
        """
        Determine if the Alarm Table is in a responsive (card) layout.

        :returns: True, if the Alarm Table is currently rendering in a responsive layout - False otherwise.
        """
        return 'tableIsResponsive' in self.find().get_attribute("class")

    def wait_until_column_is_present(self, column: AlarmTableColumn) -> None:
        """
        Wait until the specified column is displayed within the Alarm Table.

        :param column: The Alarm Table Column to wait upon the appearance of.

        :raises TimeoutException: If the column never becomes visible.
        """
        try:
            self.wait.until(IAec.function_returns_true(
                custom_function=self._column_is_present, function_args={"column": column}))
        except TimeoutException as toe:
            raise TimeoutException(msg=f"Missing column in Alarm Table: {column.data_column_id}.") from toe

    def _click_details_for_row_with_text_in_column(self, text_in_column: str, column: AlarmTableColumn) -> bool:
        """
        Click the Details hover icon for a row with the supplied text in the specified column, and then report back
        on the success of the opening of the modal.

        :param text_in_column: The text present in the supplied column.
        :param column: The Alarm Table Column which contains the supplied text.

        :returns: True, if the click resulted in the opening of the Details modal - False if unable to locate the
            desired row based on the supplied information, or if the Details modal did not open.
        """
        try:
            self._get_complex_cell(cell_text=text_in_column, column=column).hover()
            self._details_hover_piece.click(wait_timeout=5, binding_wait_time=1)
            self.wait.until(IAec.function_returns_true(
                custom_function=self.details_modal_is_open,
                function_args={}))
            return True
        except (StaleElementReferenceException, TimeoutException):
            return False

    def _column_is_present(self, column: AlarmTableColumn) -> bool:
        """
        Determine if a column is present in the Alarm Table.

        :param column: The Alarm Table Column which we will verify is currently present.

        :returns: True, if any cells can be found for the supplied Alarm Table Column - False otherwise.
        """
        try:
            return len(self._get_cells_of_column(column=column).find_all()) > 0
        except TimeoutException:
            return False

    def _get_card_labels_by_row_index(self, zero_based_row_index: Union[int, str]) -> ComponentPiece:
        """
        Obtain a ComponentPiece which defines the columns available within the card which represents an Alarm row while
        in a responsive layout.

        :param zero_based_row_index: The zero-based index of the row the card belongs to.
        """
        _label_pieces = self._card_labels_dict.get(zero_based_row_index)
        if not _label_pieces:
            locator = (By.CSS_SELECTOR, 'div.tc[data-column-id="label"]')
            _label_pieces = ComponentPiece(
                locator=locator,
                driver=self.driver,
                parent_locator_list=self._get_row_component_by_row_index(
                    zero_based_row_index=zero_based_row_index).locator_list,
                poll_freq=self.poll_freq)
            self._card_labels_dict[zero_based_row_index] = _label_pieces
        return _label_pieces

    def _get_cells_of_column(self, column: AlarmTableColumn) -> ComponentPiece:
        """
        Obtain a ComponentPiece which defines AL cells which belong to an Alarm Table Column.

        :param column: The Alarm Table Column under which al of the cells should reside.
        """
        column_id = column.data_column_id
        _cells_of_column = self._cells_of_column_dict.get(column_id)
        if not _cells_of_column:
            locator = (By.CSS_SELECTOR, f'div.tc.ia_table__cell[data-column-id="{column_id}"]')
            _cells_of_column = ComponentPiece(
                locator=locator,
                driver=self.driver,
                parent_locator_list=self.locator_list,
                poll_freq=self.poll_freq)
            self._cells_of_column_dict[column_id] = _cells_of_column
        return _cells_of_column

    def _get_complex_cell(
            self, column: AlarmTableColumn, row_index: int = 0, cell_text: Optional[str] = None) -> ComponentPiece:
        """
        Obtain a specific cell within the Table, based on information known about the cell.

        :param column: The Alarm Table Column this cell belongs to.
        :param row_index: The zero-based index of the row which contains the cell.
        :param cell_text: The known text of the cell.

        :returns: A ComponentPiece which defines the cell described by the supplied parameters.
        """
        column_id = column.data_column_id
        identifying_tuple = (column_id, row_index, cell_text)
        _cells_of_column = self._cells_of_column_dict.get(identifying_tuple)
        if not _cells_of_column:
            row_index_piece = f'[{self._ROW_INDEX_ATTRIBUTE}="{row_index}"]' if row_index else ""
            # leading space is important here
            cell_text_piece = f' div[title="{cell_text}"]' if cell_text else ""
            locator = (By.CSS_SELECTOR, f'div[data-column-id="{column_id}"]{row_index_piece}{cell_text_piece}')
            _cells_of_column = ComponentPiece(
                locator=locator,
                driver=self.driver,
                parent_locator_list=self._rows.locator_list,
                poll_freq=self.poll_freq)
            self._cells_of_column_dict[identifying_tuple] = _cells_of_column
        return _cells_of_column

    def _get_details_modal_row(self, label_text: str) -> Optional[WebElement]:
        """
        Obtain the WebElement which represents the key:value pairing of Alarm properties inside the Details modal.

        :param label_text: The case-sensitive field name which identifies the row to be returned.

        :returns: The WebElement which contains the field and value pieces based on the label text, or None if no field
            matched the supplied text.
        """
        for row in self._details_modal_rows.find_all():
            if label_text == row.find_element(*(By.CSS_SELECTOR, "div.alarmPropertiesCategoryTableLabel")).text:
                return row
        return None

    def _get_row_component_by_alarm_event_id(self, alarm_event_id: str) -> ComponentPiece:
        """
        Obtain a ComponentPiece which defines a row.

        :param alarm_event_id: The Event ID of the alarm you would like the row of.
        """
        return ComponentPiece(
            locator=(By.CSS_SELECTOR, f'{self._ALARM_TABLE_ROWS_LOCATOR[1]}[data-row-id="{alarm_event_id}"]'),
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=self.poll_freq)

    def _get_row_component_by_row_index(self, zero_based_row_index: Union[int, str]) -> ComponentPiece:
        """
        Obtain a ComponentPiece which defines a row.

        :param zero_based_row_index: The zero-based index of the alarm you would like the row of.
        """
        return ComponentPiece(
            locator=(By.CSS_SELECTOR, f'{self._ALARM_TABLE_ROWS_LOCATOR[1]}[data-row-index="{zero_based_row_index}"]'),
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=self.poll_freq)

    def _get_row_data_as_dict(self, alarm_event_id: str) -> dict:
        """
        Obtain the contents of the cells of the row where the keys of the returned dictionary are case-sensitive
            matches to the IDs of the columns.

        :param alarm_event_id: The Event ID which belongs to the row you would like returned.

        :returns: A dictionary where the keys are case-sensitive matches to the columns of the Alarm Table.

        :raises TimeoutException: If the supplied Alarm Event ID does not match any displayed row.
        """
        row_data = {}
        _row = self._get_row_component_by_alarm_event_id(
            alarm_event_id=alarm_event_id)
        try:
            cells = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'>div'),
                driver=self.driver,
                parent_locator_list=_row.locator_list,
                wait_timeout=0,
                poll_freq=self.poll_freq).find_all()
            for cell in cells:
                row_data[cell.get_attribute("data-column-id")] = cell.text
        except TimeoutException:
            # column not displayed
            pass
        return row_data

    def _get_selection_state_for_rows(self, indices: List[Union[int, str]]) -> Union[List[bool], bool]:
        """
        Return a list which contains the selection state of all rows with the supplied indices, or False if the Alarm
        Table updates while determining the state of the rows.

        :param indices: A list of zero-based indices for rows from which you want information about the selection state.
            These values may be integers or numeric strings.

        :returns: A list which describes the selection state for each row with one of the supplied indices, or False if
            the Alarm Table updates while determining the selection state of the entire list.

        :raises AssertionError: If the length of the returned list does not match the length of the list of requested
            indices.
        :raises ValueError: If any of the supplied indices is invalid.
        """
        try:
            indices = [int(_) for _ in indices]
            selection_state_list = []
            row_elements = self._rows.find_all()
            for row in row_elements:
                if int(row.get_attribute(self._ROW_INDEX_ATTRIBUTE)) in indices:
                    try:
                        row.find_element(*self._ROW_SELECTION_OVERLAY_LOCATOR)
                        selection_state_list.append(True)
                    except NoSuchElementException:
                        selection_state_list.append(False)
            # If it gets through all the row elements without an SERE then we return the list otherwise try again
            IAAssert.is_equal_to(
                actual_value=len(selection_state_list),
                expected_value=len(indices),
                failure_msg="Our requested list of indices contained an index which fell outside of the listed indices "
                            "of the page.")
            return selection_state_list
        except StaleElementReferenceException:
            return False


class _AlarmTableFilter(Filter):
    """
    The Alarm Table Filter, where text filtering and conditional filtering based on State and/or Priority occurs.
    """
    _FILTER_ICON_LOCATOR = (By.CSS_SELECTOR, "div.alarmFilterToggle")
    _CONTAINER_LOCATOR = (By.CSS_SELECTOR, 'div.toggleableAlarmFilter')
    _COLLAPSE_ICON_LOCATOR = (By.CSS_SELECTOR, 'div.closeFilterToggle svg')

    def __init__(
            self,
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 1,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._filter_icon = ComponentPiece(
            locator=self._FILTER_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=parent_locator_list,
            poll_freq=poll_freq)
        self._container = ComponentPiece(
            locator=self._CONTAINER_LOCATOR,
            driver=driver,
            parent_locator_list=parent_locator_list,
            poll_freq=poll_freq)
        self._collapse_icon = ComponentPiece(
            locator=self._COLLAPSE_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self._container.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)

    def collapse_text_filter(self) -> None:
        """
        Collapse the text filter. No action is taken if the text filter is already collapsed.

        :raises AssertionError: If unsuccessful in collapsing the text filter.
        """
        if self.filter_is_expanded():
            try:
                self._collapse_icon.click(binding_wait_time=1)
            except ElementNotInteractableException:
                pass
            except TimeoutException:
                pass
        IAAssert.is_not_true(
            value=self.filter_is_expanded(),
            failure_msg="The text filter was still expanded after an attempt to collapse it.")

    def expand_filter(self) -> None:
        """
        Expand the text filter located at the top of the Alarm Table if it is not already expanded. No action is taken
        if the filter is already expanded.

        :raises AssertionError: If unsuccessful in collapsing the text filter.
        """
        if not self.filter_is_expanded():
            try:
                self._filter_icon.click(wait_timeout=1)
                self.filter_is_expanded()  # glorified wait for the animation of the filter expansion
            except ElementNotInteractableException as enie:
                # This error is sometimes thrown even though the click registers.
                if not self.filter_is_expanded():
                    raise enie
                else:
                    pass
            except TimeoutException as toe:
                if not self.filter_is_expanded():
                    raise toe
                else:
                    pass
        IAAssert.is_true(
            value=self.filter_is_expanded(),
            failure_msg="The text filter was not expanded after attempting to expand it.")

    def filter_is_expanded(self) -> bool:
        """
        Determine if the text filter is expanded.

        :returns: True, if the text filter is expanded - False otherwise.
        """
        try:
            expanded = WebDriverWait(
                driver=self.driver,
                timeout=1,
                poll_frequency=self.poll_freq).until(
                IAec.function_returns_true(custom_function=self._filter_is_expanded, function_args={}))
            if expanded:
                # wait for any animation to complete
                self.wait_on_binding(time_to_wait=self.wait_timeout)
            return expanded
        except TimeoutException:
            return False

    def _filter_is_expanded(self) -> bool:
        """
        Determine if the text filter is expanded.

        :returns: True, if the text filter is expanded - False otherwise.
        """
        return "isExpanded" in self._container.find(wait_timeout=0.5).get_attribute("class")

    def set_filter_text(self, text: str, binding_wait_time: float = 2) -> None:
        """
        Expand the text filter before typing the supplied text into the filter input.

        :param text: The text to type into the filter.
        :param binding_wait_time: How long (in seconds) to wait after typing the supplied text before allowing code to
            continue.

        :raises AssertionError: If unsuccessful in applying the supplied text to the filter.
        :raises TimeoutException: If the icon to expand the filter is not present.
        """
        self.expand_filter()
        super().set_filter_text(text=text, binding_wait_time=binding_wait_time)

    def text_filtering_is_enabled(self) -> bool:
        """
        Determine if text filtering is enabled for the Alarm Table.

        :returns: True, if the icon (magnifying glass) which would expand the text filter is present in the DOM - False
            otherwise.
        """
        try:
            return self._filter_icon.find(wait_timeout=1) is not None
        except TimeoutException:
            return False


class _AlarmTableHeader(Header):
    """The Header of the Alarm Table."""
    pass


class _AlarmTableMenuItem(ComponentPiece):
    """
    Used as both Config modal items in both tables AND Shelve times of the AST
    """
    _MENU_ITEM_LOCATOR = (By.CSS_SELECTOR, 'div.alarmTableMenuItem')

    def __init__(
            self,
            driver: WebDriver,
            text: str,
            description: Optional[str] = None):
        super().__init__(
            locator=(By.CSS_SELECTOR, f'{self._MENU_ITEM_LOCATOR[1]}[data-label="{text}"]'),
            driver=driver,
            parent_locator_list=ComponentModal(driver=driver).locator_list,
            wait_timeout=1,
            description=description)


class _AlarmTableToolbar(ComponentPiece):
    """
    The toolbar of the Alarm Table, where the filtering mechanisms and date range selector reside.
    """
    _PREFILTER_TOGGLE_ICON_LOCATOR = (By.ID, 'preFilterToggle')
    _PREFILTER_MENU_ITEM_LOCATOR = (By.CSS_SELECTOR, 'div.preFilterMenuItem')
    _FILTER_RESULT_COUNT_LOCATOR = (By.CSS_SELECTOR, 'div.toolbarFilterResultsBar')
    _REMOVE_ALL_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'div.ia_alarmTableComponent__toolbar__preFilter__removeAll')
    _POPOVER_OR_MODAL_CLOSE_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'div[class*="CloseIcon"] svg')
    _TEXT_FILTER_ICON_LOCATOR = (By.CSS_SELECTOR, 'div.alarmFilterToggle svg')
    _TEXT_FILTER_CLOSE_ICON_LOCATOR = (By.CSS_SELECTOR, 'div.closeFilterToggle svg')
    _TEXT_FILTER_CONTAINER_LOCATOR = (By.CSS_SELECTOR, 'div.toggleableAlarmFilter')
    _GEAR_LOCATOR = (By.ID, 'configToggle')
    _CONFIG_COLUMN_ITEM_LOCATOR = (By.CSS_SELECTOR, 'div.alarmTableConfigColumnItem')
    _COLUMN_CONFIG_MENU_HEADER_LOCATOR = (By.CSS_SELECTOR, 'div.alarmTableConfigMenu')
    _COLUMN_ITEM_LOCATOR = (By.CSS_SELECTOR, 'div.alarmTableConfigColumnItem')
    _PREFILTER_MENU_LOCATOR = (By.CSS_SELECTOR, "div.alarmPreFilterMenu")
    _PREFILTER_PILLS_LOCATOR = (By.CSS_SELECTOR, "div.alarmPreFilterPill")
    _PRE_FILTER_REMOVE_ICON_LOCATOR = (By.CSS_SELECTOR, 'div.alarmPreFilterPillClose svg')
    _FILTER_RESULTS_LOCATOR = (By.CSS_SELECTOR, 'div.toolbarFilterResultsBar')
    _COUNT_OF_APPLIED_FILTERS_LABEL_LOCATOR = (By.CSS_SELECTOR, 'div.alarmPreFilterCount')

    def __init__(
            self,
            driver: WebDriver,
            parent_locator_list: List[Tuple[By, str]],
            wait_timeout: float = 5,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=(By.CSS_SELECTOR, "div.alarmTableToolbar"),
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        # Non-component locator lists
        self._filter_label_result_count = ComponentPiece(
            locator=self._FILTER_RESULT_COUNT_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._applied_filter_count_label = ComponentPiece(
            locator=self._COUNT_OF_APPLIED_FILTERS_LABEL_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._remove_all_button = ComponentPiece(
            locator=self._REMOVE_ALL_BUTTON_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._prefilter_toggle_icon = ComponentPiece(
            locator=self._PREFILTER_TOGGLE_ICON_LOCATOR,
            driver=self.driver,
            parent_locator_list=parent_locator_list,
            poll_freq=poll_freq)
        self._text_filter_container = ComponentPiece(
            locator=self._TEXT_FILTER_CONTAINER_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._text_filter_icon = ComponentPiece(
            locator=self._TEXT_FILTER_ICON_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._text_filter_close_icon = ComponentPiece(
            locator=self._TEXT_FILTER_CLOSE_ICON_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._column_configuration_icon = ComponentPiece(
            locator=self._GEAR_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._prefilter_pills = ComponentPiece(
            locator=self._PREFILTER_PILLS_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._filtered_results_label = ComponentPiece(
            locator=self._FILTER_RESULTS_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._filter = Filter(driver=driver, parent_locator_list=self.locator_list, poll_freq=poll_freq)
        # These are not children of the table component and instead is a child of the root.
        # So we shouldn't copy the existing locator list
        self._component_modal = ComponentModal(driver=driver)
        self._prefilter_menu_item = ComponentPiece(
            locator=self._PREFILTER_MENU_ITEM_LOCATOR,
            driver=self.driver,
            poll_freq=poll_freq)
        self._column_items = ComponentPiece(locator=self._COLUMN_ITEM_LOCATOR, driver=self.driver, poll_freq=poll_freq)
        self._popover_or_modal_close_icon = ComponentPiece(
            locator=self._POPOVER_OR_MODAL_CLOSE_BUTTON_LOCATOR,
            driver=self.driver,
            parent_locator_list=self._component_modal.locator_list,
            poll_freq=poll_freq)
        self._prefilter_popover_or_modal = ComponentPiece(
            locator=self._PREFILTER_MENU_LOCATOR,
            driver=driver,
            parent_locator_list=self._component_modal.locator_list,
            poll_freq=poll_freq)
        self._config_popover_or_modal_header = ComponentPiece(
            locator=self._COLUMN_CONFIG_MENU_HEADER_LOCATOR,
            driver=driver,
            parent_locator_list=self._component_modal.locator_list,
            poll_freq=poll_freq)
        self._menu_items = {}
        self._menu_item_checkboxes = {}
        self._already_attempted_to_click_icon = False

    def apply_prefilters(
            self, prefilter_list: List[Union[AlarmState, AlarmPriority, AlarmStatusTableAlarmState]]) -> None:
        """
        Set the conditional display of an alarm to require it have at least one of the supplied States or Priorities.

        :param prefilter_list: A list of States and/or Priorities of which any alarm must satisfy at least one
            requirement to be displayed.

        :raises AssertionError: If unsuccessful in applying all supplied States/Priorities. Will also be raised if
            application of all prefilters in list results in all states or priorities being applied, as the requested
            state or priority will not be present as a prefilter.
        """
        prefilter_list_as_strings = [_.value for _ in prefilter_list]
        try:
            self.wait.until(IAec.function_returns_true(
                custom_function=self._apply_prefilters,
                function_args={
                    'prefilter_list_as_strings': prefilter_list_as_strings
                }))
        except TimeoutException:
            # Continue on, and let the assertion raise the issue instead.
            pass
        priority_leading_string = ": "  # technically "Priority: ", but translations will impact this
        applied_state_and_priority_filter_displayed_text = self.get_text_of_applied_prefilters()
        actual_states_and_priorities = []
        for prefilter in applied_state_and_priority_filter_displayed_text:
            actual_states_and_priorities.append(
                prefilter if priority_leading_string not in prefilter else prefilter.split(priority_leading_string)[-1])
        for state_or_priority in prefilter_list_as_strings:
            IAAssert.contains(
                iterable=actual_states_and_priorities,
                expected_value=state_or_priority,
                failure_msg=f"Failed to apply {state_or_priority} as a conditional filter.")

    def apply_show_all_events_prefilter(self) -> None:
        """
        Select the 'Show All' option for the STATES category of filters.

        :raises AssertionError: If unsuccessful in applying the 'Show All' option.
        """
        self.wait.until(IAec.function_returns_true(
            custom_function=self._apply_prefilters,
            function_args={
                'prefilter_list_as_strings': ["Show All"]
            }))
        all_applied_states_and_priorities = self.get_text_of_applied_prefilters()
        for state in [_.value for _ in AlarmState]:
            IAAssert.does_not_contain(
                iterable=all_applied_states_and_priorities,
                expected_value=state,
                failure_msg="Failed to remove any applied Alarm State filtering after selecting 'Show All' for States.")

    def click_prefilter_icon(self) -> None:
        """
        Click the icon which opens the State and Priority conditional prefilter popover/modal.

        :raises TimeoutException: If the icon required to open the State and Priority conditional prefilter
            popover/modal is not present.
        """
        self._prefilter_toggle_icon.find().click()

    def click_remove_all_prefilters_button(self) -> None:
        """
        Click the 'Remove All' button which removes all applied prefilters.

        :raises TimeoutException: If the 'Remove All' button is not present.
        """
        self._remove_all_button.click(wait_timeout=2)

    def column_configuration_icon_is_present(self) -> bool:
        """
        Determine if the gear icon which would open the Column Configuration popover/modal is present.

        :returns: True, if the gear icon is present - False otherwise.
        """
        try:
            return self._column_configuration_icon.find() is not None
        except TimeoutException:
            return False

    def column_configuration_popover_or_modal_is_open(self) -> bool:
        """
        Determine if the popover/modal which is used to configure which columns are displayed in the Alarm Table is
        open.

        :returns: True, if the popover/modal is currently displayed - False otherwise.
        """
        try:
            return self._config_popover_or_modal_header.find(wait_timeout=0.5) is not None
        except TimeoutException:
            return False

    def column_is_present_in_column_configuration_popover(self, column: AlarmTableColumn) -> bool:
        """
        Determine if the supplied Column is displayed in the column configuration popover/modal. Requires the
        popover/modal already be opened.

        :param column: The Alarm Table Column to verify the presence of.

        :raises TimeoutException: If the Column Configuration popover/modal is not open.
        """
        return column.name in [_.text for _ in self._column_items.find_all()]

    def _apply_prefilters(self, prefilter_list_as_strings: List[str]) -> bool:
        """
        Attempt to set the state of supplied labels (menu items) to True, and report back on the success of the entire
        list.

        :param prefilter_list_as_strings: A lost of labels (menu items) as STRINGS, where each label will be set to
            'selected' and applied as a conditional filter.

        :returns: True, if the entire list of labels was set to be included as a filtering condition - False otherwise.
        """
        try:
            for menu_item_label in prefilter_list_as_strings:
                self._set_selection_state_of_menu_item(menu_item_label=menu_item_label, should_be_displayed=True)
            return True
        except TimeoutException:
            return False

    def click_column_configuration_icon(self) -> None:
        """
        Click the icon to expand the Column Configuration popover/modal.

        :raises TimeoutException: If the icon is not present.
        """
        self._column_configuration_icon.scroll_to_element()
        self._column_configuration_icon.click()

    def click_popover_or_modal_close_icon(self) -> None:
        """
        Close any displayed popover or modal.

        :raises StaleElementReferenceException: If after trying twice we were unable to click the 'close' icon of the
            popover/modal.
        """
        try:
            self._popover_or_modal_close_icon.click(wait_timeout=2)
            self._already_attempted_to_click_icon = False  # on success, make sure we reset our check
        except TimeoutException:
            pass  # nothing to close
        except StaleElementReferenceException as sere:
            if not self._already_attempted_to_click_icon:
                self._already_attempted_to_click_icon = True
                self.click_popover_or_modal_close_icon()
            else:
                raise sere

    def click_show_all_for_events(self) -> None:
        """
        Click the 'Show All' option for the EVENT category.

        :raises TimeoutException: If the Prefilter popover/modal is not currently displayed.
        :raises IndexError: If the EVENT category is not present.
        """
        self._get_menu_item(menu_item_label="Show All").find_all()[0].click()

    def click_show_all_for_priorities(self) -> None:
        """
        Click the 'Show All' option for the PRIORITY category.

        :raises TimeoutException: If the Prefilter popover/modal is not currently displayed.
        :raises IndexError: If the PRIORITY category is not present.
        """
        self._get_menu_item(menu_item_label="Show All").find_all()[1].click()

    def collapse_text_filter_if_expanded(self) -> None:
        """
        Collapse the text filter if it is currently expanded. No action is taken if the text filter is not expanded.

        :raises TimeoutException: If the collapse icon within the text filter does not become clickable.
        """
        if self.text_filter_is_expanded():
            self.wait.until(ec.element_to_be_clickable(
                self._text_filter_close_icon.get_full_css_locator())).click()
            self.wait_on_binding(time_to_wait=1)

    def dismiss_prefilter_pill(
            self, prefilter: Union[AlarmState, AlarmPriority, AlarmStatusTableAlarmState]) -> None:
        """
        Remove the supplied Prefilter as a conditional filter if it is applied. No action is taken if the supplied
        Prefilter is not currently applied as a conditional filter.

        :param prefilter: The Alarm State to be removed as a conditional filter.

        :raises TimeoutException: If no Alarm States or Priorities are currently applied as conditional filters.
        """
        prefilters = self._prefilter_pills.find_all()
        for i in range(len(prefilters)):
            if prefilter.value.lower() in prefilters[i].text.lower():
                prefilters[i].find_element(*self._PRE_FILTER_REMOVE_ICON_LOCATOR).click()
                break
        IAAssert.does_not_contain(
            iterable=[prefilter.text.lower() for prefilter in self._prefilter_pills.find_all()],
            expected_value=prefilter.value.lower(),
            failure_msg=f"Failed to remove the {prefilter.value} State as a conditional filter by clicking the "
                        f"associated pill in the Alarm Table.")

    def expand_text_filter_if_collapsed(self) -> None:
        """
        Expand the text filter of the Alarm Table if it is not already expanded. No action is taken if the text filter
        is already expanded.

        :raises AssertionError: If unsuccessful in expanding the text filter of the Alarm Table.
        :raises TimeoutException: If the magnifying glass icon is not present, or does not become clickable.
        """
        if not self.text_filter_is_expanded():
            self.wait.until(ec.element_to_be_clickable(
                self._text_filter_icon.get_full_css_locator()
            )).click()
            try:
                self.wait.until(IAec.function_returns_true(
                    custom_function=self.text_filter_is_expanded,
                    function_args={}
                ))
            except TimeoutException:
                # ignore TimeoutException and raise AssertionError instead.
                pass
            self.wait_on_binding(time_to_wait=1)
        IAAssert.is_true(
            value=self.text_filter_is_expanded(),
            failure_msg="Failed to expand the text filter of the Alarm Table.")

    def filtered_results_are_displayed(self) -> bool:
        """
        Determine if filtering of any type is in place on the Alarm Table.

        :returns: True, if any conditional or text filtering is currently applied to the Alarm Table.
        """
        try:
            return self._filtered_results_label.find(wait_timeout=1) is not None
        except TimeoutException:
            return False

    def get_all_prefilter_options(self) -> List[str]:
        """
        Obtain the text of all available State or Priority conditional prefilters. Requires that the conditional
        prefilter popover/modal which contains States and Priorities is already opened.

        :returns: A list, where each entry in the list is the text of a displayed State or Priority that could be
            applied as a conditional prefilter.

        :raises TimeoutException: If the conditional prefilter popover/modal is not already open.
        """
        try:
            return [_.text for _ in self._prefilter_menu_item.find_all()]
        except StaleElementReferenceException:
            return self.get_all_prefilter_options()

    def get_origin_of_remove_all_prefilters_button(self) -> Point:
        """
        Obtain the location of the upper-left corner of the 'Remove All' button.

        :returns: A two-dimensional point which represents the location of the upper-left corner of the 'Remove All'
            button.

        :raises TimeoutException: If the 'Remove All' button is not present.
        """
        return self._remove_all_button.get_origin()

    def get_text_of_all_columns_in_popover(self) -> List[str]:
        """
        Obtain all columns available for display from within the column configuration popover/modal.

        :returns: A list, where each item is the text of a column which is available for display in the Alarm Table.

        :raises TimeoutException: If the column configuration popover/modal is not already open.
        """
        try:
            return [_.text for _ in self._column_items.find_all()]
        except StaleElementReferenceException:
            return self.get_text_of_all_columns_in_popover()

    def get_text_of_applied_filter_count_label(self) -> str:
        """
        Obtain the text of the label preceding the applied conditional filters, which usually appears as 'FILTERS (X):'
        (after any translations have been applied).

        :returns: The text of the label which describes how many conditional filters are currently applied.

        :raises TimeoutException: If no conditional filters are currently applied.
        """
        return self._applied_filter_count_label.get_text()

    def get_text_of_applied_prefilters(self) -> List[str]:
        """
        Obtain the text of all applied State and Priority conditional filters.

        :returns: A list which contains the text of all applied conditional (State/Priority) filters. An empty list
            implies no prefilters are applied.
        """
        try:
            return [prefilter_pill.text for prefilter_pill in self._prefilter_pills.find_all()]
        except TimeoutException:
            return []

    def get_text_of_remove_all_prefilters_button(self) -> str:
        """
        Obtain the text of the 'Remove All' button (after any translations have been applied).

        :returns: The text in use by the 'Remove All' button.

        :raises TimeoutException: If the 'Remove All' button is not currently in place.
        """
        return self._remove_all_button.find().text

    def get_width_of_remove_all_prefilters_button(self, include_units: bool = False) -> str:
        """
        Obtain the width of the 'Remove All' button, with or without units.

        :param include_units: If True, the returned value will contain units of measurement, otherwise the returned
            value will be only the numeric value.

        :returns: The width of the 'Remove All' button, and potentially units.

        :raises TimeoutException: If the 'Remove All' button is not currently in place.
        """
        return self._remove_all_button.get_computed_width(include_units=include_units)

    def is_displayed(self) -> bool:
        """
        Determine if the Alarm Table is currently displayed.

        :returns: True, if the Alarm Table is currently displayed - False otherwise.
        """
        try:
            return self.find(wait_timeout=0.5).is_displayed()
        except TimeoutException:
            return False

    def prefilter_popover_or_modal_is_displayed(self) -> bool:
        """
        Determine if the State and Priority conditional filter popover/modal is displayed.

        :returns: True, if the State/Priority popover/modal is currently displayed - False otherwise.
        """
        try:
            return self._prefilter_popover_or_modal.find(wait_timeout=0.5).is_displayed()
        except TimeoutException:
            return False

    def prefilter_is_applied(self, prefilter: Union[AlarmState, AlarmPriority]) -> bool:
        """
        Determine if a Prefilter is currently applied as a conditional prefilter.

        :param prefilter: The prefilter to verify as a current conditional prefilter.

        :returns: True, if the supplied Prefilter is currently applied as a conditional filter - False otherwise.
        """
        try:
            return prefilter.value in [_.text for _ in self._prefilter_pills.find_all()]
        except StaleElementReferenceException:
            return self.prefilter_is_applied(
                prefilter=prefilter)
        except TimeoutException:
            return False

    def prefiltering_icon_is_displayed(self) -> bool:
        """
        Determine if the Alarm Table allows for applying States and/or Priorities as conditional prefilters to determine
        the display state of Alarms.

        :returns: True, if the user has access to the icon which would allow for opening the State and Priority
            conditional prefilter popover/modal.
        """
        try:
            return self._prefilter_toggle_icon.find().is_displayed()
        except TimeoutException:
            return False

    def get_count_of_results_matching_text_filter(self) -> int:
        """
        Obtain the count of results the Alarm Table believes match all applied filters.

        :returns: The displayed count of results of the Alarm Table which match all applied filters.

        :raises TimeoutException: If no filtering is applied.
        """
        return int(self.get_text_of_filter_results().split(' result')[0])

    def get_text_of_filter_results(self) -> str:
        """
        Obtain the full text of the filtered results label.

        :returns: The full text of the label which describes the count of filtered results.

        :raises TimeoutException: If no filtering is applied.
        """
        return self._filter_label_result_count.find().text

    def set_display_state_of_known_alarm_columns(
            self,
            list_of_known_alarm_columns: List[AlarmTableColumn],
            should_be_displayed: bool) -> None:
        """
        Open the column configuration popover/modal and set the display state for a list of Alarm Table Columns.

        :param list_of_known_alarm_columns: A list where each entry is an Alarm Table Column.
        :param should_be_displayed: If True, each entry will be set as an active selection within the column
            configuration popover/modal. If False, the supplied columns will be set as inactive.
        """
        if not self.column_configuration_popover_or_modal_is_open():
            self._column_configuration_icon.click()
        try:
            self.wait.until(IAec.function_returns_true(
                custom_function=self._set_selection_state_of_columns,
                function_args={
                    "list_of_known_alarm_columns": list_of_known_alarm_columns,
                    "should_be_displayed": should_be_displayed
                }
            ))
        except TimeoutException:
            # no action taken
            pass
        self.click_popover_or_modal_close_icon()

    def show_all_hidden_columns(self) -> None:
        """
        Request that all available columns be displayed in the Alarm Table.
        """
        if not self.column_configuration_popover_or_modal_is_open():
            self.click_column_configuration_icon()
        # bypass normal menu item handling because this option never has any indication it is active.
        self._get_menu_item(menu_item_label="Show All Hidden Columns").click()
        self.click_popover_or_modal_close_icon()

    def text_filter_is_expanded(self) -> bool:
        """Determine if the text filter of the Alarm Table is currently expanded."""
        return 'isExpanded' in self._text_filter_container.find().get_attribute('class')

    def _set_selection_state_of_columns(
            self,
            list_of_known_alarm_columns: List[AlarmTableColumn],
            should_be_displayed: bool) -> bool:
        """
        Set the selection state for a set of columns. Omitting a column from this list will result in no action on the
        omitted column. Report back if any column had its display state modified. Requires that the column configuration
        popover/modal already be open.

        :param list_of_known_alarm_columns: A list which contains all of the columns you would like to set the state of.
        :param should_be_displayed: Dictates whether the column should be an active selection, making it visible to the
            user.

        :returns: True, if any column had its display state changed - False otherwise.
        """
        did_click = False
        for column_name in [column.name for column in list_of_known_alarm_columns]:
            try:
                checkbox = self._get_column_menu_item_checkbox(
                    menu_item_label=column_name)
                if (self._CHECKBOX_CHECKED not in checkbox.find().get_attribute(
                        "class")) == should_be_displayed:
                    self._get_menu_item(
                        menu_item_label=column_name).click(
                        binding_wait_time=0.5)
                    did_click = True
            except TimeoutException:
                pass  # no checkbox with given name
        return not did_click

    def _set_selection_state_of_menu_item(self, menu_item_label: str, should_be_displayed: bool) -> None:
        """
        Set the selection state of any item in a popover/modal (State, Priority, or Column), except for the
        'Show All Columns' item.

        :param menu_item_label: The text of the item for which we will set the state.
        :param should_be_displayed: If True, we will set the supplied item to be an active selection. If False, we will
            set the itme to be an inactive selection.

        :raises TimeoutException: If no item with the supplied text could be found.
        """
        menu_item = self._get_menu_item(menu_item_label=menu_item_label)
        if ("isActive" in menu_item.find().find_element(
                By.CSS_SELECTOR, "div").get_attribute("class")) != should_be_displayed:
            menu_item.click(binding_wait_time=0.5)

    def _get_menu_item(self, menu_item_label: str) -> _AlarmTableMenuItem:
        """
        Obtain a menu item with the supplied text.

        :param menu_item_label: The text of the menu item.
        """
        menu_item = self._menu_items.get(menu_item_label)
        if not menu_item:
            menu_item = _AlarmTableMenuItem(driver=self.driver, text=menu_item_label)
            self._menu_items[menu_item_label] = menu_item
        return menu_item

    def _get_column_menu_item_checkbox(self, menu_item_label: str) -> ComponentPiece:
        """
        Get the checkbox associated with a menu item.

        :param menu_item_label: The text of the menu item from which you would like the checkbox.

        :returns: The Component Piece which defines the checkbox for a column menu item within the Column Configuration
            popover/modal.
        """
        checkbox = self._menu_item_checkboxes.get(menu_item_label)
        if not checkbox:
            checkbox = ComponentPiece(
                locator=(By.TAG_NAME, 'svg'),
                driver=self.driver,
                parent_locator_list=self._get_menu_item(menu_item_label=menu_item_label).locator_list,
                wait_timeout=1)
            self._menu_item_checkboxes[menu_item_label] = checkbox
        return checkbox
    

class AlarmJournalTable(_AlarmTable):
    """A Perspective Alarm Journal Component."""

    class _AlarmJournalTableDateRangeSelector(CommonDateRangeSelector):
        """The Date Range Selector of an Alarm Journal Table."""
        def __init__(
                self,
                driver: WebDriver,
                parent_locator_list: Optional[List] = None,
                description: Optional[str] = None,
                poll_freq: float = 0.5):
            super().__init__(
                driver=driver,
                parent_locator_list=parent_locator_list,
                description=description,
                poll_freq=poll_freq)

        def get_count_of_events_within_current_range(self) -> int:
            """
            Obtain a count of events which fall within the applied date range (whether Realtime or Historical).

            :returns: The count of Alarm entries which match all applied filters and which fall within the currently
                applied date range.
            """
            msg = self.get_message()
            return 0 if "alarm events" not in msg else int(msg.split(" ")[0])

    class _AlarmJournalTableFooter(ComponentPiece):
        """The footer of the Alarm Journal Table."""
        _FOOTER_CONTAINER_LOCATOR = (By.CSS_SELECTOR, "div.alarmTableFoot")
        _VIEW_INSTANCES_FOR_ALARM_BUTTON_LOCATOR = (By.CSS_SELECTOR, "button.viewInstancesButton.ofAlarmButton")
        _VIEW_INSTANCES_FOR_SOURCE_PATH_BUTTON_LOCATOR = (By.CSS_SELECTOR, "button.viewInstancesButton.ofAlarmButton")

        def __init__(
                self,
                driver: WebDriver,
                parent_locator_list: Optional[List[Tuple[By, str]]] = None,
                wait_timeout: float = 3,
                poll_freq: float = 0.5):
            super().__init__(
                locator=self._FOOTER_CONTAINER_LOCATOR,
                driver=driver,
                parent_locator_list=parent_locator_list,
                wait_timeout=wait_timeout,
                poll_freq=poll_freq)
            self._for_alarm_button = ComponentPiece(
                locator=self._VIEW_INSTANCES_FOR_ALARM_BUTTON_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)
            self._for_source_path_button = ComponentPiece(
                locator=self._VIEW_INSTANCES_FOR_SOURCE_PATH_BUTTON_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)

        def click_view_instances_for_this_alarm(self) -> None:
            """
            Click the 'Alarm' button which allows for a user to view instances of the currently-selected alarm.

            :raises TimeoutException: If the 'Alarm' button is not present. This is likely a result of no alarm being
                selected.
            """
            self._for_alarm_button.click()

        def click_view_instances_for_this_source_path(self) -> None:
            """
            Click the 'Source Path' button which allows for a user to view instances of the currently-selected alarm.

            :raises TimeoutException: If the 'Source Path' button is not present. This is likely a result of no alarm
                being selected.
            """
            self._for_source_path_button.click()

        def footer_is_expanded(self) -> bool:
            """
            Determine if the footer of the Alarm Journal Table is expanded.

            :returns: True, if the panel which contains the 'Alarm' and 'Source Path' buttons is expanded - False
                otherwise.
            """
            return "show" in self.find().get_attribute("class")

    def __init__(
            self,
            locator,
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: int = 5,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            poll_freq=poll_freq)
        self._date_range_selector = self._AlarmJournalTableDateRangeSelector(
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._ajt_footer = self._AlarmJournalTableFooter(
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)

    def apply_button_is_enabled(self) -> bool:
        """
        Determine if the 'Apply' button is enabled within the Date Range Selector.

        :returns: True, if the 'Apply' button is enabled within the Date Range Selector.

        :raises TimeoutException: If the Apply button is not present.
        """
        return self._date_range_selector.apply_button_is_enabled()

    def cancel_changes_to_date_range(self) -> None:
        """
        Click the Cancel button in the Date Range Selector.

        :raises TimeoutException: If the Cancel button is not present.
        """
        self._date_range_selector.cancel_changes()

    def click(self, **kwargs) -> None:
        """
        :raises NotImplementedError: Because there's no reason to blindly click an Alarm Journal Table.
        """
        raise NotImplementedError("Please do not click the Alarm Journal Table.")

    def click_apply_button_in_date_range_selector(self) -> None:
        """
        Click the Apply button within the Date Range Selector.

        :raises TimeoutException: If the Apply button is not present.
        """
        self._date_range_selector.apply_changes()

    def click_clear_in_historical_tab(self) -> None:
        """
        Click the 'Clear' link in the Historical Picker of the Date Range Selector.

        :raises TimeoutException: If the Historical Picker is not present.
        """
        self._date_range_selector.click_clear_in_historical_tab()

    def click_historical_day(self, numeric_day: Union[int, str]) -> None:
        """
        Click the supplied numeric day in the Historical Picker of the Date Range Selector.

        :param numeric_day: The day you would like to click.

        :raises AssertionError: If unsuccessful in clicking the supplied day.
        :raises TimeoutException: If the Historical Picker is not present.
        """
        self._date_range_selector.click_historical_day(numeric_day=numeric_day)

    def click_realtime_or_historical_tab(self, tab: DateRangeSelectorTab) -> None:
        """
        Select either the Realtime or Historical tab within the Date Range Selector.

        :param tab: The tab you would like to click.

        :raises TimeoutException: If the supplied tab is not present.
        """
        self._date_range_selector.select_tab(tab=tab)

    def click_view_instances_for_this_alarm(self) -> None:
        """
        Click the 'Alarm' button which allows for a user to view instances of the currently-selected alarm.

        :raises TimeoutException: If the 'Alarm' button is not present. This is likely a result of no alarm being
            selected.
        """
        self._ajt_footer.click_view_instances_for_this_alarm()

    def click_view_instances_for_this_source_path(self) -> None:
        """
        Click the 'Source Path' button which allows for a user to view instances of the currently-selected alarm.

        :raises TimeoutException: If the 'Source Path' button is not present. This is likely a result of no alarm
            being selected.
        """
        self._ajt_footer.click_view_instances_for_this_source_path()

    def close_date_range_popover(self) -> None:
        """
        Close the Date Range Selector if it is already expanded. Takes no action if the Date Range Selector is not
        expanded.
        """
        self._date_range_selector.close_date_range_modal_or_popover_if_displayed()

    def date_range_selector_toggle_icon_is_present(self) -> bool:
        """
        Determine if the icon used to expand the DateRangeSelector is present.

        :returns: True, if the icon is present - False otherwise.
        """
        return self._date_range_selector.date_range_selector_toggle_icon_is_present()

    def date_range_tab_is_active(self, tab: DateRangeSelectorTab) -> bool:
        """
        Determine if the supplied tab is currently the active tab.

        :param tab: The tab which will have its active status queried.

        :returns: True, if the supplied tab is active - False otherwise.

        :raises TimeoutException: If the Date Range Selector is not present.
        """
        return self._date_range_selector.tab_is_active(tab=tab)

    def day_is_node_of_range(self, numeric_day: Union[int, str]) -> bool:
        """
        Determine if the supplied numeric day is either the start or end day of the current Historical range.

        :param numeric_day: The number of the day to verify as a terminal node of the range.

        :returns: True, if the supplied numeric_day is either the starting or ending day of the current range. False, if
            the numeric_day is simply within the range or not a part of the range at all.

        :raises TimeoutException: If the Historical picker is not present; likely to happen if dealing with the Realtime
            range instead of the Historical range.
        """
        return self._date_range_selector.day_is_node_of_range(numeric_day=numeric_day)

    def day_is_within_historical_range(self, numeric_day: Union[int, str]) -> bool:
        """
        Determine if the supplied day falls anywhere within the current historical range.

        :param numeric_day: The number of the day to check for validity.

        :returns: True, if the supplied numeric day is the starting day, ending day or any day between those two days -
            False otherwise.

        :raises TimeoutException: If the Historical picker is not present; likely to happen if dealing with the Realtime
            range instead of the Historical range.
        """
        return self._date_range_selector.day_is_within_historical_range(numeric_day=numeric_day)

    def get_alarm_event_text(self) -> str:
        """
        Obtain the message related to the Date Range Selector. Currently only used for the Alarm Journal Table.
        Example: 'X alarm events'

        :returns: The message associated with the Date Range Selector, if available.

        :raises TimeoutException: If not using the Alarm Journal Table, or if the Alarm Journal Table currently has
            disabled the toolbar which houses the Date Range Selector.
        """
        return self._date_range_selector.get_message()

    def get_count_of_events_within_current_range(self) -> int:
        """
        Obtain a count of events which fall within the applied date range (whether Realtime or Historical).

        :returns: The count of Alarm entries which match all applied filters and which fall within the currently
            applied date range.
        """
        return self._date_range_selector.get_count_of_events_within_current_range()

    def get_current_range_text(self) -> str:
        """
        Obtain the range message associated with the Date Range Selector. This value describes the applied range.
        Example: 'Last 8 hours', or a breakdown of the date/times used for the Historical range.

        :returns: The range message associated with the Date Range Selector, if available.

        :raises TimeoutException: If the range message is not present.
        """
        return self._date_range_selector.get_range_message()

    def get_historical_range(self) -> HistoricalRange:
        """
        Obtain all pieces of information pertaining to the Historical Range.

        :returns: An object containing information about the currently applied Historical Range - even if the Component
            is using a realtime range.
        """
        return self._date_range_selector.get_historical_range()

    def get_historical_text_picker_range_info_text(self) -> str:
        """
        Obtain the historical range as the formatted dates the user would see.

        :returns: A formatted string representation of the dates currently applied as the Historical Range.
        """
        return self._date_range_selector.get_historical_text_picker_range_info_text()

    def get_list_of_available_months_from_date_range_selector(self) -> List[str]:
        """
        Open the Date Range Selector and obtain a list of months available for selection, before finally closing the
        date range popover/modal.

        :returns: A list of months which a user is able to select within the Date Range Selector.

        :raises TimeoutException: If the icon to open the Date Range Selector is not present.
        """
        try:
            self._date_range_selector.open_date_range_popover_or_modal_if_not_already_displayed()
            self._date_range_selector.select_tab(tab=DateRangeSelectorTab.HISTORICAL)
            return self._date_range_selector.get_list_of_available_months_from_historical_picker()
        finally:
            self._date_range_selector.close_date_range_modal_or_popover_if_displayed()

    def get_selected_start_and_end_days_from_date_range_selector(self) -> List[int]:
        """
        Obtain the currently selected beginning and end days of the Historical range.

        Note: This only returns days of the current calendar month, so ranges which span months will only return
        one day.

        :returns: The beginning and end days of the current Historical range, where the
            first element in the list is the start day and the second element is the end day.

        :raises TimeoutException: If the Historical picker is not present; likely to happen if dealing with the
            Realtime range instead of the Historical range.
        """
        return self._date_range_selector.get_selected_start_and_end_days_from_date_range_selector()

    def get_text_of_range_tabs(self) -> List[str]:
        """
        Obtain the text of the Realtime and Historical tabs, as a user would see them. Useful for verifying
        localization.

        :returns: A list of strings which represent the text displayed in the Realtime and Historical tabs, with
            Realtime as the 0th element, and Historical as the 1th element.

        :raises TimeoutException: If the Date Range Selector is not expanded.
        """
        return self._date_range_selector.get_text_of_tabs()

    def open_date_range_popover(self) -> None:
        """
        Expand the Date Range Selector if it is not already expanded.

        :raises TimeoutException: If the icon used to expand the Date Range Selector is not present.
        """
        self._date_range_selector.open_date_range_popover_or_modal_if_not_already_displayed()

    def select_realtime_unit(self, time_unit: DateRangeSelectorTimeUnit) -> None:
        """
        Select a unit of time from the Realtime range selector.

        :param time_unit: The unit of time to select from the selector.

        :raises AssertionError: If unsuccessful in applying the supplied time unit.
        """
        self._date_range_selector.select_realtime_unit(time_unit=time_unit)

    def set_historical_range(self, historical_range: HistoricalRange, apply: bool = True) -> None:
        """
        Set the historical range and click the Apply button based on additional parameters.

        :param historical_range: The Historical Range object which defines the starting and ending dates to apply.
        :param apply: If True, the supplied historical range will be applied. If False, the supplied Historical Range
            will be cancelled upon completion. If None, no action will be taken after completion, leaving the Date
            Range Selector open.

        :raises AssertionError: If unsuccessful in applying the supplied historical range.
        :raises TimeoutException: If the Apply button or the picker were not present.
        """
        self._date_range_selector.set_historical_range(historical_range=historical_range, apply=apply)

    def set_realtime_numeric_value(self, time_value: int) -> None:
        """
        Set the numeric range to be used with the time unit.

        :param time_value: The scalar amount of time you desire to apply as the Realtime range.

        :raises AssertionError: If unsuccessful in applying the supplied time value.
        """
        self._date_range_selector.set_realtime_range(time_value=time_value)


class AlarmStatusTable(_AlarmTable):
    """A Perspective Alarm Status Table Component."""
    _NOTES_MODAL_LOCATOR = (By.CSS_SELECTOR, '#alarmNotesModal')
    _NOTES_MODAL_ACK_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button.alarmNotesModalOkayButton')
    _NOTES_MODAL_CANCEL_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button.alarmNotesModalCancelButton')
    _NOTES_MODAL_TEXT_AREA_LOCATOR = (By.CSS_SELECTOR, 'div.alarmNotesContainer textarea')
    _NOTES_MODAL_CLOSE_LOCATOR = (By.CSS_SELECTOR, 'div.alarmNotesClose svg')
    _NOTES_MODAL_TITLE_LOCATOR = (By.CSS_SELECTOR, 'div.alarmNotesTitle')
    _SHELVE_TIMES_LOCATOR = (By.CSS_SELECTOR, 'div.shelveTimes div.alarmTableMenuItem')

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 5,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator,
            driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._alarm_table_toolbar = self._AlarmStatusTableToolbar(
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._alarm_table_body = self._AlarmStatusTableBody(
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._alarm_table_footer = self._AlarmStatusTableFooter(
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._alarm_status_table_header = self._AlarmStatusTableHeader(
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        # The following are for the ack modal which are children of the root
        self._notes_modal = ComponentPiece(locator=self._NOTES_MODAL_LOCATOR, driver=self.driver, poll_freq=poll_freq)
        self._notes_modal_ack_button = ComponentPiece(
            locator=self._NOTES_MODAL_ACK_BUTTON_LOCATOR,
            driver=self.driver,
            parent_locator_list=self._notes_modal.locator_list,
            poll_freq=poll_freq)
        self._notes_modal_cancel_button = ComponentPiece(
            driver=driver,
            locator=self._NOTES_MODAL_CANCEL_BUTTON_LOCATOR,
            parent_locator_list=self._notes_modal.locator_list,
            poll_freq=poll_freq)
        self._notes_modal_close = ComponentPiece(
            locator=self._NOTES_MODAL_CLOSE_LOCATOR,
            driver=self.driver,
            parent_locator_list=self._notes_modal.locator_list,
            poll_freq=poll_freq)
        self._notes_modal_text_area = ComponentPiece(
            locator=self._NOTES_MODAL_TEXT_AREA_LOCATOR,
            driver=self.driver,
            parent_locator_list=self._notes_modal.locator_list,
            poll_freq=poll_freq)
        self._notes_modal_title = ComponentPiece(
            locator=self._NOTES_MODAL_TITLE_LOCATOR,
            driver=self.driver,
            parent_locator_list=self._notes_modal.locator_list,
            poll_freq=poll_freq)
        # The Shelve time selector is its own modal too
        self._shelve_times = ComponentPiece(locator=self._SHELVE_TIMES_LOCATOR, driver=self.driver, poll_freq=poll_freq)

    def click(self, wait_timeout=None, binding_wait_time: float = 0) -> None:
        """:raises NotImplementedError: Because the Alarm Status Table should not be blindly clicked."""
        raise NotImplementedError("Please do not blindly click the Alarm Status Table.")

    def acknowledge_button_is_displayed(self) -> bool:
        """
        Determine if the 'Acknowledge' Button is displayed for the selected alarm.

        :returns: True, if the 'Acknowledge' button is displayed - False otherwise.
        """
        return self._alarm_table_footer.acknowledge_button_is_displayed()

    def acknowledge_button_is_enabled(self) -> bool:
        """
        Determine if the 'Acknowledge' button is enabled in the footer of the Alarm Status Table.

        :returns: True, if the 'Acknowledge' button is currently enabled - False otherwise.

        :raises TimeoutException: If the 'Acknowledge' button is not present in the Footer of the Alarm Status
            Table.
        """
        return self._alarm_table_footer.acknowledge_button_is_enabled()

    def apply_prefilters(
            self,
            prefilter_list: List[Union[AlarmStatusTableAlarmState, AlarmPriority]],
            close_modal_after: bool = True) -> None:
        """
        Expand the popover/modal which contains the Alarm States and Priorities for the Alarm Status Table, and then
        apply the supplied States/Priorities to the Alarm table.

        :param prefilter_list: A list of the Alarm States and/or Alarm Priorities you would like to have applied as
            a condition for display of an alarm.
        :param close_modal_after: Dictates whether the popover/modal which contains the states and priorities is
            closed after the selections are made.

        :raises AssertionError: If unsuccessful in applying all supplied States/Priorities.
        :raises TimeoutException: If the icon required to expand the conditional prefilter popover/modal is not present.
        """
        # special requirement of AlarmStatusTableAlarmState due to unique nature of Alarm Status Table prefilters.
        self.open_prefilter_popover()
        self._alarm_table_toolbar.apply_prefilters(
            prefilter_list=prefilter_list)
        if close_modal_after:
            self.close_any_open_popover_or_modal()
        self._alarm_table_toolbar.wait_on_binding(time_to_wait=1)

    def click_shelve_button(self) -> None:
        """
        Click the 'Shelve' button in the Footer of the Alarm Status Table.

        :raises TimeoutException: If the 'Shelve' button is not present, or if unsuccessful in clicking the button.
        """
        return self._alarm_table_footer.click_shelve_button()

    def dismiss_prefilter_pill(self, prefilter: Union[AlarmStatusTableAlarmState, AlarmPriority]) -> None:
        """
        Remove the supplied Prefilter as a conditional filter if it is applied. No action is taken if the supplied
        Prefilter is not currently applied as a conditional filter.

        :param prefilter: The Prefilter to be removed as a conditional filter.

        :raises TimeoutException: If no Alarm States or Priorities are currently applied as conditional filters.
        """
        self._alarm_table_toolbar.dismiss_prefilter_pill(
            prefilter=prefilter)

    def select_shelve_time(self, shelve_time_option_text: str, wait_for_shelve: bool = True) -> None:
        """
        Select a period of time for which to shelve an Alarm.

        :param shelve_time_option_text: The string label of the option to select as the period of time to shelve the
            selected alarm(s).
        :param wait_for_shelve: If True, wait for the animation associated with shelving an Alarm to complete before
            continuing.

        :raises TimeoutException: If the supplied shelve time is not an option, or if the Shelve button has not already
            been clicked.
        """
        self.wait.until(IAec.function_returns_true(
            custom_function=self._select_shelve_time_and_report_success_of_selection,
            function_args={
                "shelve_time": shelve_time_option_text
            }
        ))
        if wait_for_shelve:
            # Waits until the footer is gone
            self._alarm_table_footer.acknowledge_button_is_not_displayed()

    def shelve_time_is_displayed(self, shelve_time_option_text: str) -> bool:
        """
        Determine if the supplied shelve time text is a displayed option in the dropdown.

        :param shelve_time_option_text: The text to search for as an option of the shelve time dropdown.

        :returns: True, if the supplied text is an option of the shelve time dropdown - False otherwise.
        """
        return self._alarm_table_footer.shelve_time_is_displayed(shelve_time=shelve_time_option_text)

    def _select_shelve_time_and_report_success_of_selection(self, shelve_time: str) -> bool:
        """
        Select a shelve time from the dropdown and report on the success of the selection.

        :param shelve_time: The option to select from the shelve time dropdown.

        :returns: True, if the option was successfully selected - False otherwise.
        """
        try:
            self._alarm_table_footer.click_shelve_time(shelve_time=shelve_time)
            return True
        except TimeoutException:
            return False

    def set_row_selection_state_for_first_matching_row(
            self, known_value: str, column_for_value: AlarmTableColumn, should_be_selected: bool) -> None:
        """
        Set the selection state for a row which has a known value in a known column.

        :param known_value: The value known to be in the target row, within the specified column.
        :param column_for_value: The Alarm Table Column known to contain the supplied known value.
        :param should_be_selected: Dictates the selection state to be applied to the row described by the supplied
            value and column.

        :raises TimeoutException: If selection is disabled for the Alarm Status Table, or if no row contains the
            known value in the specified column, or if the specified colum is not present.
        """
        self._alarm_table_body.set_row_selection_state_for_first_matching_row(known_value=known_value,
                                                                              column_for_value=column_for_value,
                                                                              should_be_selected=should_be_selected)

    def set_row_selection_state_for_all_matching_rows(
            self, known_value: str, column_for_value: AlarmTableColumn, should_be_selected: bool) -> None:
        """
        Set the selection state for all rows which have a known value in a known column.

        :param known_value: The value known to be in the target rows, within the specified column.
        :param column_for_value: The Alarm Table Column known to contain the supplied known value.
        :param should_be_selected: Dictates the selection state to be applied to the rows described by the supplied
            value and column.

        :raises TimeoutException: If unsuccessful in applying the requested selection state to all supplied indices.
        """
        self._alarm_table_body.set_row_selection_state_for_all_matching_rows(known_value=known_value,
                                                                             column_for_value=column_for_value,
                                                                             should_be_selected=should_be_selected)

    def get_selection_state_for_rows(self, known_value: str, column_for_value: AlarmTableColumn) -> List[bool]:
        """
        Obtain the selection state of all rows which have a known value within a specified column.

        :param known_value: A value known to be present in the specified column.
        :param column_for_value: The column which contains the supplied value.

        :returns: A list, where each element in the list is a boolean value which represents the selection state of a
            row which had the known value within the specified column.

        :raises TimeoutException: If no rows contain the supplied value in the specified column.
        :raises AssertionError: If no rows contain the supplied value in the specified column.
        """
        return self._alarm_table_body.get_selection_state_for_rows(known_value=known_value,
                                                                   column_for_value=column_for_value)

    def get_count_of_selected_rows(self) -> int:
        """
        Obtain a count of all rows which are currently selected in the Alarm Status Table.

        :returns: A count which represents the number of currently selected rows in the Alarm Status Table.
        """
        return self._alarm_table_body.get_count_of_selected_rows()

    def get_count_of_alarm_with_expected_value(
            self,
            desired_column: AlarmTableColumn,
            desired_column_value_list: Optional[List[str]],
            known_column: AlarmTableColumn,
            known_column_value: str) -> int:
        """
        Obtain a count of all rows which contain a known value in a specific column.

        :param desired_column: The Alarm Table Column you want information from.
        :param desired_column_value_list: Potential values you want to filter for within the desired column.
        :param known_column: The Alarm Table Column you know contains text which will be used to target rows of the
            Alarm Status Table.
        :param known_column_value: The value known to exist in a column. This value is what determines which rows
            will be considered matches.

        :returns: A count of all rows which contain a known value within a known column, and which also (optionally)
            contain a set of values in a second column.
        """
        return len(self._alarm_table_body
                   .get_alarm_column_data_with_known_value(desired_column=desired_column,
                                                           desired_column_value_list=desired_column_value_list,
                                                           known_column=known_column,
                                                           known_column_value=known_column_value))

    def get_alarm_column_data_with_known_value(
            self,
            desired_column: AlarmTableColumn,
            desired_column_value_list: Optional[List[str]],
            known_column: AlarmTableColumn,
            known_column_value: str) -> List[dict]:
        """
        Obtain information about a desired column for all rows which contain a known value in a known column.

        :param desired_column: The Alarm Table Column you want information from.
        :param desired_column_value_list: Potential values you want to filter for within the desired column.
        :param known_column: The Alarm Table Column you know contains text which will be used to target rows of the
            Alarm Status Table.
        :param known_column_value: The value known to exist in a column. This value is what determines which rows
            will be considered matches.
        """
        return self._alarm_table_body\
            .get_alarm_column_data_with_known_value(desired_column=desired_column,
                                                    desired_column_value_list=desired_column_value_list,
                                                    known_column=known_column,
                                                    known_column_value=known_column_value)

    def get_row_count(self) -> int:
        """
        Obtain a count of rows in the Table.

        :returns: A count of rows in the Alarm Status Table.
        """
        return self._alarm_table_body.get_row_count(include_expanded_subviews_in_count=False)  # no subviews in AST

    def get_select_all_checkbox_state(self) -> Optional[bool]:
        """
        Obtain the state of the "select-all" checkbox.

        :returns: True, if checked. False, if un-checked. None, if some number of rows less than the total number
            of rows on the page is currently selected.

        :raises TimeoutException: If the checkbox which drives the selection of all rows is not present.
        """
        return self._alarm_status_table_header.get_select_all_checkbox_state()

    def get_sort_order_number_of_column(self, column: AlarmTableColumn) -> Optional[int]:
        """
        Obtain the numeric sort order of a given Alarm table Column.

        :param column: The Alarm Table Column from which you would like the sort order.

        :returns: The sort order of the Alarm Table Column as a number, or None if no sorting is applied.

        :raises TimeoutException: If the specified Alarm Table Column is not present.
        """
        return self._alarm_status_table_header.get_sort_order_number_of_column(column=column)

    def sort_order_of_column_is_descending(self, column: AlarmTableColumn) -> Optional[bool]:
        """
        Determine if the sort applied to a given Alarm Table Column is in descending order.

        :param column: The Alarm Table Column which will have it sort order checked.

        :returns: True, if the sort applied to the supplied Alarm Table Column is in descending order. False
            if the order is ascending. None if no sorting is applied to the Alarm Table Column.

        :raises TimeoutException: If the specified column has no sorting applied, or if the column is not present.
        """
        try:
            return self._alarm_status_table_header.descending_sort_is_active(column=column)
        except TimeoutException:
            return False

    def click_acknowledge_button_and_report_success_of_click(self) -> bool:
        """
        Click the Acknowledge button and report back the success of the click.

        :returns: True, if the 'Acknowledge' button was successfully clicked - False otherwise.
        """
        return self._alarm_table_footer.click_acknowledge_button_and_report_success_of_click()

    def click_active_alarms_tab(self) -> None:
        """
        Click the ACTIVE tab within the Alarm Status Table. This function will also wait for any transition
        between the tabs to complete.

        :raises AssertionError: If unsuccessful in getting to the ACTIVE tab of the Alarm Status Table.
        """
        return self._alarm_table_toolbar.click_active_alarms_tab()

    def click_shelved_alarms_tab(self, time_to_wait: float = 0.5) -> None:
        """
        Click the SHELVED tab within the Alarm Status Table. This function will also wait for any transition
        between the tabs to complete.

        :raises AssertionError: If unsuccessful in getting to the SHELVED tab of the Alarm Status Table.
        """
        return self._alarm_table_toolbar.click_shelved_alarms_tab(
            transition_wait_time=time_to_wait)

    def active_tab_exists(self) -> bool:
        """
        Determine if the ACTIVE tab is present in the Alarm Status Table.

        :returns: True, if the ACTIVE tab is present - False otherwise.
        """
        return self._alarm_table_toolbar.active_tab_exists()

    def shelved_tab_exists(self) -> bool:
        """
        Determine if the SHELVED tab is present in the Alarm Status Table.

        :returns: True, if the SHELVED tab is present - False otherwise.
        """
        return self._alarm_table_toolbar.shelved_tab_exists()

    def get_count_of_shelved_alarms_from_toolbar(self, expected_count: Optional[int] = None) -> int:
        """
        Obtain a count of shelved alarms from the SHELVED tab of the Alarm Status Table.

        :param expected_count: The count of Alarms you expect to be shelved. If supplied, this function will attempt
            to wait until this value is the actual count before returning a value.

        :returns: The number of Alarms declared as being shelved by the SHELVED tab.

        :raises TimeoutException: If the tabs of the Alarm Status Table are not present.
        :raises IndexError: If the SHELVED tab is not present.
        """
        return self._alarm_table_toolbar.get_count_of_shelved_alarms(
            expected_count=expected_count)

    def get_count_of_active_alarms_from_toolbar(self) -> int:
        """
        Obtain a count of Alarms which match applied filters and which are active.

        :returns: The count of alarms declared by the ACTIVE tab which match all applied PREFILTERS and which are
            active. Text filtering does not affect this count.
        """
        return self._alarm_table_toolbar.get_count_of_active_alarms()

    def get_confirmation_text_of_shelved_alarms(self, expected_shelve_message: str) -> Optional[str]:
        """
        Obtain the message displayed as a confirmation that an alarm has been shelved. Requires that an Alarm have
        been shelved immediately before invocation.

        :param expected_shelve_message: The message you expect to be displayed as a confirmation. This function will
            wait some period of time or until the expected message is displayed before returning the displayed
            message.

        :returns: The confirmation message displayed when a user shelves an alarm, or None. A None value indicates
            the message never took on the expected text.
        """
        return self._alarm_table_footer.get_shelved_alarm_confirmation_message(
            expected_shelve_message=expected_shelve_message)

    def show_all_hidden_columns(self) -> None:
        """
        Request that the Alarm Table display all available columns.
        """
        # unable to perform assertion here because this function is used across the ACTIVE/SHELVED tabs.
        self._alarm_table_toolbar.show_all_hidden_columns()

    def click_unshelve_button(self) -> None:
        """
        Click the 'Unshelve' button available in the Footer of the Alarm Status Table while interacting with alarms
        in the 'Shelved' tab.

        :raises TimeoutException: If the 'Unshelve' button is not present.
        """
        self._alarm_table_footer.click_unshelve_button()

    def set_select_all_checkbox(self, should_be_selected: bool) -> None:
        """
        Set the state of the "select-all" checkbox.

        :param should_be_selected: If True, the checkbox will be set to checked. If False, the checkbox will be set
            to an un-checked state.

        :raises TimeoutException: If the checkbox which drives the selection of all rows is not present.
        :raises AssertionError: If unsuccessful in setting the state of the "select-all" checkbox.
        """
        return self._alarm_status_table_header.set_select_all_checkbox_state(should_be_selected=should_be_selected)

    def notes_modal_is_displayed(self) -> bool:
        """
        Determine if the Acknowledgement Notes modal is displayed.

        :returns: True, if the modal which allows a user to supply acknowledgement notes to an alarm undergoing
            acknowledgement is displayed -False otherwise.
        """
        try:
            return self._notes_modal.find(wait_timeout=3).is_displayed()
        except TimeoutException:
            return False

    def set_acknowledgement_notes(self, notes: str) -> None:
        """
        Set the acknowledgement notes of an alarm undergoing acknowledgement. Requires the Acknowledgement Notes modal
        already be displayed.

        :param notes: The notes to be applied to the alarm.

        :raises TimeoutException: If the Acknowledgement Notes modal is not currently displayed.
        """
        self.wait.until(IAec.function_returns_true(
            custom_function=self._set_acknowledgement_notes,
            function_args={
                'notes': notes
            }
        ))

    def _set_acknowledgement_notes(self, notes: str) -> bool:
        """
        Set the acknowledgement notes of an alarm undergoing acknowledgement. Requires the Acknowledgement Notes modal
        already be displayed.

        :param notes: The notes to be applied to the alarm.

        :returns: True, if successful in identifying the input and sending the text content - False otherwise.
        """
        try:
            text_area = self._notes_modal_text_area.find()
            text_area.clear()
            text_area.send_keys(notes)
            return True
        except StaleElementReferenceException:
            return False

    def click_ack_alarms(self) -> None:
        """
        Click the 'Ack Alarm(s)' button in the bottom right of the Acknowledgement Notes modal.

        :raises TimeoutException: If the 'Ack Alarm(s)' button is not present.
        """
        self._notes_modal_ack_button.click()
        self._alarm_table_footer.acknowledge_button_is_not_displayed()

    def select_all_checkbox_is_enabled(self) -> bool:
        """
        Determine if the "select-all" checkbox of the Alarm Status Table is enabled.

        :returns: True, if the "select-all" checkbox is currently enabled - False otherwise.
        """
        return self._alarm_status_table_header.select_all_checkbox_is_enabled()

    class _AlarmStatusTableToolbar(_AlarmTableToolbar):
        """
        The Toolbar at the top of the Alarm Status Table, unique as it has tabs for ACTIVE and SHELVED alarms.
        """
        _TABS_LOCATOR = (By.CSS_SELECTOR, 'div.toolbarTabContainer>div.tab')
        _ACTIVE_TABS_LOCATOR = (By.CSS_SELECTOR, 'div.toolbarTabContainer>div.tab.active')
        _ALARM_COUNT_LOCATOR = (By.CSS_SELECTOR, 'div.count')

        def __init__(
                self,
                driver: WebDriver,
                parent_locator_list: List[Tuple[By, str]],
                wait_timeout: float = 5,
                poll_freq: float = 0.5):
            super().__init__(
                driver=driver,
                parent_locator_list=parent_locator_list,
                wait_timeout=wait_timeout,
                poll_freq=poll_freq)
            # Non-component locator lists
            self.active_tab = ComponentPiece(
                locator=self._ACTIVE_TABS_LOCATOR,
                driver=self.driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)
            # Note tabs/alarm_count return multiple components. One for each tab.
            # Without an ID we just have to remember to use the right index
            self.tabs = ComponentPiece(
                locator=self._TABS_LOCATOR,
                driver=self.driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)
            self.alarm_count = ComponentPiece(
                locator=self._ALARM_COUNT_LOCATOR,
                driver=self.driver,
                parent_locator_list=self.tabs.locator_list,
                poll_freq=poll_freq)

        def click_active_alarms_tab(self) -> None:
            """
            Click the ACTIVE tab within the Alarm Status Table. This function will also wait for any transition
            between the tabs to complete.

            :raises AssertionError: If unsuccessful in getting to the ACTIVE tab of the Alarm Status Table.
            """
            self.tabs.find_all()[0].click()
            self.tabs.wait_on_binding(time_to_wait=0.5)
            try:
                self.wait.until(IAec.function_returns_true(
                    custom_function=self._tab_is_active,
                    function_args={
                        'tab': 'ACTIVE'
                    }
                ))
            except TimeoutException:
                raise AssertionError("Failed to display the ACTIVE tab of the Alarm Status Table.")

        def click_shelved_alarms_tab(self, transition_wait_time: float = 0.5) -> None:
            """
            Click the ACTIVE tab within the Alarm Status Table. This function will also wait for any transition
            between the tabs to complete.

            :param transition_wait_time: The amount of time (in seconds) to wait after clicking the SHELVED tab before
                we attempt to verify it has become the active tab in use.

            :raises AssertionError: If unsuccessful in getting to the ACTIVE tab of the Alarm Status Table.
            """
            self.tabs.find_all()[1].click()
            self.tabs.wait_on_binding(time_to_wait=transition_wait_time)
            try:
                self.wait.until(IAec.function_returns_true(
                    custom_function=self._tab_is_active,
                    function_args={
                        'tab': 'SHELVED'
                    }
                ))
            except TimeoutException:
                raise AssertionError("Failed to display the SHELVED tab of the Alarm Status Table.")

        def active_tab_exists(self) -> bool:
            """
            Determine if the ACTIVE tab is present in the Alarm Status Table.

            :returns: True, if the ACTIVE tab is present - False otherwise.
            """
            return 'ACTIVE' in self.tabs.find_all()[0].text

        def shelved_tab_exists(self) -> bool:
            """
            Determine if the SHELVED tab is present in the Alarm Status Table.

            :returns: True, if the SHELVED tab is present - False otherwise.
            """
            return 'SHELVED' in self.tabs.find_all()[1].text

        def get_count_of_shelved_alarms(
                self, expected_count: Optional[int] = None, time_to_wait: float = 3) -> int:
            """
            Obtain a count of shelved alarms.

            :param expected_count: The count of Alarms you expect to be shelved. If supplied, this function will attempt
                to wait until this value is the actual count before returning a value.
            :param time_to_wait: The amount of time (in seconds) you are willing to wait for the count of shelved alarms
                to match your supplied value.

            :returns: The number of Alarms declared as being shelved by the SHELVED tab.

            :raises TimeoutException: If the tabs of the Alarm Status Table are not present.
            :raises IndexError: If the SHELVED tab is not present.
            """
            if expected_count is not None:
                try:
                    WebDriverWait(driver=self.driver, timeout=time_to_wait).until(IAec.function_returns_true(
                        custom_function=self._shelved_alarm_count_matches_expectation,
                        function_args={'expected_count': expected_count}))
                    return expected_count
                except TimeoutException:
                    return self._get_count_of_shelved_alarms()
            else:
                return self._get_count_of_shelved_alarms()

        def _shelved_alarm_count_matches_expectation(self, expected_count: int) -> bool:
            """Determine if the displayed count of shelved alarms matches some expected value."""
            return self._get_count_of_shelved_alarms() == expected_count

        def _tab_is_active(self, tab: str) -> bool:
            """
            Determine if a tab is the current active tab.

            :param tab: The case-insensitive tab to verify as the currently active tab ('active', or 'shelved').

            :returns: True, if the supplied tab is currently the active tab - False otherwise.

            :raises TimeoutException: If the tabs of the Alarm Status Table are not present.
            """
            try:
                return tab.upper() in self.active_tab.find().text
            except StaleElementReferenceException:
                return self._tab_is_active(tab=tab)

        def _get_count_of_shelved_alarms(self) -> int:
            """Obtain a count of Alarms declared as shelved by the SHELVED tab."""
            return int(self.alarm_count.find_all()[1].text)

        def get_count_of_active_alarms(self) -> int:
            """
            Obtain a count of Alarms which match applied filters and which are active.

            :returns: The count of alarms declared by the ACTIVE tab which match all applied PREFILTERS and which are
                active. Text filtering does not affect this count.
            """
            return int(self.alarm_count.find_all()[0].text)

    class _AlarmStatusTableFooter(ComponentPiece):
        """
        The Footer of the Alarm Status Table, where the buttons for acknowledging and/or Shelving alarms reside.
        """
        _ACKNOWLEDGE_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button.ackAlarmsButton')
        _UNSHELVE_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button.unshelveAlarmsButton')
        _SHELVE_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button.shelveAlarmsButton')
        _SHELVE_CONFIRMATION_MESSAGE_LOCATOR = (By.CSS_SELECTOR, "div.text")

        def __init__(
                self,
                driver: WebDriver,
                parent_locator_list: List[Tuple[By, str]],
                wait_timeout: float = 5,
                poll_freq: float = 0.5):
            super().__init__(
                locator=(By.CSS_SELECTOR, "div.alarmTableFoot"),
                driver=driver,
                parent_locator_list=parent_locator_list,
                wait_timeout=wait_timeout,
                poll_freq=poll_freq)
            # Non-component locator lists
            self.acknowledge_button = ComponentPiece(
                locator=self._ACKNOWLEDGE_BUTTON_LOCATOR,
                driver=self.driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)
            self.unshelve_button = ComponentPiece(
                locator=self._UNSHELVE_BUTTON_LOCATOR,
                driver=self.driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)
            self.shelve_button = ComponentPiece(
                locator=self._SHELVE_BUTTON_LOCATOR,
                driver=self.driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)
            self._shelve_time_coll = {}
            self.shelve_confirmation_message = ComponentPiece(
                locator=self._SHELVE_CONFIRMATION_MESSAGE_LOCATOR,
                driver=self.driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)

        def acknowledge_button_is_displayed(self) -> bool:
            """
            Determine if the Acknowledge button is displayed in the Footer of the Alarm Status Table. This function
            will wait a short period of time until the 'Acknowledge' button is displayed before returning.

            :returns: True, if the 'Acknowledge' button is displayed - False otherwise.
            """
            try:
                self.wait.until(IAec.function_returns_true(
                    custom_function=self._button_displayed,
                    function_args={
                        "local_element_object": self.acknowledge_button
                    }
                ))
                return True
            except TimeoutException:
                return False

        def acknowledge_button_is_not_displayed(self) -> bool:
            """
            Determine if the Acknowledge button is NOT displayed in the Footer of the Alarm Status Table. This function
            will wait a short period of time until the 'Acknowledge' button is no longer displayed before returning.

            :returns: True, if the 'Acknowledge' button is NOT displayed - False otherwise.
            """
            try:
                self.wait.until(IAec.function_returns_false(
                    custom_function=self._button_displayed,
                    function_args={
                        "local_element_object": self.acknowledge_button
                    }
                ))
                return True
            except TimeoutException:
                return False

        @staticmethod
        def _button_displayed(local_element_object: ComponentPiece) -> bool:
            """
            Determine the display state of a button (ComponentPiece).

            :param local_element_object: The ComponentPiece which defines the button to check.

            :returns: True, if the supplied ComponentPiece is displayed - False otherwise.
            """
            try:
                return local_element_object.find().is_displayed()
            except TimeoutException:
                return False

        def acknowledge_button_is_enabled(self) -> bool:
            """
            Determine if the 'Acknowledge' button is enabled.

            :returns: True, if the 'Acknowledge' button is currently enabled - False otherwise.

            :raises TimeoutException: If the 'Acknowledge' button is not present in the Footer of the Alarm Status
                Table.
            """
            return self.acknowledge_button.find().is_enabled()

        def click_acknowledge_button_and_report_success_of_click(self) -> bool:
            """
            Click the Acknowledge button and report back the success of the click.

            :returns: True, if the 'Acknowledge' button was successfully clicked - False otherwise.
            """
            if self.acknowledge_button_is_displayed():
                self.acknowledge_button.find().click()
                return True
            else:
                return False

        def click_shelve_button(self) -> None:
            """
            Click the 'Shelve' button in the Footer of the Alarm Status Table.

            :raises TimeoutException: If the 'Shelve' button is not present, or if unsuccessful in clicking the button.
            """
            self.wait.until(IAec.function_returns_true(
                custom_function=self._click_shelve_button_and_report_success_of_click,
                function_args={}
            ))

        def click_shelve_time(self, shelve_time: str) -> None:
            """
            Select an amount of time to shelve an alarm. Requires the 'Shelve' button have already been clicked.

            :param shelve_time: The option available within the dropdown opened on click of the 'Shelve' button which
                describes how long you would like to shelve the Alarm for.

            :raises TimeoutException: If the supplied shelve time is not present, or if the dropdown containing shelve
                time options is not present. This is most likely to occur if the 'Shelve' button was not clicked
                beforehand.
            """
            self._get_shelve_time(shelve_time=shelve_time).click()

        def click_unshelve_button(self) -> None:
            """
            Click the 'Unshelve' button available in the Footer of the Alarm Status Table while interacting with alarms
            in the 'Shelved' tab.

            :raises TimeoutException: If the 'Unshelve' button is not present.
            """
            self.wait_on_binding(time_to_wait=1)  # wait on the animation of the button
            self.wait.until(IAec.function_returns_true(
                custom_function=self._click_unshelve_button_and_report_success_of_click,
                function_args={}
            ))

        def get_shelved_alarm_confirmation_message(self, expected_shelve_message: str) -> Optional[str]:
            """
            Obtain the message displayed as a confirmation that an alarm has been shelved. Requires that an Alarm have
            been shelved immediately before invocation.

            :param expected_shelve_message: The message you expect to be displayed as a confirmation. This function will
                wait some period of time or until the expected message is displayed before returning the displayed
                message.

            :returns: The confirmation message displayed when a user shelves an alarm, or None. A None value indicates
                the message never took on the expected text.
            """
            try:
                self.wait.until(
                    IAec.function_returns_true(
                        custom_function=self._alarm_confirmation_message_has_expected_text,
                        function_args={
                            "expected_shelve_message": expected_shelve_message
                        }
                    ))
                return expected_shelve_message  # don't re-query, just return the matched text
            except TimeoutException:
                # comparison never became an exact match
                return None

        def _alarm_confirmation_message_has_expected_text(self, expected_shelve_message: str) -> bool:
            """
            Determine if the displayed confirmation message is an exact match to the supplied expected text. We are
            unable to return the exact text because the displayed text can at times be an empty string.

            :param expected_shelve_message: The message you expect to be displayed as the confirmation message.

            :returns: True, if the supplied expected text is an exact match to what is displayed - False if there is a
                discrepancy, or if the confirmation message has not yet appeared.
            """
            try:
                return self.shelve_confirmation_message.find(wait_timeout=0).text == str(expected_shelve_message)
            except TimeoutException:
                return False

        def shelve_time_is_displayed(self, shelve_time: str) -> bool:
            """
            Determine if the available periods to shelve an alarm are displayed.

            :param shelve_time: We will verify the presence of this string option.

            :returns: True, if the periods of time to shelve an Alarm are displayed - False otherwise.
            """
            try:
                return self._get_shelve_time(shelve_time=shelve_time).find().is_displayed()
            except TimeoutException:
                return False

        def _click_shelve_button_and_report_success_of_click(self) -> bool:
            """
            Wait for the 'Shelve' button to become clickable before then clicking the button.

            :returns: True, if the click was successful - False otherwise.
            """
            try:
                self.shelve_button.find(wait_timeout=0.5).click()
                return True
            except ElementNotInteractableException:
                return False

        def _click_unshelve_button_and_report_success_of_click(self) -> bool:
            """
            Wait for the 'Unshelve' button to become clickable before then clicking the button.

            :returns: True, if the click was successful - False otherwise.
            """
            try:
                self.unshelve_button.find(wait_timeout=0.5).click()
                return True
            except ElementNotInteractableException:
                return False
            except TimeoutException:
                return False

        def _get_shelve_time(self, shelve_time: str) -> ComponentPiece:
            """
            Obtain the ComponentPiece which defines an available period of time to shelve an Alarm.

            :param shelve_time: The text of the shelve time option this Component Piece will define.

            :returns: A ComponentPiece which may be used to click a period of time to shelve an alarm.
            """
            shelve_time = str(shelve_time)
            item = self._shelve_time_coll.get(shelve_time)
            if not item:
                item = _AlarmTableMenuItem(driver=self.driver, text=shelve_time)
                self._shelve_time_coll[shelve_time] = item
            return item

    class _AlarmStatusTableBody(_AlarmTableBody):
        """
        The Body of the Alarm Status Table, unique in that the Alarm Status Table actually has a column designated to
        allow for selection of rows.
        """

        def __init__(
                self,
                driver: WebDriver,
                parent_locator_list: List[Tuple[By, str]],
                wait_timeout: int = 5,
                poll_freq: float = 0.5):
            super().__init__(
                driver=driver,
                parent_locator_list=parent_locator_list,
                wait_timeout=wait_timeout,
                poll_freq=poll_freq)
            self._table_cells = ComponentPiece(
                locator=(By.CSS_SELECTOR, 'div.tc.ia_table__cell'),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)
            self._cell_by_columns_objects_dict = {}

        def set_row_selection_state_for_first_matching_row(
                self, known_value: str, column_for_value: AlarmTableColumn, should_be_selected: bool) -> None:
            """
            Set the selection state for a row which has a known value in a known column.

            :param known_value: The value known to be in the target row, within the specified column.
            :param column_for_value: The Alarm Table Column known to contain the supplied known value.
            :param should_be_selected: Dictates the selection state to be applied to the row described by the supplied
                value and column.

            :raises TimeoutException: If selection is disabled for the Alarm Status Table, or if no row contains the
                known value in the specified column, or if the specified colum is not present.
            """
            # Shouldn't have to worry about SERE here because there are no interactions
            for cell in self._get_cell_object_by_column_object(
                    alarm_table_column=column_for_value).find_all():
                if cell.text == known_value:
                    self.wait.until(IAec.function_returns_true(
                        custom_function=self._set_selection_state_for_rows,
                        function_args={
                            'indices': [int(cell.get_attribute(self._ROW_INDEX_ATTRIBUTE))],
                            'should_be_selected': should_be_selected
                        }
                    ))
                    break

        def set_row_selection_state_for_all_matching_rows(
                self, known_value: str, column_for_value: AlarmTableColumn, should_be_selected: bool) -> None:
            """
            Set the selection state for all rows which have a known value in a known column.

            :param known_value: The value known to be in the target rows, within the specified column.
            :param column_for_value: The Alarm Table Column known to contain the supplied known value.
            :param should_be_selected: Dictates the selection state to be applied to the rows described by the supplied
                value and column.

            :raises TimeoutException: If unsuccessful in applying the requested selection state to all supplied indices.
            """
            indices = []
            for cell in self._get_cell_object_by_column_object(
                    alarm_table_column=column_for_value).find_all():
                if cell.text == known_value:
                    indices.append(cell.get_attribute(self._ROW_INDEX_ATTRIBUTE))
            self.wait.until(IAec.function_returns_true(
                custom_function=self._set_selection_state_for_rows,
                function_args={
                    'indices': indices,
                    'should_be_selected': should_be_selected
                }
            ))

        def _set_selection_state_for_rows(self, indices: List[int], should_be_selected: bool) -> bool:
            """
            Set the uniform selection state for multiple rows based on their indices.

            :param indices: A list of zero-based indices which will have their selection state set.
            :param should_be_selected: Specifies the active state the checkbox for each row should reflect.

            :returns: True, if any click event occurs for any of the supplied rows - False if no action is taken.
            """
            try:
                did_click = False
                for row in self._rows.find_all():
                    if int(row.get_attribute(self._ROW_INDEX_ATTRIBUTE)) in indices:
                        checkbox_svg_element = row.find_element(*self._CHECKBOX_LOCATOR)
                        if (self._CHECKBOX_CHECKED in checkbox_svg_element.get_attribute('class')) \
                                != should_be_selected:
                            # Click the row instead of the checkbox because of the dock handler
                            IASelenium(self.driver).scroll_to_element(row, align_to_top=False).click()
                            did_click = True
                return not did_click
            except StaleElementReferenceException:
                return False

        def _get_cell_object_by_column_object(self, alarm_table_column: AlarmTableColumn) -> ComponentPiece:
            """
            Obtain a ComponentPiece which defines all cells of the DOM which reside within the supplied Alarm Table
            Column.

            :param alarm_table_column: The Alarm Table Column within which the desired cell resides.

            :returns: A ComponentPiece which defines all cells within the specified column.
            """
            column_id = alarm_table_column.data_column_id
            cell_object = self._cell_by_columns_objects_dict.get(column_id)
            if not cell_object:
                cell_object = ComponentPiece(
                    locator=(By.CSS_SELECTOR, f'div.tc[data-column-id="{column_id}"]'),
                    driver=self.driver,
                    parent_locator_list=self.locator_list,
                    poll_freq=self.poll_freq)
                self._cell_by_columns_objects_dict[column_id] = cell_object
            return cell_object

        def get_count_of_selected_rows(self) -> int:
            """
            Obtain a count of all rows which are currently selected in the Alarm Status Table.

            :returns: A count which represents the number of currently selected rows in the Alarm Status Table.
            """
            try:
                return len(self._selected_rows.find_all(wait_timeout=0.5))
            except TimeoutException:
                return 0

        # Until IGN-5222 is completed, we will have to assume the table is unchanged between known/desired queries
        def get_alarm_column_data_with_known_value(
                self,
                desired_column: AlarmTableColumn,
                desired_column_value_list: Optional[List[str]],
                known_column: AlarmTableColumn,
                known_column_value: str) -> List[dict]:
            """
            Obtain information about a desired column for all rows which contain a known value in a known column.

            :param desired_column: The Alarm Table Column you want information from.
            :param desired_column_value_list: Potential values you want to filter for within the desired column.
            :param known_column: The Alarm Table Column you know contains text which will be used to target rows of the
                Alarm Status Table.
            :param known_column_value: The value known to exist in a column. This value is what determines which rows
                will be considered matches.
            """
            local_known_cells_object = self._get_cell_object_by_column_object(known_column)
            local_desired_cells_object = self._get_cell_object_by_column_object(desired_column)
            values = []
            try:
                known_cell_elements = local_known_cells_object.find_all(wait_timeout=3)
            except TimeoutException:
                known_cell_elements = []
            try:
                desired_cell_elements = local_desired_cells_object.find_all(wait_timeout=3)
            except TimeoutException:
                desired_cell_elements = []
            for index in range(len(known_cell_elements)):
                if known_cell_elements[index].text == known_column_value and \
                        (desired_column_value_list is None or
                         desired_cell_elements[index].text in desired_column_value_list):
                    values.append(
                        {
                            known_column.data_column_id: known_cell_elements[index].text,
                            desired_column.data_column_id: desired_cell_elements[index].text,
                            self._ROW_INDEX_ATTRIBUTE: desired_cell_elements[index].get_attribute(
                                self._ROW_INDEX_ATTRIBUTE)
                        })
            return values

    class _AlarmStatusTableHeader(_AlarmTableHeader):
        """
        The header of the Alarm Status Table, unique in that it contains a checkbox to drive the selection state of all
        displayed rows.
        """
        _SELECT_ALL_CHECKBOX_LOCATOR = (By.CSS_SELECTOR, 'div.thc[data-column-id="select"]')

        def __init__(self, driver: WebDriver, parent_locator_list: List[Tuple[By, str]], poll_freq: float = 0.5):
            super().__init__(
                driver=driver,
                parent_locator_list=parent_locator_list,
                wait_timeout=1,
                poll_freq=poll_freq)
            self._select_all_checkbox = CommonCheckbox(
                locator=self._SELECT_ALL_CHECKBOX_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                wait_timeout=1,
                poll_freq=poll_freq)

        def get_select_all_checkbox_state(self) -> Optional[bool]:
            """
            Obtain the state of the "select-all" checkbox.

            :returns: True, if checked. False, if un-checked. None, if some number of rows less than the total number
                of rows on the page is currently selected.

            :raises TimeoutException: If the checkbox which drives the selection of all rows is not present.
            """
            return self._select_all_checkbox.is_selected()

        def get_sort_order_number_of_column(self, column: AlarmTableColumn) -> Optional[int]:
            """
            Obtain the numeric sort order of a given Alarm table Column.

            :param column: The Alarm Table Column from which you would like the sort order.

            :returns: The sort order of the Alarm Table Column as a number, or None if no sorting is applied.

            :raises TimeoutException: If the specified Alarm Table Column is not present.
            """
            return super().get_sort_order_number_of_column(column_id=column.data_column_id)

        def set_select_all_checkbox_state(self, should_be_selected: bool) -> None:
            """
            Set the state of the "select-all" checkbox.

            :param should_be_selected: If True, the checkbox will be set to checked. If False, the checkbox will be set
                to an un-checked state.

            :raises TimeoutException: If the checkbox which drives the selection of all rows is not present.
            :raises AssertionError: If unsuccessful in setting the state of the "select-all" checkbox.
            """
            self._select_all_checkbox.scroll_to_element(align_to_top=True)
            self._select_all_checkbox.set_state(should_be_selected=should_be_selected, binding_wait_time=0.5)
            IAAssert.is_equal_to(
                actual_value=self.get_select_all_checkbox_state(),
                expected_value=should_be_selected,
                failure_msg="Failed to set the state of the 'select-all' checkbox of the Alarm Status Table.")

        def select_all_checkbox_is_enabled(self) -> bool:
            """
            Determine if the "select-all" checkbox of the Alarm Status Table is enabled.

            :returns: True, if the "select-all" checkbox is currently enabled - False otherwise.
            """
            return self._select_all_checkbox.is_enabled()

        def descending_sort_is_active(self, column: AlarmTableColumn) -> Optional[bool]:
            """
            Determine if the sort applied to a given Alarm Table Column is in descending order.

            :param column: The Alarm Table Column which will have it sort order checked.

            :returns: True, if the sort applied to the supplied Alarm Table Column is in descending order. False
                if the order is ascending. None if no sorting is applied to the Alarm Table Column.

            :raises TimeoutException: If the specified column has no sorting applied, or if the column is not present.
            """
            return super().descending_sort_is_active(column_id=column.data_column_id)
