from typing import Optional, List, Tuple, Union

from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece
from Helpers.IAExpectedConditions import IAExpectedConditions as IAec
from Helpers.Point import Point


class Body(ComponentPiece):
    """The body of a table, which contains information and interactions for rows and cells."""
    BODY_CELL_CSS = 'div.tc'
    BODY_ROW_CSS = 'div.ia_table__body__row'
    ROW_GROUP_CSS = 'div.tr-group'
    _EMPTY_MESSAGE_LOCATOR = (By.CSS_SELECTOR, 'div.emptyMessage')

    def __init__(
            self,
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 10,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=(By.CSS_SELECTOR, "div.tb"),
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._empty_message = ComponentPiece(
            locator=self._EMPTY_MESSAGE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._row_groups = ComponentPiece(
            locator=(By.CSS_SELECTOR, self.ROW_GROUP_CSS),
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._rows = ComponentPiece(
            locator=(By.CSS_SELECTOR, self.BODY_ROW_CSS),
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._cells = ComponentPiece(
            locator=(By.CSS_SELECTOR, self.BODY_CELL_CSS),
            driver=driver,
            parent_locator_list=self._rows.locator_list,
            poll_freq=poll_freq)

    def get_cell_data_by_row_index_column_index(
            self,
            zero_based_row_index: Union[int, str],
            zero_based_column_index: Union[int, str]) -> str:
        """
        Get the String data of a cell specified by a zero-based row index and a zero-based column index.

        :param zero_based_row_index: The zero-based index of the row you are targeting.
        :param zero_based_column_index: The zero-based index of the column you are targeting.

        :returns: The displayed contents of the specified cell.

        :raises TimeoutException: If no cell exists with the provided indices.
        """
        _locator = (By.CSS_SELECTOR, f'{self.ROW_GROUP_CSS}[data-row-index="{zero_based_row_index}"] '
                                     f'{self.BODY_ROW_CSS} '
                                     f'{self.BODY_CELL_CSS}[data-column-index="{zero_based_column_index}"]')
        return ComponentPiece(
            locator=_locator,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=self.poll_freq).get_text()

    def get_cell_data_by_row_index_column_id(self, zero_based_row_index: Union[int, str], column_id: str) -> str:
        """
        Get the String data of a cell specified by a zero-based row index and a CASE-SENSITIVE column name.

        :param zero_based_row_index: The zero-based index of the row you are targeting.
        :param column_id: The CASE-SENSITIVE id of the column you are targeting. Note that the id may not be the name
            of the column as the id is a direct mapping against the keys of the data in use.

        :returns: The displayed contents of the specified cell.

        :raises TimeoutException: If no cell exists with the provided row index in the supplied column.
        """
        _locator = (By.CSS_SELECTOR, f'{self.ROW_GROUP_CSS}[data-row-index="{zero_based_row_index}"] '
                                     f'{self.BODY_ROW_CSS} {self.BODY_CELL_CSS}[data-column-id="{column_id}"]')
        return ComponentPiece(
            locator=_locator,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=self.poll_freq).get_text()

    def get_cell_origin(self, zero_based_row_index: int, zero_based_column_index: int) -> Point:
        """
        Obtain the origin (top-left corner) position of a cell.

        :param zero_based_row_index: The zero-based index of the row you are targeting.
        :param zero_based_column_index: The zero-based index of the column you are targeting.

        :returns: A two-dimensional point in the DOM which represents the top-left corner of the cell.

        :raises TimeoutException: If no cell exists with the provided indices.
        """
        _locator = (By.CSS_SELECTOR, f'{self.ROW_GROUP_CSS}[data-row-index="{zero_based_row_index}"] '
                                     f'{self.BODY_ROW_CSS} {self.BODY_CELL_CSS}'
                                     f'[data-column-index="{zero_based_column_index}"]')
        return ComponentPiece(
            locator=_locator,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=self.poll_freq).get_origin()

    def get_cell_termination(self, zero_based_row_index: int, zero_based_column_index: int) -> Point:
        """
        Obtain the termination (bottom-right corner) position of a cell.

        :param zero_based_row_index: The zero-based index of the row you are targeting.
        :param zero_based_column_index: The zero-based index of the column you are targeting.

        :returns: A two-dimensional point in the DOM which represents the bottom-right corner of the cell.

        :raises TimeoutException: If no cell exists with the provided indices.
        """
        _locator = (By.CSS_SELECTOR, f'{self.ROW_GROUP_CSS}[data-row-index="{zero_based_row_index}"] '
                                     f'{self.BODY_ROW_CSS} {self.BODY_CELL_CSS}'
                                     f'[data-column-index="{zero_based_column_index}"]')
        return ComponentPiece(
            locator=_locator,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=self.poll_freq).get_termination()

    def get_column_count(self) -> int:
        """
        Obtain the count of cells in the first row of the body of the Table.

        :returns: The count of cells in the first row of the Table.

        :raises TimeoutException: If no first row is present in the Table.
        """
        _locator = (By.CSS_SELECTOR, f'{self.ROW_GROUP_CSS}[data-row-index="0"] '
                                     f'{self.BODY_ROW_CSS} {self.BODY_CELL_CSS}')
        return len(ComponentPiece(
            locator=_locator,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=self.poll_freq).find_all())

    def get_column_width(self, column_name: str, include_units: bool = False) -> str:
        """
        Obtain the width of a column.

        :param column_name: The name of the column of which we are retrieving the width.
        :param include_units: A value of True specifies we should include the units of measurement (almost always
            'px'), while a value of False specifies we should return only the numeric value (as a string).

        :returns: The width of the specified column as a string, because it might have units attached.

        :raises TimeoutException: If the specified column does not exist, or if the Table has no rows displayed.
        """
        _locator = (By.CSS_SELECTOR, f'{self.ROW_GROUP_CSS}[data-row-index="0"] '
                                     f'{self.BODY_ROW_CSS} {self.BODY_CELL_CSS}[data-row-id="{column_name}"')
        return ComponentPiece(
            locator=_locator,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=self.poll_freq).get_computed_width(include_units=include_units)

    def get_empty_message_text(self) -> str:
        """
        Obtain the message displayed while the table has no content.

        :raises TimeoutException: If no empty message is found, most likely because the Table has content.
        """
        return self._empty_message.get_text().strip()

    def get_height_of_row_by_index(self, zero_based_row_index: int, include_units: bool = False) -> str:
        """
        Obtain the height of a row.

        :param zero_based_row_index: The zero-based index of the row you are targeting.
        :param include_units: A value of True specifies we should include the units of measurement (almost always
            'px'), while a value of False specifies we should return only the numeric value (as a string).

        :returns: The height of the specified row as a string, because it might have units attached.

        :raises TimeoutException: If the specified row index does not exist.
        """
        _locator = (By.CSS_SELECTOR, f'{self.ROW_GROUP_CSS}[data-row-index="{zero_based_row_index}"] '
                                     f'{self.BODY_ROW_CSS}')
        return ComponentPiece(
            locator=_locator,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=self.poll_freq).get_computed_height(include_units=include_units)

    def get_row_index_of_first_row_with_value_in_column(
            self, column_id_with_known_value: str, known_value: str) -> Optional[int]:
        """
        Obtain the index of the first row which contains s specified value in a know column.

        :param column_id_with_known_value: The case-sensitive column ID which of the column that you want to search.
            Note that this may not always be the name of the column, as this attribute is mapped to the data key which
            drives the column.
        :param known_value: The case-sensitive value you are searching for within the column.

        :returns: The zero-based index of the first row which contains the specified known_value in the specified
            column, or None if no row contained the value.
        """
        _locator = (By.CSS_SELECTOR, f'{self.BODY_CELL_CSS}[data-column-id="{column_id_with_known_value}"]')
        _cells = ComponentPiece(
            locator=_locator,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=self.poll_freq).find_all()
        for cell in _cells:
            if cell.text == str(known_value):
                return int(cell.get_attribute("data-row-index"))
        return None

    def get_row_count(
            self, include_expanded_subviews_in_count: bool = False, expected_count: Optional[int] = None) -> int:
        """
        Obtain a count of rows in the Table.

        :param include_expanded_subviews_in_count: A True value will include any expanded subviews as a row, while a
            value of False will only return a count of rows which reflects the native data.
        :param expected_count: If supplied, the function will wait some short period of time until this number of rows
            appears.

        :returns: A count of rows in the table, or possibly a count of rows which includes expanded subviews.
        """
        try:
            return int(self.wait.until(IAec.function_returns_true(
                custom_function=self._get_row_count,
                function_args={
                    "include_expanded_subviews_in_count": include_expanded_subviews_in_count,
                    "expected_count": expected_count
                }
            )))
        except TimeoutException:
            return 0

    def _get_row_count(self, include_expanded_subviews_in_count: bool, expected_count: Optional[int]) -> int:
        """
        Obtain a count of rows in the Table.

        :param include_expanded_subviews_in_count: If True, we will include expanded subviews as part of the row count.
            If False, expanded subviews will be omitted from the count, making the returned value a true reflection of
            the underlying data.
        :param expected_count: A count we expect the Table to have, and we will wait on reporting until this value is
            found, or some period of time has elapsed.
        """
        try:
            rows = self._rows.find_all(wait_timeout=1)
            if not include_expanded_subviews_in_count:
                rows = [row for row in rows if "subview" not in row.get_attribute("class")]
            if expected_count is not None:
                expected_count = int(expected_count)
                if len(rows) == expected_count:
                    return expected_count
                else:
                    return False
            return len(rows)
        except StaleElementReferenceException:
            return False
        except TimeoutException:
            return False

    def get_row_data_by_row_index(self, zero_based_row_index: int) -> dict:
        """
        Obtain the data of a specified row and return that data as a dictionary, where the keys of the dictionary
        are the column ids.

        :param zero_based_row_index: The zero-based index of the row you are targeting.

        :returns: The row data as a dictionary, with the keys of the dictionary being the case-sensitive
            ids of the columns.
        """
        _locator = (By.CSS_SELECTOR, f'{self.ROW_GROUP_CSS}[data-row-index="{zero_based_row_index}"] '
                                     f'{self.BODY_ROW_CSS} {self.BODY_CELL_CSS}')
        cell_web_element_list = ComponentPiece(
            locator=_locator,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=self.poll_freq).find_all()
        row_data_as_dictionary = {}
        for cell in cell_web_element_list:
            row_data_as_dictionary[cell.get_attribute('data-column-id')] = cell.text
        row_data_as_dictionary.pop('expandSubview', None)  # remove the expandSubview column from the dict
        return row_data_as_dictionary

    def get_row_data_by_column_value(self, column_value: str, column_id: str) -> List[dict]:
        """
        Obtain the row data for all rows which contain a known value in a specified column.

        :param column_value: The known value within a column which will be used to determine what rows are returned.
        :param column_id: The id of the column you expect to contain the supplied value.

        :returns: The row data for every row which contains the supplied value in the specified column.

        :raises TimeoutException: If no rows are found.
        :raises KeyError: If the supplied column_id value does not match any displayed column.
        """
        rows_with_column_value = []
        for i in range(self.get_row_count()):
            row_dict = self.get_row_data_by_row_index(zero_based_row_index=i)
            if row_dict[column_id] == str(column_value):
                rows_with_column_value.append(row_dict)
        return rows_with_column_value

    def get_row_group_count(self) -> int:
        """
        Obtain the count of row groups present in the table

        :returns: int - The count of row groups.
        """
        try:
            return len(self._row_groups.find_all())
        except TimeoutException:
            return 0

    def get_row_width(self, include_units: bool = False) -> str:
        """
        Obtain the width of a row.

        :param include_units: If True, the returned value will include the units (almost always 'px'). If False, the
            returned value will be the numeric representation as a string.

        :raises TimeoutException: If no rows are present in the Table.
        """
        return self._rows.get_computed_width(include_units=include_units)
