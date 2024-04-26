from typing import List, Tuple
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece
from Components.PerspectiveComponents.Common.TablePieces.Body import Body
from Components.PerspectiveComponents.Common.TablePieces.HeaderAndFooter import Header
from Helpers.Point import Point


class Table(ComponentPiece):
    """A Common Table Component, containing ONLY content which would be found in ALL the following components:

    - Table
    - Alarm Journal Table
    - Alarm Status Table
    - Power Chart
    """

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List] = None,
            wait_timeout: float = 10,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._body = Body(driver=driver, parent_locator_list=self.locator_list, poll_freq=poll_freq)
        self._header = Header(driver=driver, parent_locator_list=self.locator_list, poll_freq=poll_freq)

    def descending_sort_order_is_active_for_column(self, column_id: str) -> bool:
        """
        Determine if the column is displaying in descending order.

        :returns: True, if the column is currently sorted in descending order - False otherwise.

        :raises TimeoutException: If no header is present.
        """
        return self._header.descending_sort_is_active(column_id=column_id)

    def get_cell_data_by_column_index(self, row_index: int, column_index: int) -> str:
        """
        Obtain the data of a specific cell within the Table.

        :param row_index: The zero-based index of the row the cell belongs to.
        :param column_index: The zero-based index of the column the cell belongs to.

        :returns: The data of the specified cell, as a string.

        :raises TimeoutException: If no rows are displayed within the Table, or if the supplied indexes are invalid
            based on the data of the Table.
        """
        return self._body.get_cell_data_by_row_index_column_index(
            zero_based_row_index=row_index, zero_based_column_index=column_index)

    def get_cell_data_by_column_id(self, row_index: int, column_id: str) -> str:
        """
        Obtain the data of a specific cell within the Table.

        :param row_index: The zero-based index of the row the cell belongs to.
        :param column_id: The id of the column the cell belongs to. Note that column ids are direct mappings to the
            keys of the data of the Table, and may not match the name of the column.

        :returns: The data of the specified cell, as a string.

        :raises TimeoutException: If no rows are displayed within the Table, or if the supplied index/id values are
            invalid based on the data of the Table.
        """
        return self._body.get_cell_data_by_row_index_column_id(
            zero_based_row_index=row_index, column_id=column_id)

    def get_cell_origin(self, row_index: int, column_index: int) -> Point:
        """
        Obtain a two-dimensional point in space which represents the top-left corner of the cell.

        :param row_index: The zero-based index of the row the cell belongs to.
        :param column_index: The zero-based index of the column the cell belongs to.

        :returns: The top-left corner of the cell as a two-dimensional point.

        :raises TimeoutException: If no rows are displayed within the Table, or if the supplied indexes are invalid
            based on the data of the Table.
        """
        return self._body.get_cell_origin(zero_based_row_index=row_index, zero_based_column_index=column_index)

    def get_cell_termination(self, row_index: int, column_index: int) -> Point:
        """
        Obtain a two-dimensional point in space which represents the bottom-right corner of the cell.

        :param row_index: The zero-based index of the row the cell belongs to.
        :param column_index: The zero-based index of the column the cell belongs to.

        :returns: The bottom-right corner of the cell as a two-dimensional point.

        :raises TimeoutException: If no rows are displayed within the Table, or if the supplied indexes are invalid
            based on the data of the Table.
        """
        return self._body.get_cell_termination(
            zero_based_row_index=row_index, zero_based_column_index=column_index)

    def get_column_count_from_body(self) -> int:
        """
        Obtain a count of columns from the BODY of the Table.

        :raises TimeoutException: If no rows are present in the body of the Table.
        """
        return self._body.get_column_count()

    def get_column_count_from_header(self) -> int:
        """
        Obtain a count of columns from the HEADER of the Table.

        :raises TimeoutException: If no columns are present in the header of the Table.
        """
        return self._header.get_count_of_columns()

    def get_column_index(self, column_id: str) -> int:
        """
        Obtain the index of a column, based on its id.

        :param column_id: The id of the column. Note that column ids are direct mappings to the keys of the data of the
            Table, and may not match the name of the column.

        :raises TimeoutException: If no column exists with the supplied id.
        """
        return self._header.get_column_index(
            column_id=column_id)

    def get_column_names_from_header(self) -> List[str]:
        """
        Obtain the column names displayed in the Header.

        :returns: All currently displayed column names from the header. Note that column names are not the same as
            column ids.

        :raises TimeoutException: If no header is present, or if no rows are displayed in the Table.
        """
        return self._header.get_column_names()

    def get_column_width(self, column_id: str, include_units: bool = False) -> str:
        """
        Obtain the width of a column.

        :param column_id: The id of the column from which you'd like the width.
        :param include_units: Dictates whether the returned value should include units of measurement (almost always
            'px').

        :returns: The width of the column as a string.

        :raises TimeoutException: If no header is present, or if no rows are displayed, or if no column exists with the
            supplied id.
        """
        return self._header.get_column_width(
            column_id=column_id, include_units=include_units)

    def get_column_max_width(self, column_id: str, include_units: bool = False) -> str:
        """
        Obtain the maximum width allowed to a column.

        :param column_id: The id of the column from which you'd like the max-width value.
        :param include_units: Dictates whether the returned value should include units of measurement (almost always
            'px').

        :raises TimeoutException: If no header is present, or if no rows are displayed, or if no column exists with the
            supplied id.
        """
        return self._header.get_column_max_width(
            column_id=column_id, include_units=include_units)

    def get_computed_height_of_body(self, include_units: bool = False) -> str:
        """
        Get the computed height of the component. Must return as a string because of the possibility of included units.

        :param include_units: Include the units of height (typically "px") if True, otherwise return only the numeric
        value (as a str).

        :returns: The height of the body of the Table as a string. May contain units based on include_units kwarg.

        :raises TimeoutException: If the component is not found in the DOM.
        """
        return self._body.get_computed_height(include_units=include_units)

    def get_count_of_header_columns(self) -> int:
        """Obtain a count of columns form the header."""
        return self._header.get_count_of_columns()

    def get_count_of_row_groups(self) -> int:
        """
        Obtain a count of row groups. Row groups are distinct from rows, in that row GROUPS can contain multiple rows
        and potentially subviews. They are a way of grouping row content which belongs together into one container.

        :returns: A numeric count of row groups currently displayed within the Table.
        """
        return self._body.get_row_group_count()

    def get_count_of_rows(
            self, include_expanded_subviews_in_count: bool = False) -> int:
        """
        Obtain a count of rows currently displayed in the Table.

        :param include_expanded_subviews_in_count: If True, subviews which are currently expanded will be counted as a
            row. If False, subviews will not be included in the returned count.

        :returns: A numeric count of rows currently displayed in the Table. This count may optionally contain expanded
            subviews.
        """
        return self._body.get_row_count(
            include_expanded_subviews_in_count=include_expanded_subviews_in_count)

    def get_empty_message_text(self) -> str:
        """
        Obtain the text of the message which is clarifying the Table contains no data.

        :returns: The text of the message displayed in the Table which informs users there is no data.

        :raises TimeoutException: If the Table is not currently informing the user there is no data.
        """
        return self._body.get_empty_message_text()

    def get_origin_of_column_in_header(self, column_index: int) -> Point:
        """
        Obtain the origin of a column in the Header.

        :param column_index: The zero-based index of the column.

        :returns: A two-dimensional point which represents the top-left corner of a cell in the Header.

        :raises TimeoutException: If no header is present, or if the Table contains no data.
        """
        return self._header.get_origin_of_column(column_index=column_index)

    def get_row_data(self, row_index: int) -> dict:
        """
        Obtain the data from all cells in a row.

        :param row_index: The zero-based index of the row from which you would like data.

        :returns: The data of a row as a dictionary, where the keys of the dictionary match the keys of the underlying
            data (column ids - not names).

        :raises TimeoutException: If no row exists with the supplied index.
        """
        return self._body.get_row_data_by_row_index(zero_based_row_index=row_index)

    def get_row_data_by_column_value(self, column_id: str, known_value: str) -> List[dict]:
        """
        Obtain the data from all cells in all rows which contain some known value within a column.

        :param column_id: The id of the column which contains your known value.
        :param known_value: A value in the supplied column which identifies the corresponding row as the target.

        :returns: The data of all rows which contains the known_value as a value in the column specified by the
            supplied column_id.

        :raises TimeoutException: If no rows are displayed in the Table.
        :raises KeyError: If no column exists with the supplied id.
        """
        return self._body.get_row_data_by_column_value(column_id=column_id, column_value=known_value)

    def get_row_width(self, include_units: bool = False) -> str:
        """
        Obtain the width of rows within the Table.

        :param include_units: Dictates whether the returned value should include units of measurement.

        :returns: The width of the rows of the Table as a string.

        :raises TimeoutException: If no rows are displayed in the Table.
        """
        return self._body.get_row_width(include_units=include_units)

    def get_row_index_of_first_row_with_value_in_column(self, column_id: str, known_value: str) -> Optional[int]:
        """
        Obtain the index of the row which contains a supplied value in a specified column.

        :param column_id: The id of the column which contains the known value.
        :param known_value: A value which identifies which row of the Table we would like the index from.

        :returns: The zero-based index of the first row which contains the supplied value within the specified column,
            or None if no row contains the supplied value in the specified column.

        :raises TimeoutException: If no rows are displayed in the Table
        """
        return self._body.get_row_index_of_first_row_with_value_in_column(
            column_id_with_known_value=column_id, known_value=known_value)

    def get_sort_order_number_of_column(self, column_id: str) -> Optional[int]:
        """
        Obtain the sort order of a column, if it has one.

        :param column_id: The id of the column which we want to sort order of.

        :returns: The sort order of the specified column, or None if the column is not sorted or is the only sorted
            column.
        """
        return self._header.get_sort_order_number_of_column(column_id=column_id)

    def get_termination_of_column_in_header(self, column_index: int) -> Point:
        """
        Obtain a two-dimensional point which represents the bottom-right of a cell in the Header.

        :param column_index: The zero-based index of the column.

        :returns: A two-dimensional point which represents the bottom-right corner of a cell in the Header.

        :raises TimeoutException: If no column exists with the supplied index, or if the Table contains no data.
        """
        return self._header.get_termination_of_column(column_index=column_index)

    def header_is_present(self) -> bool:
        """
        Determine if the Header is currently displayed within the Table.

        :returns: True, if the Header is currently displayed - False otherwise.
        """
        return self._header.header_is_present()

    def hover_over_column_header(self, column_index: int) -> None:
        """
        Hover over the header cell of a column.

        :param column_index: The zero-based index of the column for which you would like to hover over the Header cell.

        :raises TimeoutException: If no column exists with the supplied index, or if the Table contains no data.
        """
        self._header.hover_over_column_in_header(column_index=column_index)
