from enum import Enum
from typing import List, Optional, Tuple, Union

from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException, \
    ElementClickInterceptedException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece, BasicPerspectiveComponent
from Components.Common.TextInput import CommonTextInput
from Components.PerspectiveComponents.Common.DateRangeSelector import HistoricalRange
from Components.PerspectiveComponents.Common.DateTimePicker import PerspectiveDate
from Components.PerspectiveComponents.Common.Icon import CommonIcon
from Components.PerspectiveComponents.Common.Table import Table as CommonTable
from Components.PerspectiveComponents.Common.TablePieces.Body import Body
from Components.PerspectiveComponents.Common.TablePieces.Filter import Filter
from Components.PerspectiveComponents.Common.TablePieces.HeaderAndFooter import Header, FilterModal, Footer
from Components.PerspectiveComponents.Common.TablePieces.Pager import Pager
from Helpers.CSSEnumerations import CSS
from Helpers.IAAssert import IAAssert
from Helpers.IASelenium import IASelenium
from Helpers.Point import Point


class ColumnConfigurations:
    """Enums relating to ways a column can be configured/rendered, and also runtime settings like column filtering."""
    class Render(Enum):
        """Available settings for how a column may be rendered."""
        AUTO = "auto"
        NUMBER = "number"
        DATE = "date"
        BOOLEAN = "boolean"
        STRING = "string"
        VIEW = "view"

    class Filter:
        """Column filtering settings, including conditions and filter icon visibility"""
        class Condition(Enum):
            """
            This is a complete collection of conditions, but not all conditions are applicable based on the column type.
            """
            BETWEEN = "between"  # number, NOT date
            BETWEEN_DATES = "between dates"
            BETWEEN_DATE_TIMES = "between date times"
            CONTAINS = "contains"
            DATE_EQUALS = "date equals"
            DATE_TIME_EQUALS = "date time equals"
            EARLIER_THAN_DATE = "earlier than date"
            EARLIER_THAN_DATE_TIME = "earlier than date time"
            ENDS_WITH = "ends with"  # string
            EQUALS = "equals"  # string or number, NOT date
            FALSE = "false"
            GREATER_THAN = "greater than"
            GREATER_THAN_OR_EQUAL_TO = "greater than or equal to"
            LATER_THAN_DATE = "later than date"
            LATER_THAN_DATE_TIME = "later than date time"
            LESS_THAN = "less than"
            LESS_THAN_OR_EQUAL_TO = "less than or equal to"
            STARTS_WITH = "starts with"  # string
            TRUE = "true"

        class Visible(Enum):
            """Settings for specifying the appearance of the column filter icon in the header."""
            ALWAYS = "always"
            ON_HOVER = "on-hover"
            NEVER = "never"


