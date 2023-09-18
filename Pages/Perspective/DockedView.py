from enum import Enum
from time import sleep
from typing import Tuple, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Helpers.IAAssert import IAAssert
from Helpers.Point import Point
from Pages.Perspective.View import View


class DockedView(View):
    """
    We need to know which direction the view is expected to be in, and we need to know the id of the
    root container (node). To set this id, select the root node of the view, then insert a value into the META
    properties for the view with a key of "domId".

    This does mean that we will be unable to accurately test Docked Views if they are also a View presently displayed
    on the Page.
    """
    class Side(Enum):
        TOP = 'top'
        BOTTOM = 'bottom'
        LEFT = 'left'
        RIGHT = 'right'

    def __init__(
            self,
            driver: WebDriver,
            side: Side,
            root_id: str,
            primary_locator: Tuple[By, str] = None,
            view_resource_path: Optional[str] = None,
            config_id: Optional[str] = None):
        """
        :param driver: The WebDriver in use for the browser window.
        :param side: The side on which this Docked View is configured.
        :param root_id: The domId of the root node for this Docked View.
        :param primary_locator: The primary locator used to identify a component of the View. This will be the same as
            the `root_id` in most cases.
        :param view_resource_path: The path of the View within the "Perspective/Views" directory of the Designer.
        :param config_id: The ID configured within the Designer for this Docked View.
        """
        View.__init__(
            self,
            driver=driver,
            primary_locator=primary_locator,
            view_resource_path=view_resource_path)
        self._side = side
        self._direction = side
        self._root_id = root_id
        self._config_id = config_id
        self._root = BasicPerspectiveComponent(
            locator=(By.ID, root_id), driver=driver)
        dock_id_piece = f' > div[data-dock-id="{config_id}"] ' if config_id else ''
        handle_locator = (
            By.CSS_SELECTOR,
            f"div.docked-view-{self._side.value}{dock_id_piece} div.view-toggle")
        self._dock_toggle_handle = ComponentPiece(driver=driver, locator=handle_locator, wait_timeout=1)

    def click_handle(self) -> None:
        """
        Click the handle of this Docked View.

        :raises TimeoutException: If no Docked View handle exists on the side with this Docked View.
        :raises AssertionError: If unsuccessful in changing the expansion state of this Docked View after clicking the
            associated handle.
        """
        original_state = self.is_expanded()
        if not self.handle_is_visible():
            self.selenium.move_mouse(x_offset=1, y_offset=1)
            try:
                locator = (By.CSS_SELECTOR, f'div.toggle-{self._side.value}.toggle-visible')
                self.wait.until(
                    ec.presence_of_element_located(locator), f"Locator was never found: {locator}")
            except TimeoutException as toe:
                raise TimeoutException(msg="The handle of the docked view never became visible.") from toe
            sleep(1)
        self._dock_toggle_handle.click()
        sleep(2)  # We need to allow for the view to go through its expand/collapse animation (Edge is slow)
        if original_state == self.is_expanded():
            # geckodriver issue! Firefox does not correctly release the mouse click, so click AGAIN to force it
            self.click_handle()
        IAAssert.is_not_equal_to(
            actual_value=self.is_expanded(),
            expected_value=original_state,
            failure_msg=f'We failed to {"collapse" if original_state else "expand"} the Docked View.')

    def collapse(self) -> None:
        """
        Collapse this Docked View if it is currently expanded. If this Docked View is already collapsed, then no action
        is taken.

        :raises TimeoutException: If no Docked View handle exists on the side with this Docked View.
        :raises AssertionError: If unsuccessful in changing the expansion state of this Docked View after clicking the
            associated handle.
        """
        if self.is_expanded():
            self.click_handle()

    def expand(self) -> None:
        """
        Expand this Docked View if it is currently collapsed. If this Docked View is already expanded, then no action
        is taken.

        :raises TimeoutException: If no Docked View handle exists on the side with this Docked View.
        :raises AssertionError: If unsuccessful in changing the expansion state of this Docked View after clicking the
            associated handle.
        """
        if not self.is_expanded():
            self.click_handle()

    def get_config_id(self) -> str:
        """
        The configuration ID is the optionally supplied 'quasi-unique' identifier for the docked view configuration.
        The uniqueness of this ID is not enforced, and the existence of docked views on ANY side which share
        the same ID could result in undocumented and contentious behavior. This config ID is not tied to the View -
        only the configuration - and due to system.perspective.alterDock and the ability to configure any view with
        any ID, this property should only be set on initialization of the docked view.
        """
        return self._config_id

    def get_height(self, include_units: bool = False) -> str:
        """
        Get the computed height of the Docked View. Must return as a string because of the possibility of
        included units.

        :param include_units: Include the units of height (typically "px") if True, otherwise return only the numeric
            value (as a string).

        :returns: The computed height of the Docked View as a string.

        :raises TimeoutException: If the root of the Docked View is not found in the DOM.
        """
        return self._root.get_computed_height(include_units=include_units)

    def get_origin(self) -> Point:
        """
        Get the Cartesian Coordinate of the upper-left corner of the component, measured from the
        top-left of the viewport.

        :returns: The Cartesian Coordinate of the upper-left corner of the component, measured from the
            top-left of the viewport.
        """
        return self._root.get_origin()

    def get_termination(self) -> Point:
        """
        Get the Cartesian Coordinate of the bottom-right corner of the component, measured from the
        top-left of the viewport.

        :returns: The Cartesian Coordinate of the bottom-right corner of the component, measured from the
            top-left of the viewport.
        """
        return self._root.get_termination()

    def get_width(self, include_units: bool = False) -> str:
        """
        Get the computed width of the Docked View. Must return as a string because of the possibility of
        included units.

        :param include_units: Include the units of width (typically "px") if True, otherwise return only the numeric
            value (as a string).

        :returns: The computed width of the Docked View as a string.

        :raises TimeoutException: If the root of the Docked View is not found in the DOM.
        """
        return self._root.get_computed_width(include_units=include_units)

    def handle_is_visible(self) -> bool:
        """
        Determine if the handle of this Docked View is visible. May return "false positive" if the Docked View does not
        have a configured ID.

        :returns: True, if this Docked View has a configured ID and the handle is visible, or if this Docked View does
            not have a configured ID but any Docked View on the same side of this Docked View has a handle visible.
            False, if This Docked View has a configured ID but no handle is visible, or if no Docked View on the same
            side as this Docked View has a handle which is visible.
        """
        try:
            return 'toggle-visible' in self._dock_toggle_handle.find().get_attribute('class')
        except TimeoutException:
            # no dock toggle found
            return False

    def is_expanded(self) -> bool:
        """
        Determine if the Docked View is currently expanded.

        :returns: True, if the underlying View is displayed - False if the underlying view is not displayed, or if the
            View does not have an HTML `id` attribute applied to the root node.
        """
        try:
            return self._root.find(wait_timeout=0).is_displayed()
        except TimeoutException:
            return False

    def is_present_in_dom(self) -> bool:
        """
        Determine if the Docked View is present within the DOM.

        :returns: True, if the underlying View in use for the Docked View is found within the DOM - False otherwise.
        """
        try:
            return self._root.find() is not None
        except TimeoutException:
            return False
