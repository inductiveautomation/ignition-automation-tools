from typing import List, Optional, Tuple

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Components.Common.Button import CommonButton
from Components.PerspectiveComponents.Common.ComponentModal import ComponentModal
from Helpers.IAAssert import IAAssert
from Helpers.IASelenium import IASelenium
from Helpers.Point import Point
from Pages.Perspective.Widget import Widget


class Dashboard(BasicPerspectiveComponent):
    """
    A Perspective Dashboard Component.

    The Dashboard requires specialized information about its internal widgets in order to perform some interactions.
    """
    _GRID_LOCATOR = (By.CSS_SELECTOR, 'div.gridCommon__grid')
    _GRID_CELL_LOCATOR = (By.CSS_SELECTOR, 'div.grid-cell.dashboard-cell')
    _EDIT_TOGGLE_LOCATOR = (By.CSS_SELECTOR, 'div.dashboard-run-edit-toggle')
    _ADD_OR_REMOVE_CANCEL_LOCATOR = (By.CSS_SELECTOR, f'button.{CommonButton.SECONDARY_CLASS}')
    _ADD_OR_REMOVE_CONFIRM_LOCATOR = (By.CSS_SELECTOR, f'button.{CommonButton.PRIMARY_CLASS}')
    _REMOVE_WIDGET_MODAL_LOCATOR = (By.CSS_SELECTOR, 'div.removeWidgetModalContent')
    _ADD_WIDGET_MODAL_LOCATOR = (By.CSS_SELECTOR, 'div.addWidgetsModalContent')
    _ADD_WIDGET_MODAL_CATEGORY_LOCATOR = (By.CSS_SELECTOR, 'div.addWidgetCategory')  # TitleBar
    _ADD_WIDGET_MODAL_TITLE_LOCATOR = (By.CSS_SELECTOR, 'div.widgetMenuItemTitle')
    _WIDGET_LOCATOR = (By.CSS_SELECTOR, 'div.dashboard-widget')
    _DELETE_LOCATOR = (By.CSS_SELECTOR, 'div.widget-control-delete')
    _EAST_RESIZE_HANDLE_LOCATOR = (By.CSS_SELECTOR, 'div.widget-resize-handle.east div')
    _NORTH_RESIZE_HANDLE_LOCATOR = (By.CSS_SELECTOR, 'div.widget-resize-handle.north div')
    _SOUTH_RESIZE_HANDLE_LOCATOR = (By.CSS_SELECTOR, 'div.widget-resize-handle.south div')
    _WEST_RESIZE_HANDLE_LOCATOR = (By.CSS_SELECTOR, 'div.widget-resize-handle.west div')

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
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
        self._grid = ComponentPiece(
            locator=self._GRID_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._grid_cell = ComponentPiece(
            locator=self._GRID_CELL_LOCATOR,
            driver=driver,
            parent_locator_list=self._grid.locator_list,
            poll_freq=poll_freq)
        self._edit_toggle = ComponentPiece(
            locator=self._EDIT_TOGGLE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._shared_modal = ComponentModal(driver=driver, wait_timeout=2, poll_freq=poll_freq)
        self._add_remove_cancel_button = CommonButton(
            locator=self._ADD_OR_REMOVE_CANCEL_LOCATOR,
            driver=driver,
            parent_locator_list=self._shared_modal.locator_list,
            poll_freq=poll_freq)
        self._add_remove_confirm_button = CommonButton(
            locator=self._ADD_OR_REMOVE_CONFIRM_LOCATOR,
            driver=driver,
            parent_locator_list=self._shared_modal.locator_list,
            poll_freq=poll_freq)
        self._remove_widget_modal = ComponentPiece(
            locator=self._REMOVE_WIDGET_MODAL_LOCATOR,
            driver=driver,
            parent_locator_list=self._shared_modal.locator_list,
            wait_timeout=2,
            poll_freq=poll_freq)
        self._add_widget_modal = ComponentPiece(
            locator=self._ADD_WIDGET_MODAL_LOCATOR,
            driver=driver,
            parent_locator_list=self._shared_modal.locator_list,
            wait_timeout=2,
            poll_freq=poll_freq)
        self._add_widget_categories = ComponentPiece(
            locator=self._ADD_WIDGET_MODAL_CATEGORY_LOCATOR,
            driver=driver,
            parent_locator_list=self._add_widget_modal.locator_list,
            wait_timeout=2,
            poll_freq=poll_freq)
        self._add_widget_modal_title = ComponentPiece(
            locator=self._ADD_WIDGET_MODAL_TITLE_LOCATOR,
            driver=driver,
            parent_locator_list=self._add_widget_modal.locator_list,
            poll_freq=poll_freq)
        self._widget = ComponentPiece(
            locator=self._WIDGET_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=2,
            poll_freq=poll_freq)
        self._delete_widget = ComponentPiece(
            locator=self._DELETE_LOCATOR,
            driver=driver,
            parent_locator_list=self._widget.locator_list,
            poll_freq=poll_freq)
        self._grid_cell_collection = {}
        self._east_resize_handle = ComponentPiece(
            locator=self._EAST_RESIZE_HANDLE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._north_resize_handle = ComponentPiece(
            locator=self._NORTH_RESIZE_HANDLE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._south_resize_handle = ComponentPiece(
            locator=self._SOUTH_RESIZE_HANDLE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._west_resize_handle = ComponentPiece(
            locator=self._WEST_RESIZE_HANDLE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)

    def add_button_is_enabled(self) -> bool:
        """
        Determine if the Add button in the "Add Widget" modal is enabled.

        :returns: True, if the "add" button within the "Add Widget" modal is enabled - False otherwise.

        :raises TimeoutException: If the "Add Widget" modal is not present.
        """
        try:
            return self._add_remove_confirm_button.find().is_enabled()
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate the 'Add' button in the Add Widget modal.") from toe

    def add_widget_modal_is_displayed(self) -> bool:
        """
        Determine if the 'Add Widget' modal is currently displayed.

        :returns: True, if the Add Widget modal is displayed - False otherwise.
        """
        try:
            return self._add_widget_modal.find().is_displayed()
        except TimeoutException:
            return False

    def any_modal_is_displayed(self) -> bool:
        """
        Determine if ANY modal is displayed within the Dashboard.

        :returns: True, if any modal is currently visible within the Dashboard.
        """
        try:
            return self._shared_modal.find() is not None
        except TimeoutException:
            return False

    def cancel_modal(self) -> None:
        """
        Close any displayed modal by clicking the "Cancel" button.

        :raises TimeoutException: If the "Cancel" button is not present.
        """
        try:
            self._add_remove_cancel_button.click()
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate the 'Cancel' button in the modal.") from toe

    def category_is_expanded(self, category: str) -> bool:
        """
        Determine if a category within the "Add Widget" modal is expanded.

        :param category: The name of the category to check for expansion.

        :returns: True, if the supplied category is expanded - False otherwise.

        :raises IndexError: If no category is present with the supplied case-sensitive name.
        :raises TimeoutException: If no categories are found at all.
        """
        clazz = self._get_category(category=category).find_element(*(By.TAG_NAME, "div")).get_attribute("class")
        return "expanded" in clazz

    def click_add_button(self) -> None:
        """
        Click the "Add" button within the "Add Widget" modal.

        :raises TimeoutException: If the "Add Widget" modal is not present.
        """
        try:
            self._add_remove_confirm_button.click()
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate the 'Add' button in the Add Widget modal.") from toe

    def click_edit_toggle(self) -> None:
        """
        Click the edit toggle, regardless of current state.

        :raises TimeoutException: If the edit toggle is not present.
        """
        try:
            self.hover()
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate a Dashboard with the defined locator.") from toe
        try:
            self._edit_toggle.hover()
            self._edit_toggle.wait_on_binding(time_to_wait=1)
            self._edit_toggle.click(binding_wait_time=1)
        except TimeoutException as toe:
            raise TimeoutException(
                msg="The edit toggle of the Dashboard was not present. Make sure the toggle is turned on "
                    "in props.") from toe

    def click_grid_cell(self, one_based_column_index: int, one_based_row_index: int) -> None:
        """
        Click a cell within the grid of the Dashboard during editing.

        :param one_based_column_index: The one-based index of the column to target.
        :param one_based_row_index: The one-based index of the row to target.

        :raises TimeoutException: If the supplied indices do not define a cell which is present.
        """
        # firefox reasons
        try:
            IASelenium(driver=self.driver).simple_click(
                web_element=self._get_grid_cell(
                    one_based_column_index=one_based_column_index, one_based_row_index=one_based_row_index).find())
        except TimeoutException as toe:
            raise TimeoutException(
                msg="Unable to locate a grid cell with the supplied indices in the Dashboard.") from toe

    def click_widget_name(self, widget_name: str) -> None:
        """
        Click a widget in the "Add Widget" modal.

        :param widget_name: The case-sensitive name of the widget to click.

        :raises IndexError: If no widget exists with the supplied name.
        :raises TimeoutException: If the "Add Widget" modal is not present.
        """
        try:
            list(filter(lambda e: e.text == widget_name, self._add_widget_modal_title.find_all()))[0].click()
        except IndexError as ie:
            raise IndexError(f"No widget found with a name of '{widget_name}'.") from ie
        except TimeoutException as toe:
            raise TimeoutException("No widgets found at all in the Add Widget modal.") from toe

    def collapse_category(self, category: str) -> None:
        """
        Collapse a category within the "Add Widget" modal.

        :param category: The case-sensitive name of the category to collapse.

        :raises IndexError: If no category exists with the supplied name.
        :raises TimeoutException: If no categories exist at all.
        """
        if self.category_is_expanded(category=category):
            self._get_category(category=category).click()
        IAAssert.is_not_true(
            value=self.category_is_expanded(category=category),
            failure_msg=f"Failed to collapse the '{category}' category.")

    def confirm_remove_widget(self, binding_wait_time: int = 1) -> None:
        """
        Click the "Confirm" button visible while attempting to remove a widget from the Dashboard.

        :param binding_wait_time: How long to wait (in seconds) after clicking before allowing code to continue.

        :raises TimeoutException: If the "Confirm" button is not present.
        """
        try:
            self._add_remove_confirm_button.click(binding_wait_time=binding_wait_time)
        except TimeoutException as toe:
            raise TimeoutException(
                msg="Unable to locate the 'Remove' button in the confirmation modal while deleting a widget.") from toe

    def dashboard_is_in_editing_mode(self) -> bool:
        """
        Determine if the Dashboard is currently in "editing" mode.

        :returns: True, while a user may edit widget layout - False otherwise.
        """
        try:
            return "isEditing" in self.find().get_attribute("class")
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate a Dashboard component with the supplied locator.") from toe

    def delete_active_widget(self) -> None:
        """
        Go through the deletion process for the currently selected widget.

        :raises TimeoutException: If the Dashboard is not in editing mode, or if no widget is selected/active.
        """
        self._delete_active_widget()

    def delete_all_widgets(self) -> None:
        """
        Delete all widgets currently placed in the Dashboard.

        :raises AssertionError: If unsuccessful in deleting all widgets.
        :raises TimeoutException: If no widgets are currently placed, or if not in editing mode.
        """
        while self.get_count_of_widgets() > 0:
            self._widget.click()  # get first - which one does not matter
            self._delete_active_widget()
        IAAssert.is_equal_to(
            actual_value=self.get_count_of_widgets(),
            expected_value=0,
            failure_msg="Failed to delete all widgets.")

    def delete_widget(self, widget: Widget) -> None:
        """
        Delete a specific widget.

        :param widget: The Widget object which contains information regarding the structure of your widget.

        :raises AssertionError: If unsuccessful in removing the supplied widget.
        :raises TimeoutException: If the supplied widget is not present, or if the Dashboard is not in editing mode.
        """
        widget.select_during_edit_mode()
        self._delete_active_widget()
        IAAssert.is_not_true(
            value=widget.is_currently_placed_on_dashboard(),
            failure_msg=f"Failed to remove the '{widget.name}' widget.")

    def drag_widget_to_column_row_and_release(
            self,
            one_based_column_index: int,
            one_based_row_index: int,
            widget: Widget) -> None:
        """
        Click within a widget and drag it to a specified cell, before then releasing the click.

        :param one_based_column_index: The one-based index of the column we will drag the widget to.
        :param one_based_row_index: The one-based index of the row we will drag the widget to.
        :param widget: The Widget object which contains information about the widget we will be dragging.

        :raises TimeoutException: If the Widget is not present, or if the Dashboard is not in editing mode, or if the
            supplied cell indices are not valid.
        """
        cell_x_offset = int(float(self.get_cell_width())) // 2
        cell_y_offset = int(float(self.get_cell_height())) // 2
        # click-and-hold the widget in the center of the 1st (upper-left) cell, move the mouse to the center of the
        # supplied cell, and then release the held click.
        ActionChains(
            driver=self.driver) \
            .move_to_element_with_offset(
            to_element=widget.get_widget(),
            xoffset=cell_x_offset,
            yoffset=cell_y_offset) \
            .click_and_hold() \
            .move_to_element_with_offset(
            to_element=self._get_grid_cell(
                one_based_column_index,
                one_based_row_index).find(),
            xoffset=int(float(self.get_cell_width())),
            yoffset=int(float(self.get_cell_height()))) \
            .release() \
            .perform()

    def enter_editing_mode(self) -> None:
        """
        Click the mode toggle of the Dashboard if not already in editing mode.

        :raises TimeoutException: If the editing toggle is not present.
        """
        if not self.dashboard_is_in_editing_mode():
            self.click_edit_toggle()
        IAAssert.is_true(
            value=self.dashboard_is_in_editing_mode(),
            failure_msg="Failed to enter editing mode.")

    def enter_run_mode(self) -> None:
        """
        Click the mode toggle of the Dashboard if in editing mode.

        :raises TimeoutException: If the editing toggle is not present.
        """
        if self.dashboard_is_in_editing_mode():
            self.click_edit_toggle()
        IAAssert.is_not_true(
            value=self.dashboard_is_in_editing_mode(),
            failure_msg="Failed to enter run mode.")

    def expand_category(self, category: str) -> None:
        """
        Expand a category in the "Add Widget" modal.

        :param category: The case-sensitive name of the category to expand.

        :raises AssertionError: If unsuccessful in expanding the supplied category.
        :raises IndexError: If the supplied category does not exist.
        """
        if not self.category_is_expanded(category=category):
            self._get_category(category=category).click()
        IAAssert.is_true(
            value=self.category_is_expanded(category=category),
            failure_msg=f"Failed to expand the '{category}' category.")

    def get_cell_height(self, include_units: bool = False) -> str:
        """
        Obtain the height of the cells within the grid of the Dashboard.

        :param include_units: Dictates whether the returned value will include units of measurement.

        :returns: The height of the cells of the Dashboard grid, as a string.
        """
        try:
            return self._grid_cell.get_computed_height(include_units=include_units)
        except TimeoutException as toe:
            raise TimeoutException("Unable to locate the grid within the Dashboard.") from toe

    def get_cell_width(self, include_units: bool = False) -> str:
        """
        Obtain the width of the cells within the grid of the Dashboard.

        :param include_units: Dictates whether the returned value will include units of measurement.

        :returns: The width of the cells of the Dashboard grid, as a string.
        """
        try:
            return self._grid_cell.get_computed_width(include_units=include_units)
        except TimeoutException as toe:
            raise TimeoutException("Unable to locate the grid within the Dashboard.") from toe

    def get_column_gutter_width(self, include_units: bool = False) -> str:
        """
        Obtain the width of the gap between columns in the Dashboard.

        :param include_units: Dictates whether the returned value will include units of measurement.

        :returns: The width of the gap between columns of the Dashboard, as a string.
        """
        try:
            gap = self._grid.find().value_of_css_property(property_name="gap")
        except TimeoutException as toe:
            raise TimeoutException("Unable to locate the grid within the Dashboard.") from toe
        if not include_units:
            return gap.split("px")[0]
        else:
            return gap

    def get_count_of_columns(self) -> int:
        """
        Obtain a count of how many columns are configured for the Dashboard.

        :returns: The number of columns available within the Dashboard, regardless of mode.
        """
        try:
            return int(self._grid.find().value_of_css_property(
                property_name="grid-template-columns").split("repeat(")[1].split(",")[0])
        except TimeoutException as toe:
            raise TimeoutException("Unable to locate the grid within the Dashboard.") from toe

    def get_count_of_rows(self) -> int:
        """
        Obtain a count of how many rows are configured for the Dashboard.

        :returns: The number of rows available within the Dashboard, regardless of mode.
        """
        try:
            return int(self._grid.find().value_of_css_property(
                property_name="grid-template-rows").split("repeat(")[1].split(",")[0])
        except TimeoutException as toe:
            raise TimeoutException("Unable to locate the grid within the Dashboard.") from toe

    def get_count_of_widgets(self) -> int:
        """
        Obtain a count of how many widgets are currently displaying inside the Dashboard.
        """
        try:
            return len(self._widget.find_all())
        except TimeoutException:
            return 0

    def get_displayed_widget_categories(self) -> List[str]:
        """
        Obtain the text of all displayed categories.

        :returns: A list which contains the text of all displayed categories.

        :raises TimeoutException: If no categories are found.
        """
        try:
            return [_.text.split("\n")[0] for _ in self._add_widget_categories.find_all()]
        except TimeoutException as toe:
            raise TimeoutException(
                msg="No categories found in the Add Widget modal, or the Add Widget modal itself was missing.") from toe

    def get_list_of_widget_names_in_category(self, category: str) -> List[str]:
        """
        Obtain the text of all widgets listed under a specific category.

        :param category: The category from which you would like the listed widget names.

        :returns: A list which contains all of the widgets listed under the supplied category.

        :raises IndexError: If the supplied category does not exist.
        :raises NoSuchElementException: If no widgets are listed under the supplied category.
        """
        try:
            return [_.text for _ in
                    self._get_category(category=category).find_elements(*self._ADD_WIDGET_MODAL_TITLE_LOCATOR)]
        except NoSuchElementException as nsee:
            raise NoSuchElementException(msg=f"No widgets listed under the {category} category.") from nsee

    def get_origin_of_cell(self, one_based_column_index: int, one_based_row_index: int) -> Point:
        """
        Obtain the origin of a cell from within the grid of the Dashboard.

        :param one_based_column_index: The one-based index of the column of the target cell.
        :param one_based_row_index: The one-based index of the row of the target cell.

        :returns: A two-dimensional point which represents the position of the upper-left corner of the cell described
            by the provided indices.
        """
        try:
            return self._get_grid_cell(
                one_based_column_index=one_based_column_index, one_based_row_index=one_based_row_index).get_origin()
        except TimeoutException as toe:
            raise TimeoutException(
                msg=f"No cell found with a column index of {one_based_column_index} and a row index of "
                    f"{one_based_row_index}.") from toe

    def remove_widget_confirmation_modal_is_displayed(self) -> bool:
        """
        Determine if the modal to remove or cancel widget removal is displayed.

        :returns: True, if the user can see a modal with a "Cancel" and "Remove" button while attempting to remove a
            widget - False otherwise.
        """
        try:
            return self._remove_widget_modal.find().is_displayed()
        except TimeoutException:
            return False

    def resize_bottom_of_widget(self, one_based_row_target: int, widget: Widget) -> None:
        """
        Resize a widget by using the bottom resize handle. Potential for failure if the supplied index is not
        possible due to size constraints of the Widget.

        :param one_based_row_target: The one-based index of the row you would like the widget to end in.
        :param widget: The Widget object which contains information about your widget.

        :raises AssertionError: If unsuccessful in resizing the widget.
        :raises TimeoutException: If the Dashboard is not in editing mode, or if the supplied index is invalid.
        """
        row_difference = int(one_based_row_target) - (widget.get_next_available_cell_as_column_row()[1] - 1)
        if row_difference != 0:
            widget.select_during_edit_mode()
            closest_column = widget.get_starting_column() + widget.get_column_span() // 2
            self._resize_widget(
                handle=self._south_resize_handle,
                one_based_target_column_index=closest_column,
                one_based_target_row_index=one_based_row_target)
        # Adjust for one-based indexing in the assertion.
        IAAssert.is_equal_to(
            actual_value=widget.get_starting_row() + widget.get_row_span() - 1,
            expected_value=one_based_row_target,
            failure_msg=f"Failed to resize the widget via the bottom handle.")

    def resize_left_of_widget(self, one_based_column_target: int, widget: Widget) -> None:
        """
        Resize a widget by using the left side resize handle. Potential for failure if the supplied index is not
        possible due to size constraints of the Widget.

        :param one_based_column_target: The one-based index of the column you would like the widget to begin in.
        :param widget: The Widget object which contains information about your widget.

        :raises AssertionError: If unsuccessful in resizing the widget.
        :raises TimeoutException: If the Dashboard is not in editing mode, or if the supplied index is invalid.
        """
        column_difference = int(one_based_column_target) - (widget.get_next_available_cell_as_column_row()[0] - 1)
        if column_difference != 0:
            widget.select_during_edit_mode()
            closest_row = widget.get_starting_row() + widget.get_row_span() // 2
            self._resize_widget(
                handle=self._west_resize_handle,
                one_based_target_column_index=one_based_column_target,
                one_based_target_row_index=closest_row)
        IAAssert.is_equal_to(
            actual_value=widget.get_starting_column(),
            expected_value=one_based_column_target,
            failure_msg="Failed to resize the widget via the left handle.")

    def resize_right_of_widget(self, one_based_column_target: int, widget: Widget) -> None:
        """
        Resize a widget by using the right side resize handle. Potential for failure if the supplied index is not
        possible due to size constraints of the Widget.

        :param one_based_column_target: The one-based index of the column you would like the widget to end in.
        :param widget: The Widget object which contains information about your widget.

        :raises AssertionError: If unsuccessful in resizing the widget.
        :raises TimeoutException: If the Dashboard is not in editing mode, or if the supplied index is invalid.
        """
        column_difference = int(one_based_column_target) - (widget.get_next_available_cell_as_column_row()[0] - 1)
        if column_difference != 0:
            widget.select_during_edit_mode()
            closest_row = widget.get_starting_row() + widget.get_row_span() // 2
            self._resize_widget(
                handle=self._east_resize_handle,
                one_based_target_column_index=one_based_column_target,
                one_based_target_row_index=closest_row)
        # Adjust for one-based indexing in the assertion.
        IAAssert.is_equal_to(
            actual_value=widget.get_starting_column() + widget.get_column_span() - 1,
            expected_value=one_based_column_target,
            failure_msg="Failed to resize the widget via the right resize handle.")

    def resize_top_of_widget(self, one_based_row_target: int, widget: Widget) -> None:
        """
        Resize a widget by using the top resize handle. Potential for failure if the supplied index is not possible
        due to size constraints of the Widget.

        :param one_based_row_target: The one-based index of the row you would like the widget to start in.
        :param widget: The Widget object which contains information about your widget.

        :raises AssertionError: If unsuccessful in resizing the widget.
        """
        row_difference = int(one_based_row_target) - (widget.get_next_available_cell_as_column_row()[1] - 1)
        if row_difference != 0:
            widget.select_during_edit_mode()
            closest_column = widget.get_starting_column() + widget.get_column_span() // 2
            self._resize_widget(
                handle=self._north_resize_handle,
                one_based_target_column_index=closest_column,
                one_based_target_row_index=one_based_row_target)
        IAAssert.is_equal_to(
            actual_value=widget.get_starting_row(),
            expected_value=one_based_row_target,
            failure_msg="Failed to resize the widget via the top handle.")

    def _delete_active_widget(self) -> None:
        """
        Click the "X" for the currently selected widget, and then confirm the deletion.

        :raises TimeoutException: If no widget is selected/active, or if unable to locate the confirmation button in
            the resulting confirmation modal.
        """
        try:
            self._delete_widget.click()
        except TimeoutException as toe:
            raise TimeoutException(
                msg="There was no X available for the active widget, or no widget was selected/active.") from toe
        self.confirm_remove_widget(binding_wait_time=1)

    def _get_category(self, category: str) -> WebElement:
        """
        Obtain the underlying WebElement of a category based on the text of that category.

        :raises IndexError: If no category with the supplied name could be found.
        :raises TimeoutException: If no categories are found at all within the Add Widget modal.
        """
        try:
            return list(
                filter(
                    lambda e: e.text.split("\n")[0] == category, self._add_widget_categories.find_all()))[0]
        except IndexError as ie:
            raise IndexError(f"Unable to locate any category with a name of '{category}'.") from ie
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate any categories in the Add Widget modal.") from toe

    def _get_grid_cell(self, one_based_column_index: int, one_based_row_index: int) -> ComponentPiece:
        """
        Obtain the ComponentPiece which defines a singular cell within the grid of the Dashboard.

        :param one_based_column_index: The one-based index of the target column.
        :param one_based_row_index: The one-based index of the target row.

        :returns: A single cell of the grid displayed while in editing mode.
        """
        css_selector = f'div.grid-cell.dashboard-cell[data-column="{one_based_column_index}"]' \
                       f'[data-row="{one_based_row_index}"]'
        grid_cell = self._grid_cell_collection.get(css_selector)
        if not grid_cell:
            grid_cell = ComponentPiece(
                locator=(By.CSS_SELECTOR, css_selector),
                driver=self.driver,
                parent_locator_list=self._grid.locator_list,
                poll_freq=self.poll_freq)
            self._grid_cell_collection[css_selector] = grid_cell
        return grid_cell

    def _resize_widget(
            self,
            handle: ComponentPiece,
            one_based_target_column_index: int,
            one_based_target_row_index: int) -> None:
        """
        Resize a widget.

        :param handle: The ComponentPiece which identifies the handle we will be dragging.
        :param one_based_target_column_index: The one-based index of the column we will be dragging the handle to.
        :param one_based_target_row_index: The one-based index of the row we will be dragging the handle to.
        """
        try:
            ActionChains(driver=self.driver).drag_and_drop(
                source=handle.find(),
                target=self._get_grid_cell(
                    one_based_column_index=one_based_target_column_index,
                    one_based_row_index=one_based_target_row_index).find()).perform()
        except TimeoutException as toe:
            raise TimeoutException(
                msg="Unable to locate either the resize handle or the destination cell within the grid while resizing "
                    "a widget.") from toe