class _TableBody(Body):
    _ROW_GROUP_LOCATOR = (By.CSS_SELECTOR, "div.tr-group")
    _ROW_LOCATOR = (By.CSS_SELECTOR, "div:not(.subview).tr")  # Not compatible with Workstation until JXBrowser upgrade
    _CELL_LOCATOR = (By.CSS_SELECTOR, "div.tc")
    _SELECTED_CELL_LOCATOR = (By.CSS_SELECTOR, "div.t-selected")
    _ROOT_SELECTION_LOCATOR = (By.CSS_SELECTOR, f"{_SELECTED_CELL_LOCATOR}.root-selected")
    _COPY_OPTION_LOCATOR = (By.CSS_SELECTOR, 'div.copy')
    _SUBVIEW_ARROW_CSS = 'div.tc-expand[data-column-id="expandSubview"] div.expand-subview'
    _EMPTY_MESSAGE_LOCATOR = (By.CSS_SELECTOR, '.empty-message')
    _EMPTY_MESSAGE_ICON_LOCATOR = (By.CSS_SELECTOR, '.empty-icon svg')

    def __init__(self, driver: WebDriver, parent_locator_list: Optional[List] = None, poll_freq: float = 0.5):
        super().__init__(driver=driver, parent_locator_list=parent_locator_list, poll_freq=poll_freq)
        self._copy_option = ComponentPiece(
            locator=self._COPY_OPTION_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._empty_message = ComponentPiece(
            locator=self._EMPTY_MESSAGE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=0.5,
            poll_freq=poll_freq)
        self._empty_icon = CommonIcon(
            locator=self._EMPTY_MESSAGE_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=0.5,
            poll_freq=poll_freq)

    def cell_is_root_selection(self, row_index: int, column_index: int) -> bool:
        """
        Determine if the cell of a Table is the root of the current selection.

        :param row_index: The zero-based index of the row we will check.
        :param column_index: The zero-based index of the column we will check.

        :returns: True, if the resultant cell is the root of the current selection of the Table.

        :raises TimeoutException: If the supplied row and column indices are invalid.
        """
        _locator = (By.CSS_SELECTOR, f'{self._ROW_LOCATOR}[data-row-index="{row_index}"] '
                                     f'{self._CELL_LOCATOR}[data-column-index="{column_index}"]')
        try:
            return ComponentPiece(
                locator=_locator,
                driver=self.driver,
                parent_locator_list=self.locator_list,
                poll_freq=self.poll_freq).find().find_element(*self._ROOT_SELECTION_LOCATOR) is not None
        except StaleElementReferenceException:
            return self.cell_is_root_selection(row_index=row_index, column_index=column_index)
        except NoSuchElementException:
            return False

    def cell_is_selected(self, row_index: int, column_index: int) -> bool:
        """
        Determine if a specified cell is currently part of the active selection of the Table.

        :param row_index: The zero-based index of the row we will check.
        :param column_index: The zero-based index of the column we will check.

        :returns: True, if the resultant cell is part of the current selection of the Table.

        :raises TimeoutException: If the supplied row and column indices are invalid.
        """
        _locator = (By.CSS_SELECTOR, f'{self.__get_row_css_by_row_index(row_index=row_index)} '
                                     f'{self.__get_column_css_by_index(column_index=column_index)}')
        try:
            return ComponentPiece(
                locator=_locator,
                driver=self.driver,
                parent_locator_list=self.locator_list,
                poll_freq=self.poll_freq).find().find_element(*self._SELECTED_CELL_LOCATOR) is not None
        except StaleElementReferenceException:
            return self.cell_is_root_selection(row_index=row_index, column_index=column_index)
        except NoSuchElementException:
            return False

    def click_copy_option(self) -> None:
        """
        Click the "Copy" option of the displayed context menu. Note: the context menu the copy option belongs to must be
        triggered/displayed before invoking this function.

        :raises TimeoutException: If the context menu which contains the copy option is not present.
        """
        self._copy_option.click(wait_timeout=1)

    def collapse_subview_by_row_index(self, row_index: int) -> None:
        """
        Collapse an expanded subview. Takes no action if the subview is already collapsed.

        :param row_index: The zero-based index of the row which might have an expanded subview.

        :raises TimeoutException: if no row exists with the supplied index.
        """
        if self.subview_is_expanded(row_index=row_index):
            locator = (By.CSS_SELECTOR, self.__get_subview_css_by_row_index(row_index=row_index))
            subview_arrow = ComponentPiece(locator=locator, driver=self.driver, parent_locator_list=self.locator_list)
            subview_arrow.click(binding_wait_time=0.5)

    def contains_subviews(self) -> bool:
        """
        Determine if the Table contains subviews. This function does not reflect the current display state of subviews
        - only their presence.

        :returns: True, if the Table contains Subviews - False otherwise.
        """
        try:
            return ComponentPiece(
                locator=(By.CSS_SELECTOR, self.__get_subview_css_by_row_index(row_index=0)),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                poll_freq=self.poll_freq).find() is not None
        except TimeoutException:
            return False

    def copy_option_is_displayed(self) -> bool:
        """
        Determine if the "Copy" option is currently displayed in a context menu of the Table.

        :returns: True, if the "Copy" option is currently displayed in a context menu - False otherwise.
        """
        try:
            return self._copy_option.find() is not None
        except TimeoutException:
            return False

    def copy_option_is_enabled(self) -> bool:
        """
        Determine if the "Copy" option of the context menu is currently enabled.

        :returns: True, if the "Copy" option of the Table's context menu is currently enabled - False otherwise.

        :raises TimeoutException: If the "Copy" option is not present in the context menu, or the context menu is not
            present.
        """
        return 'disabled' not in self._copy_option.find().get_attribute("class")

    def double_click_cell(self, row_index: int, column_index: int, binding_wait_time: float = 0) -> None:
        """
        Double-click a cell of the Table.

        :param row_index: The zero-based index of the row containing the target cell.
        :param column_index: The zero-based index of the column containing the target cell.
        :param binding_wait_time: The amount of time (in seconds) to wait before allowing code to continue.

        :raises TimeoutException: If the supplied indices do not define a cell of the Table.
        """
        _locator = (By.CSS_SELECTOR, f'{self.__get_row_css_by_row_index(row_index=row_index)} '
                                     f'{self.__get_column_css_by_index(column_index=column_index)}')
        ComponentPiece(
            locator=_locator,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=self.poll_freq).double_click(binding_wait_time=binding_wait_time)

    def expand_subview_by_row_index(self, row_index: int) -> None:
        """
        Expand the subview of a row of the Table.

        :param row_index: The zero-based index of the row which contains the subview to be expanded.

        :raises TimeoutException: If no row exists with the supplied index.
        :raises AssertionError: If the interaction does not result in the subview being expanded.
        """
        if not self.subview_is_expanded(row_index=row_index):
            ComponentPiece(
                locator=(By.CSS_SELECTOR, self.__get_subview_css_by_row_index(row_index=row_index)),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                poll_freq=self.poll_freq)\
                .click(binding_wait_time=0.5)
        IAAssert.is_true(
            value=self.subview_is_expanded(row_index=row_index),
            failure_msg=f"Failed to expand a subview for row {row_index}.")

    def get_count_of_selected_rows(self) -> int:
        """
        Obtain a count of the rows which are at least partially selected.

        :returns: A count of rows where at least one cell of the row is currently selected.
        """
        return self._get_count_of_selected_rows()

    def get_dimensions_of_copy_option(self) -> Tuple[str, str]:
        """
        Obtain the width and height of the "Copy" option of the Table context menu.

        :raises TimeoutException: If the context menu of the Table is not present.
        """
        return self._copy_option.get_css_property(property_name=CSS.WIDTH).split('px')[0], \
            self._copy_option.get_css_property(property_name=CSS.HEIGHT).split('px')[0]

    def get_empty_message(self) -> str:
        """
        Obtain the text of the message displayed when the Table contains no data.

        :returns: The message displayed by the Table when there is no backing data.

        :raises TimeoutException: If the message is not present.
        """
        return self._empty_message.get_text()

    def get_empty_message_text_color(self) -> str:
        """
        Obtain the color in use for the message displayed when the Table contains no backing data.

        :returns: The color (as a string) of the message which is displayed when the Table contains no data.

        :raises TimeoutException: If the message is not present.
        """
        return self._empty_message.get_css_property(property_name=CSS.COLOR)

    def get_empty_message_icon_color(self) -> str:
        """
        Obtain the color in use for the icon displayed when the Table contains no backing data.

        :returns: The color (as a string) of the icon which is displayed when the Table contains no data.

        :raises TimeoutException: If the message is not present.
        """
        return self._empty_icon.get_fill_color()

    def get_empty_message_icon_name(self) -> str:
        """
        Obtain the slash-delimited path of the icon displayed when the Table contains no backing data.

        :returns: The path of the icon which is displayed when the Table contains no data as a slash-delimited string.

        :raises TimeoutException: If the message is not present.
        """
        return self._empty_icon.get_icon_name()

    def inclusive_select_cells_by_indices(
            self, list_of_row_column_index_tuples: List[Tuple[Union[int, str], Union[int, str]]]) -> None:
        """
        Select all content between a set of cells. Shift will be held during this event.

        :param list_of_row_column_index_tuples: A list of tuples where each tuple contains the zero-based index of the
            target row as the 0th element and the zero-based index of the target column as the 1th element.

        :raises TimeoutException: If any of the supplied tuples fail to define a valid cell.
        """
        cell_web_element_list = []
        tuple_row_index_location = 0
        tuple_column_index_location = 1
        for i in range(len(list_of_row_column_index_tuples)):
            _row_index = list_of_row_column_index_tuples[i][tuple_row_index_location]
            _column_index = list_of_row_column_index_tuples[i][tuple_column_index_location]
            _locator = (
                By.CSS_SELECTOR,
                f'{self.__get_row_css_by_row_index(row_index=_row_index)} '
                f'{self.__get_column_css_by_index(column_index=_column_index)}')
            cell_web_element_list.append(
                ComponentPiece(
                    locator=_locator,
                    driver=self.driver,
                    parent_locator_list=self.locator_list,
                    poll_freq=self.poll_freq).find())
            if len(cell_web_element_list) == 1:
                cell_web_element_list[0].click()
            else:
                IASelenium(driver=self.driver).inclusive_multi_select_elements(web_element_list=cell_web_element_list)

    def row_contains_subview(self, row_index: int) -> bool:
        """
        Determine if a row contains a subview.

        :param row_index: The zero-based index of the row to check.

        :returns: True, if the supplied row contains a subview. False, if the row does not contain a subview, or if the
            row does not exist.
        """
        try:
            return ComponentPiece(
                locator=(By.CSS_SELECTOR, self.__get_subview_css_by_row_index(row_index=row_index)),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                poll_freq=self.poll_freq).find() is not None
        except TimeoutException:
            return False

    def row_is_completely_selected(self, row_index: int) -> bool:
        """
        Determine if every cell of a row is currently selected.

        :param row_index: The zero-based index of the row to check.

        :returns: True, if every cel within the specified row is currently selected - False otherwise.
        """
        for i in range(self.get_column_count()):
            if not self.cell_is_selected(row_index=row_index, column_index=i):
                return False
        return True

    def rows_are_completely_selected(self, list_of_row_indices: List[Union[int, str]]) -> bool:
        """
        Determine if a set of rows is completely selected.

        :param list_of_row_indices: A list which contains the zero-based indices of al rows to check.

        :returns: True, if every row specified in the list is completely selected - False otherwise.

        :raises TimeoutException: If any of the specified rows does not exist.
        """
        for i in range(len(list_of_row_indices)):
            if not self.row_is_completely_selected(row_index=i):
                return False
        return True

    def set_cell_data_by_row_index_column_id(
            self,
            zero_based_row_index: int,
            column_id: str,
            text: str,
            commit_value: bool) -> None:
        """
        Set the data of a cell specified by a zero-based row index and a CASE-SENSITIVE column ID.

        :param zero_based_row_index: The zero-based index of the row you are targeting.
        :param column_id: The CASE-SENSITIVE id of the column you are targeting. Note that the id may not be the name
            of the column as the id is a direct mapping against the keys of the data in use.
        :param text: The new data to be set in the specified cell.
        :param commit_value: A boolean flag indicating whether to commit changes immediately or not.
            If True, changes will be committed by appending Keys.ENTER to it after setting the cell data.
            If False, changes will not be committed, allowing for further modifications before committing.

        :raises: TimeoutException: If the cell is not already in an editable state; this function does not prepare the
        cell for editing.
        """

        _locator = (By.CSS_SELECTOR, f'{self.__get_row_css_by_row_index(row_index=zero_based_row_index)} '
                                     f'{self.__get_column_css_by_column_id(column_id=column_id)} textarea.ia_textArea')
        if commit_value:
            text += Keys.ENTER
        text_input = CommonTextInput(
                locator=_locator,
                driver=self.driver,
                parent_locator_list=self.locator_list,
                poll_freq=self.poll_freq)
        """
        Note:
        After using commit changes, set_text will attempt to locate the <textarea> and verify if the text has been 
        set. However, the <textarea> disappears after committing the changes, resulting in a TimeoutException.
        A TimeoutException before attempting to set the text means the cell is not editable. The TimeoutException 
        swallowed while actually setting the cell is the one which is expected due to the <textarea> being removed from 
        the DOM.
        """
        text_input.find()
        try:
            text_input.set_text(text=text, release_focus=False)
        except TimeoutException:
            pass

    def scroll_to_row(self, row_index: int, align_to_top: bool = False) -> None:
        """
        Scroll the Table so that the specified row is visible.

        :param row_index: The zero-based index of the row we will scroll to.
        :param align_to_top: If True, we will try to align the row to the Top of the viewport. If False, we will attempt
            to align the row to the bottom of the viewport.

        :raises TimeoutException: If no row exists with the supplied index.
        """
        row_index = int(row_index)
        rows = ComponentPiece(
            locator=self._ROW_GROUP_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=self.poll_freq)
        min_index = min([int(row.get_attribute('data-row-index')) for row in rows.find_all()])
        max_index = max([int(row.get_attribute('data-row-index')) for row in rows.find_all()])
        if min_index > row_index:
            self._scroll_to_row(row_index=min_index, align_to_top=False)
            self.scroll_to_row(row_index=row_index, align_to_top=align_to_top)
        elif max_index < row_index:
            self._scroll_to_row(row_index=max_index, align_to_top=True)
            self.scroll_to_row(row_index=row_index, align_to_top=align_to_top)
        else:
            self._scroll_to_row(row_index=row_index, align_to_top=align_to_top)

    def subview_is_expanded(self, row_index: int) -> bool:
        """
        Determine if a subview is expanded for a given row. Only works properly in tables which have virtualization
        disabled, or if the row is already in view.

        :param row_index: The zero-based index of the row to check.
        """
        try:
            return "open" in ComponentPiece(
                locator=(By.CSS_SELECTOR, self.__get_subview_css_by_row_index(row_index=row_index)),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                poll_freq=self.poll_freq).find(wait_timeout=1).get_attribute("class")
        except TimeoutException:
            return False

    def _get_count_of_selected_rows(self) -> int:
        """
        Obtain a count of rows where at least one cell of the row is selected.
        """
        try:
            count = 0
            for row in self._rows.find_all():
                try:
                    row.find_element(*self._SELECTED_CELL_LOCATOR)
                    count += 1
                except NoSuchElementException:
                    pass
            return count
        except StaleElementReferenceException:
            return self.get_count_of_selected_rows()

    def _scroll_to_row(self, row_index: int, align_to_top: bool = False) -> None:
        """
        Scroll the Table so that the specified row is visible.

        :param row_index: The zero-based index of the row we will scroll to.
        :param align_to_top: If True, we will try to align the row to the Top of the viewport. If False, we will attempt
            to align the row to the bottom of the viewport.

        :raises TimeoutException: If no row exists with the supplied index.
        """
        row = ComponentPiece(
            locator=(By.CSS_SELECTOR, self.__get_row_css_by_row_index(row_index=row_index)),
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=self.poll_freq)
        row.scroll_to_element(align_to_top=align_to_top)
        row.wait_on_binding()

    def __get_column_css_by_index(self, column_index: Union[int, str]) -> str:
        """Obtain the CSS which defines a column based on its index."""
        return f'{self._CELL_LOCATOR[1]}[data-column-index="{column_index}"]'

    def __get_column_css_by_column_id(self, column_id: Union[int, str]) -> str:
        """Obtain the CSS which defines a column based on its id."""
        return f'{self._CELL_LOCATOR[1]}[data-column-id="{column_id}"]'

    def __get_row_css_by_row_index(self, row_index: Union[int, str]) -> str:
        """Obtain the CSS which defines a row based on its index."""
        return f'{self._ROW_GROUP_LOCATOR[1]}[data-row-index="{row_index}"] {self._ROW_LOCATOR[1]}'

    def __get_subview_css_by_row_index(self, row_index: Union[int, str]) -> str:
        """Obtain the CSS which defines a subview based on the index of the row which contains it."""
        return f'{self.__get_row_css_by_row_index(row_index=row_index)} {self._SUBVIEW_ARROW_CSS}'


class _TableHeader(Header):
    _ACTIVE_FILTER_CLASS = "ia_table__head__header__filter--active"
    _HEADER_GROUP_LOCATOR = (By.CSS_SELECTOR, "div.tr-group")

    def __init__(
            self,
            driver: WebDriver,
            parent_locator_list: List[Tuple[By, str]],
            wait_timeout: float = 1,
            poll_freq: float = 0.5):
        super().__init__(
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            poll_freq=poll_freq)
        self._filter_modal = FilterModal(driver=driver)
        self._header_row_groups = {}
        self._header_row_group_cells = {}

    def click_filter_for_column(self, column_index: int) -> None:
        """
        Click the filter icon for a given column.

        :param column_index: The numeric index of the column which contains the filter icon we will click.

        :raises TimeoutException: If the supplied column is not configured to allow for filtering.
        """
        self._get_filter_by_column_index(column_index=column_index).click()

    def column_has_active_filter_applied(self, column_index: int) -> bool:
        """
        Determine if a column has a filter currently applied.

        :param column_index: The numeric index of the column to check for an applied filter.

        :returns: True, if the column with the provided index has a filter applied - False otherwise.
        """
        try:
            return self._ACTIVE_FILTER_CLASS in self._get_filter_icon_by_column_index(
                column_index=column_index).find().get_attribute("class")
        except TimeoutException:
            return False

    def filter_icon_is_displayed_for_column(self, column_index: int) -> bool:
        """
        Determine if the supplied column is currently displaying a filter icon.

        :param column_index: The zero-based index of the column to check for a filter icon in the Header.

        :returns: True, if the column is currently displaying an icon. False, if no icon is currently displayed. If
            receiving a return of False but expecting True, verify the column is not configured to only display the
            icon on-hover.
        """
        try:
            return self._get_filter_by_column_index(column_index=column_index).find().is_displayed()
        except TimeoutException:
            return False

    def get_count_of_header_row_groups(self) -> int:
        """
        Obtain a count of how many Header Row Groups are present in the Header of the Table.

        :returns: A count of Header Row Groups.
        """
        try:
            return len(self._get_header_row_group(zero_based_header_row_group_index=None).find_all())
        except TimeoutException:
            return 0

    def get_labels_from_header_row_group(self, zero_based_header_row_group_index: Union[int, str]) -> List[str]:
        """
        Obtain the labels of all cells within the specified Header Row Group.

        :param zero_based_header_row_group_index: The 0-based index of the Header Group Row you would like the labels
            of.

        :returns: A list, where each entry is the text of a label within the specified Header Row Group.
        """
        try:
            return [_.text for _ in self._get_header_row_group(
                zero_based_header_row_group_index=zero_based_header_row_group_index).find_all()]
        except TimeoutException:
            return []

    def get_origin_of_header_row_group_cell(
            self, label_text: str, zero_based_header_row_group_index: Union[int, str] = 0) -> Point:
        """
        Obtain a two-dimensional point in the viewport which represents the upper-left corner of the Header Row Group
        cell defined by the supplied arguments.

        :param label_text: The text of the cell you want the origin of.
        :param zero_based_header_row_group_index: The 0-based index of the Header Row Group you expect this cell to
            belong to.

        :returns: The location of the upper-left corner of the Header Group Row cell defined by the supplied arguments.
        """
        return self._get_cell_from_header_row_group(
            zero_based_header_row_group_index=zero_based_header_row_group_index, label=label_text).get_origin()

    def get_termination_of_header_row_group_cell(
            self, label_text: str, zero_based_header_row_group_index: Union[int, str] = 0) -> Point:
        """
        Obtain a two-dimensional point in the viewport which represents the bottom-right corner of the Header Row Group
        cell defined by the supplied arguments.

        :param label_text: The text of the cell you want the origin of.
        :param zero_based_header_row_group_index: The 0-based index of the Header Row Group you expect this cell to
            belong to.

        :returns: The location of the bottom-right corner of the Header Group Row cell defined by the supplied
            arguments.
        """
        return self._get_cell_from_header_row_group(
            zero_based_header_row_group_index=zero_based_header_row_group_index, label=label_text).get_termination()

    def set_column_filter_condition(self, condition: ColumnConfigurations.Filter.Condition) -> None:
        """
        Set the current filtering condition of a column within the open filtering modal.

        :param condition: The condition to use.

        :raises TimeoutException: If the column filtering modal is not present.
        :raises AssertionError: If the interaction does not result in the condition being selected.
        """
        self._filter_modal.set_condition(condition=condition.value)

    def _get_filter_by_column_index(self, column_index: int) -> ComponentPiece:
        """
        Obtain the filter piece of the column with the specified index.
        """
        filter_comp = self._filter_cells.get(column_index)
        if not filter_comp:
            filter_comp = ComponentPiece(
                locator=(By.CSS_SELECTOR, "div.filter-button svg"),
                driver=self.driver,
                parent_locator_list=self._get_header_cell_by_index(column_index=column_index).locator_list,
                wait_timeout=1)
            self._filter_cells[column_index] = filter_comp
        return filter_comp

    def _get_filter_icon_by_column_index(self, column_index: Union[int, str]) -> ComponentPiece:
        """
        Obtain the icon of the filter for a column by providing the column index.
        """
        return ComponentPiece(
            locator=(By.CSS_SELECTOR, "path.iaFilterIcon"),
            driver=self.driver,
            parent_locator_list=self._get_filter_by_column_index(column_index=column_index).locator_list)

    def _get_header_row_group(
            self,
            zero_based_header_row_group_index: Optional[Union[int, str]] = 0) -> ComponentPiece:
        """
        Obtain a Header Row Group of varying specificity, based on the supplied arguments.

        :param zero_based_header_row_group_index: The 0-based index of the Header Row Group. If None is supplied, then
            all row groups will be matched.

        :returns: A ComponentPiece which defines the Header Group entry with varying levels of specificity; the more
            information supplied, the more specific the locator will be.
        """
        index = str(zero_based_header_row_group_index) \
            if zero_based_header_row_group_index is not None else zero_based_header_row_group_index
        header_row_group = self._header_row_groups.get(index)
        if not header_row_group:
            row_index_piece = f'[data-row-index="{index}"]' if index is not None else ''
            header_row_group = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'{self._HEADER_GROUP_LOCATOR[1]}{row_index_piece}'),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                description=f"The {zero_based_header_row_group_index}th row of Header Row Groups.",
                poll_freq=self.poll_freq)
            self._header_row_groups[index] = header_row_group
        return header_row_group

    def _get_cell_from_header_row_group(
            self,
            label: str,
            zero_based_header_row_group_index: Optional[Union[int, str]] = 0):
        index = str(zero_based_header_row_group_index) \
            if zero_based_header_row_group_index is not None else zero_based_header_row_group_index
        cell = self._header_row_group_cells.get((index, label))
        if not cell:
            cell = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'div.tc[data-label="{label}"]'),
                driver=self.driver,
                parent_locator_list=self._get_header_row_group(
                    zero_based_header_row_group_index=zero_based_header_row_group_index).locator_list,
                description=f"A Header Row Group cell in the {zero_based_header_row_group_index}th row, with a "
                            f"label of '{label}'.",
                poll_freq=self.poll_freq)
            self._header_row_group_cells[(index, label)] = cell
        return cell


