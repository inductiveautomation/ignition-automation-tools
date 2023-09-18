from typing import Tuple, Union

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from Components.BasicComponent import ComponentPiece
from Pages.Perspective.View import View


class Widget(View):
    """
    "Widget" is a Perspective concept of a view which is used within the Dashboard component. It is essentially a
    View which contains multiple additional properties that allow for a user to identify the widget in a dropdown/list,
    as well as defining default drop size and minimum configuration sizes. These properties are set independently
    in each Dashboard, and so the values must either be kept in lock-step, or each new Dashboard must have its
    own Widgets.

    Due to the complex interactions between Widget and Dashboard, the Widget object needs to know about the Dashboard
    it belongs to.
    """
    # must use xpath here because the WIDGET uses xpath
    _HEADER_LOCATOR = (
        By.XPATH, '//div[contains(concat(" ",normalize-space(@class)," ")," dashboard-widget-head-title ")]')

    def __init__(
            self,
            driver: WebDriver,
            default_size: Tuple[int, int],
            min_size: Tuple[int, int],
            name: str,
            root_locator: Tuple[Union[By, str], str],
            category: str = None,
            header: str = None):
        """
        :param driver: The WebDriver in use for the browser window.
        :param default_size: A Tuple, where the 0th item represents the "width" of the Widget and the 1th item
            represents the "height" of the Widget.
        :param min_size: A Tuple, where the 0th item represents the minimum width of the Widget, and the 1th item
            represents the minimum height of the Widget.
        :param name: The name of the Widget as it will appear in the selection panel.
        :param root_locator: A locator which defines the `root` node of the widget.
        :param category: The category this Widget resides under in the selection panel.
        :param header: The header configured for this Widget, if so configured.
        """
        View.__init__(
            self,
            driver=driver,
            primary_locator=root_locator)

        """
        :param driver: The WebDriver in use by the browser window.
        :param default_size: A tuple where the 0th item represents the default column span (width) of the Widget, and
            the 1th item represents the default row span (height).
        :param min_size: A tuple where the 0th item represents the minimum configured column span of the Widget, and
            the 1th item represents the minimum configured row span of the Widget.
        :param name: The name of the Widget as it is expected to appear during selection.
        :param root_locator: The locator used to identify the root node of the View in use for this Widget.
        :param category: The category the Widget falls under during selection.
        :param header: The configured header of the Widget.
        """
        View.__init__(
            self,
            driver=driver,
            primary_locator=root_locator)
        self.default_column_span = default_size[0]
        self.default_row_span = default_size[1]
        self.min_column_span = min_size[0]
        self.min_row_span = min_size[1]
        self.category = category
        self.name = name
        self.header = header
        self._root = ComponentPiece(locator=root_locator, driver=driver)
        self._widget = ComponentPiece(
            locator=(By.XPATH, "/../.."), driver=driver, parent_locator_list=self._root.locator_list)
        self._widget_header = ComponentPiece(
            locator=self._HEADER_LOCATOR, driver=driver, parent_locator_list=self._widget.locator_list)

    def get_column_span(self) -> int:
        """
        Obtain a count of columns this widget spans.

        :returns: The number of columns this widget is currently spanning.

        :raises TimeoutException: If this widget is not present.
        """
        return self.get_next_available_cell_as_column_row()[0] - self.get_starting_column()

    def get_header_text(self) -> str:
        """
        Obtain the text of the header of the widget.

        :returns: The text of the header for this widget.

        :raises TimeoutException: If this widget is not present.
        """
        try:
            return self._widget_header.xfind().text
        except TimeoutException as toe:
            raise TimeoutException(
                msg="Unable to retrieve header text because the widget could not be located within "
                    "the Dashboard.") from toe

    def get_next_available_cell_as_column_row(self) -> Tuple[int, int]:
        """
        Obtain the next available cells based on the termination of this widget.

        If this widget is placed at (3,2), and spans two columns and two rows, you would expect a returned value of
        (5,4) because the widget occupies the 3rd and 4th columns, making the 5th column the next possibly available
        columns, and the 2nd and 3rd rows are occupied, so the 4th row is the next available row.

        :returns: A Tuple, where the 0th element is the next potentially available column after this widget, and the 1th
            element is the next potentially available row.

        :raises TimeoutException: If this widget is not present in the Dashboard.
        """
        try:
            arr_of_strs = self._widget.xfind().value_of_css_property(property_name="grid-area").split(" / ")[-2:]
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate widget within the Dashboard.") from toe
        ending_row = int(arr_of_strs[0])
        ending_col = int(arr_of_strs[1])
        return ending_col, ending_row  # (column, row) to retain (x, y)

    def get_row_span(self) -> int:
        """
        Obtain the count of rows this widget spans.

        :returns: The vertical count of rows this widget spans.

        :raises TimeoutException: If the widget is not present.
        """
        return self.get_next_available_cell_as_column_row()[1] - self.get_starting_row()

    def get_starting_column(self) -> int:
        """
        Obtain the one-based index of the column this widget originates in.

        :returns: The one-based index of the column in which this widget originates.

        :raises TimeoutException: If the widget is not present.
        """
        return self._get_origin_as_column_row()[0]

    def get_starting_row(self) -> int:
        """
        Obtain the one-based index of the row this widget originates in.

        :returns: The one-based index of the row in which this widget originates.

        :raises TimeoutException: If the widget is not present.
        """
        return self._get_origin_as_column_row()[1]

    def get_widget(self) -> WebElement:
        """
        Obtain the widget as a WebElement.

        :returns: The WebElement defined by the widget.

        :raises TimeoutException: If the widget is not present.
        """
        try:
            return self._widget.xfind()
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate Widget within the Dashboard.") from toe

    def has_header(self) -> bool:
        """
        Determine if this widget has a header.

        :returns: True, if this widget contains a header - False otherwise.
        """
        try:
            return self._widget_header.xfind() is not None
        except TimeoutException:
            return False

    def is_selected_during_edit_mode(self) -> bool:
        """
        Determine if this widget is selected during editing mode.

        :returns: True, if this widget is selected/active during editing mode - False otherwise.
        """
        try:
            return 'isEditing' in self._widget.xfind().get_attribute('class')
        except TimeoutException as toe:
            raise TimeoutException(
                msg="Unable to determine selection of widget as we could not locate the widget within the "
                    "Dashboard.") from toe

    def is_currently_placed_on_dashboard(self) -> bool:
        """
        Determine if this widget is currently displayed on the Dashboard.

        :returns: True, if this widget is currently displayed on the Dashboard, regardless of mode. False, if this
            widget is not displayed.
        """
        try:
            return self._root.xfind() is not None
        except TimeoutException:
            return False

    def select_during_edit_mode(self) -> None:
        """
        Select this widget while the Dashboard is in editing mode.

        :raises TimeoutException: If this widget is not currently placed, or the Dashboard is not in editing mode.
        """
        if not self.is_selected_during_edit_mode():
            self._widget.xfind().click()

    def _get_origin_as_column_row(self) -> Tuple[int, int]:
        """
        Obtain the column:row indices of this widget's origin cell.

        :returns: A Tuple, where the 0th element id the one-based column index of the cell this widget originates in,
            and the 1th element is the one-based row index the widget originates in.

        :raises TimeoutException: If the widget is not currently placed.
        """
        try:
            column = int(self._widget.xfind().get_attribute('data-column'))
            row = int(self._widget.xfind().get_attribute('data-row'))
            return column, row
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate widget within the Dashboard.") from toe
