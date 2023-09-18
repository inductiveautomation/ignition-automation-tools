from typing import Tuple, List, Optional

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece


class Column(BasicPerspectiveComponent):
    """A Perspective Column Container."""
    _ROW_CONTAINER_LOCATOR = (By.CSS_SELECTOR, "div.inner-container")
    _ROW_LOCATOR = (By.CSS_SELECTOR, f"{_ROW_CONTAINER_LOCATOR[1]} > div.row")

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 5,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._rows = ComponentPiece(
            locator=self._ROW_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=2,
            poll_freq=poll_freq)
        self._indexed_rows_dict = {}

    def element_with_locator_is_in_row_by_index(
            self, element_locator: Tuple[By, str], zero_based_row_index: int) -> bool:
        """
        Determine if the supplied locator exists within a specified row.

        :param element_locator: The Tuple locator of the element to search for in the specified row.
        :param zero_based_row_index: The zero-based index of the row we will search for the provided locator.

        :returns: True, if the supplied locator is found within the specified row - False otherwise.
        """
        try:
            return self._get_row_by_index(index=zero_based_row_index).find().find_element(*element_locator) is not None
        except NoSuchElementException:
            return False
        except TimeoutException:
            return False

    def get_count_of_web_elements_in_row_by_locator(self, zero_based_row_index: int, locator: Tuple[By, str]) -> int:
        """
        Obtain a count of the number of instances which match the supplied locator within a specified row.

        :param zero_based_row_index: The zero-based index of the row within which we will search for the supplied
            locator.
        :param locator: The Tuple locator we will search for within the specified row.

        :returns: The number of times the supplied locator is found within the specified row.

        :raises TimeoutException: If the supplied row index is not present.
        """
        try:
            # allow TimeoutException to be raised if row does not exist.
            return len(self._get_row_by_index(index=zero_based_row_index).find().find_elements(*locator))
        except NoSuchElementException:
            # return 0 if no element with locator is found.
            return 0

    def get_row_of_component_by_locator(self, element_locator: Tuple[By, str]) -> Optional[int]:
        """
        Obtain the row index of the row which contains the supplied locator.

        :param element_locator: The Tuple locator which describes an element located within the Column Container.

        :returns: The zero-based index of the row which contains the supplied locator, or None if no row contains the
            locator.
        """
        for row in self._rows.find_all():
            try:
                if row.find_element(*element_locator) is not None:
                    return int(row.get_attribute("data-row-index"))
            except NoSuchElementException:
                pass
        return None

    def _get_row_by_index(self, index: int) -> ComponentPiece:
        """
        Obtain a Component Piece which defines a singular row within the Column Container.

        :returns: A ComponentPiece which defines a singular row within the Column Container.
        """
        row = self._indexed_rows_dict.get(index)
        if not row:
            row = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'{self._ROW_CONTAINER_LOCATOR[1]} div[data-row-index="{index}"]'),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                wait_timeout=2,
                poll_freq=self.poll_freq)
            self._indexed_rows_dict[index] = row
        return row