class Table(CommonTable, BasicPerspectiveComponent):
    """
    A Perspective Table Component.
    """
    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 10,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        CommonTable.__init__(
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
            poll_freq=poll_freq)
        self._body = _TableBody(driver=driver, parent_locator_list=self.locator_list, poll_freq=poll_freq)
        self._filter = Filter(driver=driver, parent_locator_list=self.locator_list, poll_freq=poll_freq)
        self._filter_modal = FilterModal(driver=driver)
        self._footer = Footer(driver=driver, parent_locator_list=self.locator_list, poll_freq=poll_freq)
        self._header = _TableHeader(driver=driver, parent_locator_list=self.locator_list, poll_freq=poll_freq)
        self._pager = Pager(driver=driver, parent_locator_list=self.locator_list, poll_freq=poll_freq)

    def apply_column_filter(self) -> None:
        """
        Apply the current configuration of the filter for the column.

        :raises TimeoutException: If the filter modal and/or Apply button within the modal is not present.
        """
        self._filter_modal.click_apply_button()

    def cell_is_root_selection(self, row_index: int, column_index: int) -> bool:
        """
        Determine if the cell defined by the supplied indices is the root of the current selection.

        :param row_index: The zero-based index of the target row.
        :param column_index: The zero-based index of the target column.

        :returns: True, if the resultant cell is the root of the current selection - False otherwise.

        :raises TimeoutException: If no cell is defined by the supplied indices.
        """
        return self._body.cell_is_root_selection(row_index=row_index, column_index=column_index)

    def cell_is_selected(self, row_index: int, column_index: int) -> bool:
        """
        Determine if a specified cell is currently part of the active selection of the Table.

        :param row_index: The zero-based index of the row we will check.
        :param column_index: The zero-based index of the column we will check.

        :returns: True, if the resultant cell is part of the current selection of the Table.

        :raises TimeoutException: If the supplied row and column indices are invalid.
        """
        return self._body.cell_is_selected(row_index=row_index, column_index=column_index)

    def click(self, wait_timeout=None, binding_wait_time: float = 0) -> None:
        """
        This method is only here to override the inherited method and prevent any generic clicking of the Table.

        :raises NotImplementedError: Please don't blindly click the Table...
        """
        raise NotImplementedError

    def click_copy_option(self) -> None:
        """
        Click the "Copy" option of the displayed context menu. Note: the context menu the copy option belongs to must be
        triggered/displayed before invoking this function.

        :raises TimeoutException: If the context menu which contains the copy option is not present.
        """
        self._body.click_copy_option()

    def click_filter_for_column(self, column_index: int) -> None:
        """
        Click the filter icon for a given column.

        :param column_index: The numeric index of the column which contains the filter icon we will click.

        :raises TimeoutException: If the supplied column is not configured to allow for filtering.
        """
        self._header.click_filter_for_column(column_index=column_index)

    def click_first_page_button(self) -> None:
        """
        Click the option in the Page which would take a user to the 'first' page.

        :raises TimeoutException: If the 'First' page option is not present in the Pager.
        :raises AssertionError: If clicking the 'First' page button does result in the Table displaying the first page.
        """
        self._pager.click_first_page_button()

    def click_last_page_button(self) -> None:
        """
        Click the option in the Page which would take a user to the 'last' page.

        :raises TimeoutException: If the 'Last' page option is not present in the Pager.
        """
        self._pager.click_last_page_button()

    def click_next_page_chevron(self) -> None:
        """
        Click the chevron which would take the user to the next page.

        :raises TimeoutException: If the 'next' chevron does not exist, or if no page numbers exist in the Pager.
        """
        self._pager.click_next_page_chevron()

    def click_page_number(self, page_number: Union[int, str]) -> None:
        """
        Click a page number within the Pager.

        :param page_number: The page number you wish to click.

        :raises TimeoutException: If no page numbers are present in the Pager.
        :raises IndexError: If the specified page number is not present in the Pager.
        :raises AssertionError: If the Table does not end up displaying the specified page number.
        """
        self._pager.click_page_number(desired_page=page_number)

    def click_previous_page_chevron(self) -> None:
        """
        Click the chevron which would take the user to the previous page.

        :raises TimeoutException: If the 'previous' chevron does not exist.
        """
        self._pager.click_previous_page_chevron()

    def collapse_subview_by_row_index(self, row_index: int) -> None:
        """
        Collapse an expanded subview. Takes no action if the subview is already collapsed.

        :param row_index: The zero-based index of the row which might have an expanded subview.

        :raises TimeoutException: if no row exists with the supplied index.
        """
        self._body.collapse_subview_by_row_index(row_index=row_index)

    def column_filter_modal_apply_button_is_enabled(self) -> bool:
        """
        Determine if the Apply button is enabled in the modal.

        :returns: True, if the Apply button is enabled - False otherwise.

        :raises TimeoutException: if the Apply button is not present.
        """
        return self._filter_modal.apply_button_is_enabled()

    def column_filter_modal_is_displayed(self) -> bool:
        """
        Determine if the filter modal is currently displayed.

        :returns: True, if the filter modal is currently displayed - False otherwise.
        """
        return self._filter_modal.is_displayed()

    def column_filter_modal_value_input_is_enabled(self) -> bool:
        """
        Determine if the basic value input field in the filter modal is enabled.

        :returns: True, if the value input is enabled - False otherwise.

        :raises TimeoutException: If the value input field is not present.
        """
        return self._filter_modal.value_input_is_enabled()

    def contains_sub_views(self) -> bool:
        """
        Determine if the Table contains subviews. This function does not reflect the current display state of subviews
        - only their presence.

        :returns: True, if the Table contains Subviews - False otherwise.
        """
        return self._body.contains_subviews()

    def copy_option_is_displayed(self) -> bool:
        """
        Determine if the "Copy" option is currently displayed in a context menu of the Table.

        :returns: True, if the "Copy" option is currently displayed in a context menu - False otherwise.
        """
        return self._body.copy_option_is_displayed()

    def copy_option_is_enabled(self) -> bool:
        """
        Determine if the "Copy" option of the context menu is currently enabled.

        :returns: True, if the "Copy" option of the Table's context menu is currently enabled - False otherwise.

        :raises TimeoutException: If the "Copy" option is not present in the context menu, or the context menu is not
            present.
        """
        return self._body.copy_option_is_enabled()

    def double_click_cell_in_body(self, row_index: int, column_index: int) -> None:
        """
        Double-click a cell in the body of the Table.

        :param row_index: The zero-based index of the row containing the target cell.
        :param column_index: The zero-based index of the column containing the target cell.

        :raises TimeoutException: If the supplied indices do not define a cell of the Table.
        """
        self._body.double_click_cell(row_index=row_index, column_index=column_index)

    def end_time_hours_input_is_enabled_in_filtering_modal(self) -> bool:
        """
        Determine if the input for hours for the ending date is currently enabled.

        :returns: True, if the input which drives the hours of the ending date is currently enabled - False otherwise.

        :raises TimeoutException: If the hours input for the ending date is not present.
        """
        return self._filter_modal.end_time_hours_input_is_enabled()

    def end_time_minutes_input_is_enabled_in_filtering_modal(self) -> bool:
        """
        Determine if the input for minutes for the ending date is currently enabled.

        :returns: True, if the input which drives the minutes of the ending date is currently enabled - False otherwise.

        :raises TimeoutException: If the minutes input for the ending date is not present.
        """
        return self._filter_modal.end_time_minutes_input_is_enabled()

    def end_time_seconds_input_is_enabled_in_filtering_modal(self) -> bool:
        """
        Determine if the input for seconds for the ending date is currently enabled.

        :returns: True, if the input which drives the seconds of the ending date is currently enabled - False otherwise.

        :raises TimeoutException: If the seconds input for the ending date is not present.
        """
        return self._filter_modal.end_time_seconds_input_is_enabled()

    def entire_row_is_selected(self, row_index: int) -> bool:
        """
        Determine if every cell in a row is selected.

        :returns: True if every cell in the specified row is selected - False otherwise.
        """
        return self._body.row_is_completely_selected(row_index=row_index)

    def expand_subview_by_row_index(self, row_index: int) -> None:
        """
        Expand the subview of a row of the Table.

        :param row_index: The zero-based index of the row which contains the subview to be expanded.

        :raises TimeoutException: If no row exists with the supplied index.
        :raises AssertionError: If the interaction does not result in the subview being expanded.
        """
        self._body.expand_subview_by_row_index(row_index=row_index)

    def column_filter_icon_is_displayed_for_column(self, column_index: int) -> bool:
        """
        Determine if the supplied column is currently displaying a filter icon.

        :param column_index: The zero-based index of the column to check for a filter icon in the Header.

        :returns: True, if the column is currently displaying an icon. False, if no icon is currently displayed. If
            receiving a return of False but expecting True, verify the column is not configured to only display the
            icon on-hover.
        """
        return self._header.filter_icon_is_displayed_for_column(column_index=column_index)

    def filter_is_present(self) -> bool:
        """
        Determine if the filter for the table exists.

        :returns: True, if the filter for the table exists - False otherwise. This function makes no claims about
            visibility.
        """
        return self._filter.is_present()

    def first_page_button_is_displayed(self) -> bool:
        """
        Determine if the 'First' page option is displayed in the Pager.

        :returns: True, if a user can see the 'First' page option in the Pager.
        """
        return self._pager.first_page_button_is_displayed()

    def first_page_button_is_enabled(self) -> bool:
        """
        Determine if the 'First' page option is enabled in the Pager.

        :returns: True, if the 'First' page option in the Pager is enabled.

        :raises TimeoutException: If the 'First' page option is not present in the Pager.
        """
        return self._pager.first_page_button_is_enabled()

    def footer_is_present(self) -> bool:
        """
        Determine if the Table is currently displaying a Footer.

        :returns: True, if the Table is currently displaying a Footer - False otherwise.
        """
        return self._footer.footer_is_present()

    def get_active_page(self) -> int:
        """
        Obtain the number of the currently displayed page of the Table.

        :returns: The number of the currently displayed page.

        :raises TimeoutException: If no page numbers are present.
        """
        return self._pager.get_active_page()

    def get_all_listed_pages(self) -> List[int]:
        """
        Obtain all displayed page numbers.

        :returns: All page numbers available for clicking in the Pager, including the current (disabled) page.
        """
        return self._pager.get_all_listed_pages()

    def get_all_row_display_options(self) -> List[str]:
        """
        Obtain all selection options form the dropdown which controls how many rows may be displayed in the Table.

        :returns: A list of strings, where each entry is an option available for selection to drive the count of rows
            displayed by the Table.

        :raises TimeoutException: If the row count dropdown is not present.
        """
        return self._pager.get_all_row_display_options()

    def get_available_column_filter_conditions(self, column_index: int) -> List[str]:
        """
        Obtain all options available to the user in the condition dropdown.

        :returns: A list which contains the text of every option in the dropdown of available conditions.

        :raises TimeoutException: If the dropdown which contains available conditions is not present.
        """
        if not self.column_filter_modal_is_displayed():
            self.click_filter_for_column(column_index=column_index)
        return self._filter_modal.get_available_conditions()

    def get_text_of_remove_filter_and_apply_button(self) -> Tuple[str, str]:
        """
        Obtain the text of the Remove Filter link and the Apply Button.

        :returns: A tuple, where the 0th element is the text of the Remove Filter link, and the 1th element is the text
            of the Apply button.

        :raises TimeoutException: If either the Remove Filter link or the Apply button is not present.
        """
        return (
            self._filter_modal.get_remove_filter_link_text(),
            self._filter_modal.get_apply_button_text()
        )

    def get_dimensions_of_copy_option(self) -> Tuple[str, str]:
        """
        Obtain the width and height of the "Copy" option of the Table context menu.

        :returns: A tuple, where the 0th element is the width of the copy option and the 1th element is the height.

        :raises TimeoutException: If the context menu of the Table is not present.
        """
        return self._body.get_dimensions_of_copy_option()

    def get_displayed_row_data_as_a_list_of_dictionaries(
            self, start_row_index: Optional[int] = None, end_row_index: Optional[int] = None) -> List[dict]:
        """
        Obtain the data of a subset of rows.

        :param start_row_index: The zero-based index of the row which defines the beginning of the subset. If not
            supplied, we will begin with the 0th row.
        :param end_row_index: The zero-based index of the row which defines the end of the subset. if not supplied,
            we will end with the last row.

        :returns: A list of dictionaries, where the keys of each dictionary match the columns ids.

        :raises IndexError: If the supplied row indices are invalid based on the data.
        """
        return [
            self.get_row_data_by_row_index(row_index=row_index)
            for row_index in range(self.get_count_of_rows())
        ][start_row_index:end_row_index]

    def get_empty_message(self) -> str:
        """
        Obtain the text of the message displayed when the Table contains no data.

        :returns: The message displayed by the Table when there is no backing data.

        :raises TimeoutException: If the message is not present.
        """
        return self._body.get_empty_message()

    def get_empty_message_text_color(self) -> str:
        """
        Obtain the color in use for the message displayed when the Table contains no backing data.

        :returns: The color (as a string) of the message which is displayed when the Table contains no data.

        :raises TimeoutException: If the message is not present.
        """
        return self._body.get_empty_message_text_color()

    def get_empty_message_icon_name(self) -> str:
        """
        Obtain the slash-delimited path of the icon displayed when the Table contains no backing data.

        :returns: The path of the icon which is displayed when the Table contains no data as a slash-delimited string.

        :raises TimeoutException: If the message is not present.
        """
        return self._body.get_empty_message_icon_name()

    def get_enabled_days_from_column_filter_picker(self) -> List[int]:
        """
        Obtain all days available for selection in the current month.

        :returns: A list with the numbers of all available days within the current month.

        :raises TimeoutException: If the date picker (calendar) is not present.
        """
        return self._filter_modal.get_enabled_days_from_picker()

    def get_height_of_row(self, row_index: int, include_units: bool = False) -> str:
        """
        Obtain the height of a row.

        :param row_index: The zero-based index of the row you are targeting.
        :param include_units: A value of True specifies we should include the units of measurement (almost always
            'px'), while a value of False specifies we should return only the numeric value (as a string).

        :returns: The height of the specified row as a string, because it might have units attached.

        :raises TimeoutException: If the specified row index does not exist.
        """
        return self._body.get_height_of_row_by_index(
            zero_based_row_index=row_index, include_units=include_units)

    def get_labels_from_header_row_group(self, zero_based_header_row_group_index: Union[int, str] = 0) -> List[str]:
        """
        Obtain the labels of all cells within the specified Header Row Group.

        :param zero_based_header_row_group_index: The 0-based index of the Header Group Row you would like the labels
            of.

        :returns: A list, where each entry is the text of a label within the specified Header Row Group.
        """
        return self._header.get_labels_from_header_row_group(
            zero_based_header_row_group_index=zero_based_header_row_group_index)

    def get_last_displayed_page_number(self) -> int:
        """
        Obtain the number of the last page available in the Pager. This value may not be the count of Pages of data,
        but is the last number a user sees displayed.

        Example: A Table may have 40 pages, but the pager may only allow for quick navigation to pages 1, 2, 3, 4, or 5
        before then displaying the 'Last' page option, or a 'next set of pages' option.

        :returns: The last visible page number available for clicking in the Pager.

        :raises TimeoutException: If no pages numbers are present.
        """
        return self._pager.get_last_displayed_page_number()

    def get_list_of_displayed_column_names_from_header(self) -> List[str]:
        """
        :returns: A list of Strings which contains all the column names from the header.
        """
        return self.get_column_names_from_header()

    def get_origin_of_cell_in_header_rwo_group(
            self,
            label_text: str,
            zero_based_header_row_group_index: Union[int, str] = 0) -> Point:
        """
        Obtain a two-dimensional point in the viewport which represents the upper-left corner of the Header Row Group
        cell defined by the supplied arguments.

        :param label_text: The text of the cell you want the origin of.
        :param zero_based_header_row_group_index: The 0-based index of the Header Row Group you expect this cell to
            belong to.

        :returns: The location of the upper-left corner of the Header Group Row cell defined by the supplied arguments.
        """
        return self._header.get_origin_of_header_row_group_cell(
            label_text=label_text, zero_based_header_row_group_index=zero_based_header_row_group_index)

    def get_row_group_count(self) -> int:
        """
        Obtain a count of row groups. Row groups are distinct from rows, in that row GROUPS can contain multiple rows
        and potentially subviews. They are a way of grouping row content which belongs together into one container.

        :returns: A numeric count of row groups currently displayed within the Table.
        """
        return self._body.get_row_group_count()

    def get_row_data_by_row_index(self, row_index: int) -> dict:
        """
        Get the data from a specified row as a dictionary, with the column names as the keys.
        :param row_index: This argument is cast as an int, and is used to determine what row we
        should obtain data from.

        :returns: dict - The data of the row packaged as a dictionary, where they keys are the column ids.
        """
        return self._body.get_row_data_by_row_index(zero_based_row_index=row_index)

    def get_cell_data_by_row_index_column_index(self, row_index: int, column_index: int) -> str:
        """
        Get the data of a specific cell in the table. NOTE: this always returns a str, due to how the DOM stores the
        information.

        :param row_index: The zero-based index of the ROW you are targeting.
        :param column_index: The zero-based index of the COLUMN you are targeting.

        :returns: The data of the cell as a string.

        :raises TimeoutException: If no cell exists with the provided indices.
        """
        return self._body.get_cell_data_by_row_index_column_index(
            zero_based_row_index=row_index, zero_based_column_index=column_index)

    def get_cell_data_by_row_index_column_id(self, row_index: int, column_id: str) -> str:
        """
        Get the data of a specific cell in the table by supplying the index of the row and the CASE-SENSITIVE
        id of the column. NOTE: this always returns a str, due to how the DOM stores the information.

        :param row_index: The zero-based index of the ROW you are targeting.
        :param column_id: The case-sensitive id of the column you are targeting.

        :returns: The data of the cell as a string.

        :raises TimeoutException: If no cell exists with the provided row index in the supplied column.
        """
        return self._body.get_cell_data_by_row_index_column_id(
            zero_based_row_index=row_index, column_id=column_id)

    def get_column_names_from_footer(self) -> List[str]:
        """
        Obtain all column names displayed in the Footer.

        :returns: A list which contains all column names displayed in the Footer.

        :raises TimeoutException: If no Footer is present.
        """
        return self._footer.get_column_names()

    def get_count_of_header_row_groups(self) -> int:
        """
        Obtain a count of how many Header Row Groups are present in the Header of the Table.

        :returns: A count of Header Row Groups.
        """
        return self._header.get_count_of_header_row_groups()

    def get_count_of_selected_rows(self) -> int:
        """
        Get a count of rows for which every cell in the row is selected.

        :returns: The count of rows for which every cell in the row is selected.
        """
        return self._body.get_count_of_selected_rows()

    def get_active_page_from_listings(self) -> int:
        """
        Obtain the value text of the "active" page as conveyed by the clickable page links in the pager.

        :returns: The number of the active page link.
        """
        return self._pager.get_active_page()

    def get_displayed_rows_selection(self) -> int:
        """
        Obtain the value of the row display dropdown from the pager.

        :returns: The value of the row display dropdown in the Pager.
        """
        return self._pager.get_selected_row_count_option_from_dropdown()

    def get_selected_row_count_option(self) -> int:
        """
        Obtain the currently selected VALUE from the dropdown which dictates how many rows are displayed.

        :returns: The currently selected count of rows which should be displayed. If "25 rows" is selected, this will
            return 25.

        :raises TimeoutException: If the row count dropdown is not present. This dropdown/select piece is only present
            while the Table is wider than 700px.
        """
        return self._pager.get_selected_row_count_option_from_dropdown()

    def get_termination_of_cell_in_row_group_header(
            self, label_text: str, zero_based_header_row_group_index: Union[int, str] = 0) -> Point:
        """
        Obtain a two-dimensional point in the viewport which represents the bottom-right corner of the Header Row Group
        cell defined by the supplied arguments.

        :param label_text: The text of the cell you want the origin of.
        :param zero_based_header_row_group_index: The 0-based index of the Header Row Group you expect this cell to
            belong to.

        :returns: The location of the bottom-right corner of the Header Group Row cell defined by the supplied
            arguments.
        """
        return self._header.get_termination_of_header_row_group_cell(
            label_text=label_text, zero_based_header_row_group_index=zero_based_header_row_group_index)

    def get_text_of_filter_results(self) -> str:
        """
        Obtain the text of the label which provides feedback on the results of the filter.

        :returns: A description of how many results match the applied filter string ("X result(s)").

        :raises TimeoutException: If the feedback filter is not present.
        """
        return self._filter.get_results_text()

    def go_to_page(self, page_number: int) -> None:
        """
        Use the page jump input field to go to a specific page in the Table.

        :param page_number: The page of the Table to go to.

        :raises TimeoutException: If the page jump input is not present.
        :raises AssertionError: If the Table does not end up on the supplied page.
        """
        self._pager.jump_to_page(page_to_jump_to=page_number)

    def hour_input_is_displayed_in_filter_modal(self) -> bool:
        """
        Determine if the hours input is displayed. This should not be used when dealing with a time condition of
        "between", because multiple hour inputs might be present.

        :returns: True, if any hour input is displayed.
        """
        return self._filter_modal.hour_input_is_displayed()

    def hour_input_is_enabled_in_filter_modal(self) -> bool:
        """
        Determine if the hours input is enabled. This should not be used when dealing with a time condition of
        "between", because multiple hour inputs might be present.

        :returns: True, if the hour input field is enabled.
        """
        return self._filter_modal.hour_input_is_enabled()

    def jump_input_is_displayed(self) -> bool:
        """
        Determine if the input which allows for a user to type a page number is displayed.

        :returns: True, if the user is able to type a page number into the Pager - False otherwise.
        """
        return self._pager.jump_input_is_displayed()

    def jump_to_page(self, page_number: int) -> None:
        """
        Use the page jump input field to go to a specific page in the Table.

        :param page_number: The page of the Table to go to.

        :raises TimeoutException: If the page jump input is not present.
        :raises AssertionError: If the Table does not end up on the supplied page.
        """
        self._pager.jump_to_page(page_to_jump_to=page_number)

    def last_page_button_is_displayed(self) -> bool:
        """
        Determine if the 'Last' page option is displayed in the Pager.

        :returns: True, if a user can see the 'Last' page option in the Pager.
        """
        return self._pager.last_page_button_is_displayed()

    def last_page_button_is_enabled(self) -> bool:
        """
        Determine if the 'Last' page option is enabled in the Pager.

        :returns: True, if the 'Last' page option in the Pager is enabled.

        :raises TimeoutException: If the 'Last' page option is not present in the Pager.
        """
        return self._pager.last_page_button_is_enabled()

    def minute_input_is_displayed_in_filter_modal(self) -> bool:
        """
        Determine if the minutes input is displayed. This should not be used when dealing with a time condition of
        "between", because multiple minute inputs might be present.

        :returns: True, if any minute input is displayed.
        """
        return self._filter_modal.minute_input_is_displayed()

    def minute_input_is_enabled_in_filter_modal(self) -> bool:
        """
        Determine if the minutes input is enabled. This should not be used when dealing with a time condition of
        "between", because multiple minute inputs might be present.

        :returns: True, if the minute input field is enabled.
        """
        return self._filter_modal.minute_input_is_enabled()

    def next_page_chevron_is_enabled(self) -> bool:
        """
        Determine if the next page chevron is enabled.

        :returns: True, if the next page chevron is enabled - False otherwise.
        """
        return self._pager.next_page_chevron_is_enabled()

    def page_number_is_displayed(self, page_number: int) -> bool:
        """
        Determine if a specific page number is currently displayed.

        :param page_number: The number of the page for which we will verify display status.

        :returns: True, if the supplied page number is currently displayed - False otherwise.

        :raises TimeoutException: If no page numbers are displayed in the Pager.
        """
        return self._pager.page_number_is_displayed(desired_page=page_number)

    def pager_is_displayed(self, location: Pager.Location = Pager.Location.BOTTOM) -> bool:
        """
        Determine if the specified pager is displayed.

        :returns: True, if the specified pager is displayed - False otherwise.
        """
        return self._pager.is_displayed(location=location)

    def previous_page_chevron_is_enabled(self) -> bool:
        """
        Determine if the previous page chevron is enabled.

        :returns: True, if the previous page chevron is enabled - False otherwise.

        :raises TimeoutException: If the previous page chevron is not present.
        """
        return self._pager.previous_page_chevron_is_enabled()

    def remove_column_filter(self, column_index: int) -> None:
        """
        Remove the applied filter for a column.

        :param column_index: The zero-based index of the column for which we wil remove the applied filter.

        :raises TimeoutException: If the column is not configured to have any filtering done.
        :raises AssertionError: If unable to successfully remove any filter from the column.
        """
        if not self.column_filter_modal_is_displayed():
            self.hover_over_column_header(column_index=column_index)
            self.click_filter_for_column(column_index=column_index)
        try:
            self._filter_modal.click_remove_filter()
        except ElementClickInterceptedException:
            selenium = IASelenium(driver=self.driver)
            original_height = selenium.get_inner_height()
            selenium.set_inner_window_dimensions(inner_height=float(original_height) + 50)
            try:
                self._filter_modal.click_remove_filter()
            finally:
                selenium.set_inner_window_dimensions(inner_height=original_height)
        if not self.column_filter_modal_is_displayed():
            self.hover_over_column_header(column_index=column_index)
        IAAssert.is_not_true(
            value=self._header.column_has_active_filter_applied(column_index=column_index),
            failure_msg=f"Failed to remove column filter for column {column_index}.")

    def results_label_is_displayed(self) -> bool:
        """
        Determine if information about filtered results is present.

        :returns: True, if a breakdown regarding filtered results is displayed.
        """
        return self._filter.results_text_content_is_displayed()

    def row_contains_subview(self, row_index: int) -> bool:
        """
        Determine if a row contains a subview.

        :param row_index: The zero-based index of the row to check.

        :returns: True, if the supplied row contains a subview. False, if the row does not contain a subview, or if the
            row does not exist.
        """
        return self._body.row_contains_subview(row_index=row_index)

    def rows_are_completely_selected(self, list_of_row_indices: List) -> bool:
        """
        Determine if a set of rows is completely selected.

        :param list_of_row_indices: A list which contains the zero-based indices of al rows to check.

        :returns: True, if every row specified in the list is completely selected - False otherwise.

        :raises TimeoutException: If any of the specified rows does not exist.
        """
        return self._body.rows_are_completely_selected(list_of_row_indices=list_of_row_indices)

    def row_select_dropdown_is_displayed(self) -> bool:
        """
        Determine if the dropdown which allows for specifying a row count to display is displayed.

        :returns: True, if the row count dropdown is displayed - False otherwise.
        """
        return self._pager.row_select_dropdown_is_displayed()

    def scroll_to_row(self, row_index: int, align_to_top: bool = False) -> None:
        """
        Scroll the Table so that the specified row is visible.

        :param row_index: The zero-based index of the row we will scroll to.
        :param align_to_top: If True, we will try to align the row to the Top of the viewport. If False, we will attempt
            to align the row to the bottom of the viewport.

        :raises TimeoutException: If no row exists with the supplied index.
        """
        return self._body.scroll_to_row(row_index=row_index, align_to_top=align_to_top)

    def seconds_input_is_enabled_in_modal(self) -> bool:
        """
        Determine if the seconds input is enabled. Distinct from :func:`end_time_seconds_input_is_enabled`, which is
        used for date ranges.

        :returns: True, if the seconds input is enabled - False otherwise.

        :raises TimeoutException: If the seconds input is not present.
        """
        return self._filter_modal.seconds_input_is_enabled()

    def seconds_input_is_displayed_in_modal(self) -> bool:
        """
        Determine if the seconds input is displayed. Distinct from :func:`end_time_seconds_input_is_displayed`, which is
        used for date ranges.

        :returns: True, if the seconds input is displayed - False otherwise.

        :raises TimeoutException: If the seconds input is not present.
        """
        return self._filter_modal.seconds_input_is_displayed()

    def select_cells_by_indices(self, list_of_row_column_index_tuples: List[Tuple[int, int]]) -> None:
        """
        Select a single cell or multiple cells from the table.

        Each tuple in the list should consist of two elements, where the 0th element is the zero-based row index,
        and the 1th element is the zero-based column index.

        :param list_of_row_column_index_tuples: A list of tuples which are the row index and the column index.

        :raises TimeoutException: If any of the tuples fail to define a cell of the Table.
        """
        self._body.inclusive_select_cells_by_indices(list_of_row_column_index_tuples=list_of_row_column_index_tuples)
        self.wait_on_binding(time_to_wait=0.5)

    def select_rows_to_display(self, count_of_rows: int) -> None:
        """
        This method expects a numeric value (either int or str), without the additional " rows" portion of the dropdown.
        For example: If you want 25 rows displayed, supply 25, but not "25 rows".

        :param count_of_rows: The numeric value of rows you would like displayed.
        """
        self._pager.set_displayed_row_count(count_of_rows=count_of_rows)

    def set_column_filter_condition(self, condition: ColumnConfigurations.Filter.Condition) -> None:
        """
        Select a condition from the dropdown.

        :param condition: The condition to select.

        :raises TimeoutException: If the condition dropdown is not present.
        :raises AssertionError: If we fail to select the supplied condition.
        """
        self._filter_modal.set_condition(condition=condition.value)

    def set_column_filter_date(self, date: PerspectiveDate, apply: bool = True) -> None:
        """
        Select a date, and potentially apply that date.

        :param date: The date to select in the filter modal.
        :param apply: If True, click the apply button. If False, take no action after selecting the date.

        :raises TimeoutException: If the date picker (calendar) is not present, or if the Apply button is not present.
        """
        self._filter_modal.select_date_and_apply(date=date, apply=apply)

    def set_column_filter_max_value(self, text: str) -> None:
        """
        Set the maximum value in use by the filter.

        :param text: The maximum value the filter should use.

        :raises TimeoutException: if the maximum value input field is not present.
        :raises AssertionError: If we fail to set the input to the supplied value.
        """
        self._filter_modal.set_maximum_range_value(text=text)

    def set_column_filter_min_value(self, text: str) -> None:
        """
        Set the minimum value in use by the filter.

        :param text: The minimum value the filter should use.

        :raises TimeoutException: if the minimum value input field is not present.
        :raises AssertionError: If we fail to set the input to the supplied value.
        """
        self._filter_modal.set_minimum_range_value(text=text)

    def set_column_filter_range(self, date_range: HistoricalRange) -> None:
        """
        Apply a historical range (start AND end date) to the filter modal and then click the Apply button.

        :param date_range: An object containing the start and end dates to be applied to the filter modal.

        :raises TimeoutException: If the date picker (calendar) is not present, or if the Apply button is not present.
        """
        self._filter_modal.select_range(historical_range=date_range)

    def set_column_filter_value(self, text: str) -> None:
        """
        Set the value for the condition. This function should be sued for condition which do not include ranges of any
        type.

        :param text: The value of the condition.

        :raises TimeoutException: if the value input field is not present.
        :raises AssertionError: If we fail to set the input to the supplied value.
        """
        self._filter_modal.set_value_for_condition(text=text)

    def set_displayed_row_count(self, desired_row_count: int) -> None:
        """
        Set the number of displayed rows in the Table. The count of rows must be a valid value from the
        dropdown (Select) in the Pager.

        :param desired_row_count: The desired count of rows (this must be one of the available values in the dropdown).

        :raises TimeoutException: If the row count dropdown is not present.
        :raises AssertionError: If unable to set the row count dropdown to the supplied row count.
        """
        self._pager.set_displayed_row_count(count_of_rows=desired_row_count)

    def set_filter_text(self, text: str) -> None:
        """
        Set the text filter to contain some text.

        :param text: The text you want to supply to the filter of the Table.

        :raises TimeoutException: If the filter input is not present.
        :raises AssertionError: If the supplied text is not successfully applied to the filter.
        """
        self._filter.set_filter_text(text=text)

    def set_cell_data_by_row_index_column_id(
            self, row_index: int, column_id: str, text: str, commit_value: bool) -> None:
        """
        Set the data of a cell in the table specified by the given parameters.

        :param row_index: The zero-based index of the row where the cell data will be set.
        :param column_id: The CASE-SENSITIVE id of the column where the cell data will be set.
            Note that the id may not be the name of the column as the id is a direct mapping against the keys of the
            data in use.
        :param text: The new data to be set in the specified cell.
        :param commit_value: A boolean flag indicating whether to commit changes immediately or not.
            If True, changes will be committed by pressing Enter after setting the cell data.
            If False, changes will not be committed, allowing for further modifications before committing.
        """
        self._body.set_cell_data_by_row_index_column_id(
            zero_based_row_index=row_index, column_id=column_id, text=text, commit_value=commit_value)

    def start_time_hours_input_is_enabled(self) -> bool:
        """
        Determine if the hours input of the start time is enabled.

        :returns: True, if the hours input of the start time is enabled - False otherwise.

        :raises TimeoutException: If the hours input is not present.
        """
        return self._filter_modal.start_time_hours_input_is_enabled()

    def start_time_minutes_input_is_enabled(self) -> bool:
        """
        Determine if the minutes input of the start time is enabled.

        :returns: True, if the minutes input of the start time is enabled - False otherwise.

        :raises TimeoutException: If the minutes input is not present.
        """
        return self._filter_modal.start_time_minutes_input_is_enabled()

    def start_time_seconds_input_is_enabled(self) -> bool:
        """
        Determine if the seconds input of the start time is enabled.

        :returns: True, if the seconds input of the start time is enabled - False otherwise.

        :raises TimeoutException: If the seconds input is not present.
        """
        return self._filter_modal.start_time_seconds_input_is_enabled()

    def subview_is_expanded(self, row_index: int) -> bool:
        """
        Determine if a subview is expanded for a given row. Only works properly in tables which have virtualization
        disabled, or if the row is already in view.

        :returns: True, if the row with the supplied index is displaying an expanded subview - False otherwise.

        :param row_index: The zero-based index of the row to check.
        """
        return self._body.subview_is_expanded(row_index=row_index)

    def wait_for_cell_to_have_text_by_row_index_column_id(
            self, zero_based_row_index: Union[int, str], column_id: str, text: str, timeout: float = 0):
        return self._body.wait_for_cell_to_have_text_by_row_index_column_id(
            zero_based_row_index=zero_based_row_index,
            column_id=column_id,
            text=text,
            timeout=timeout)
