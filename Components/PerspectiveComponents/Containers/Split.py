from enum import Enum
from typing import List, Optional, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece, BasicPerspectiveComponent
from Components.PerspectiveComponents.Common.Icon import CommonIcon
from Helpers.CSSEnumerations import CSS


class Orientation(Enum):
    """An enumeration of the available orientations of the Split Container."""
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'


class Split(BasicPerspectiveComponent):
    """A Perspective Split Container."""
    _CONTENT_WRAPPER_LOCATOR = (By.CSS_SELECTOR, 'div.split-container')
    _FIRST_PANE_LOCATOR = (By.CSS_SELECTOR, 'div.split-pane')
    _SPLIT_HANDLE_LOCATOR = (By.CSS_SELECTOR, 'div.split-handle')
    _INVISIBLE_HANDLE_LOCATOR = (By.CSS_SELECTOR, 'div.split-handle-invis')
    _HANDLE_ICON_LOCATOR = (By.CSS_SELECTOR, 'svg.drag-icon')

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
        self._content_wrapper = ComponentPiece(
            locator=self._CONTENT_WRAPPER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._split_handle = ComponentPiece(
            locator=self._SPLIT_HANDLE_LOCATOR,
            driver=self.driver,
            parent_locator_list=self._content_wrapper.locator_list,
            poll_freq=poll_freq)
        self._split_handle_invisible = ComponentPiece(
            locator=self._INVISIBLE_HANDLE_LOCATOR,
            driver=self.driver,
            parent_locator_list=self._content_wrapper.locator_list,
            poll_freq=poll_freq)
        self._first_pane = ComponentPiece(
            locator=self._FIRST_PANE_LOCATOR,
            driver=driver,
            parent_locator_list=self._content_wrapper.locator_list,
            poll_freq=poll_freq)
        self._handle_icon = CommonIcon(
            locator=self._HANDLE_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self._split_handle.locator_list,
            poll_freq=poll_freq)

    def click_and_hold_split_handle(self, pause_after_click: float = 5) -> None:
        """
        Click the handle of the Split Container, and hold it for an indefinite amount of time. NOTE: THIS FUNCTION DOES
        NOT RELEASE THE CLICK.

        :param pause_after_click: The amount of time after making the click before allowing code to continue.
        """
        ActionChains(self.driver).click_and_hold(self._split_handle.find()).pause(seconds=pause_after_click).perform()

    def drag_split_handle_to_pixel_value(self, desired_position_in_pixels: float) -> None:
        """
        Drag the handle of the Split Container from its current position to the specified pixel. Pixels outside the
        bounds of the Split Container are valid, though the Split Container should stop updating the handle position
        once the cursor leaves the bounds of the Container. The drag will always be done to the specified pixel based
        on the orientation of the Split Container; vertical orientations will always drag the handle up/down, and
        horizontal orientations will always drag the handle left/right.

        :param desired_position_in_pixels: The pixel to which we should drag the handle of the Split Container.
        """
        if self.has_orientation(orientation=Orientation.VERTICAL):
            x_step = 0
            y_step = 1
            first_pane_height = float(self._first_pane.get_computed_height())
            handle_height = float(self._split_handle.get_computed_height())
            current_pixel_position = first_pane_height + (handle_height / 2)
        else:
            x_step = 1
            y_step = 0
            first_pane_width = float(self._first_pane.get_computed_width())
            handle_width = float(self._split_handle.get_computed_width())
            current_pixel_position = first_pane_width + (handle_width/2)
        pixel_count = (float(desired_position_in_pixels) - current_pixel_position)
        ActionChains(self.driver)\
            .click_and_hold(self._split_handle.find())\
            .pause(seconds=5)\
            .move_by_offset((x_step * pixel_count), (y_step * pixel_count))\
            .release()\
            .perform()

    def drag_split_handle_to_percentage_value(self, desired_percentage: float) -> None:
        """
        Drag the handle of the Split Container to a percentage of the available space of the Split Container.

        :param desired_percentage: The numeric percentage to which we should drag the handle of the Split Container.
        """
        if self.has_orientation(orientation=Orientation.VERTICAL):
            x_step = 0
            y_step = 1
            first_pane_height = float(self._first_pane.get_computed_height())
            handle_height = float(self._split_handle.get_computed_height())
            container_height = float(self.get_computed_height())
            current_percent = (first_pane_height + (handle_height / 2.0))
            target_percent = (desired_percentage / 100.0) * container_height
        else:
            x_step = 1
            y_step = 0
            first_pane_width = float(self._first_pane.get_computed_width())
            handle_width = float(self._split_handle.get_computed_width())
            container_width = float(self.get_computed_width())
            current_percent = (first_pane_width + (handle_width / 2.0))
            target_percent = (desired_percentage / 100.0) * container_width
        pixel_count = target_percent - current_percent
        ActionChains(self.driver)\
            .click_and_hold(self._split_handle.find()) \
            .pause(seconds=5)\
            .move_by_offset((x_step*pixel_count), (y_step*pixel_count))\
            .release()\
            .perform()

    def get_split_handle_height(self, include_units: bool = False) -> str:
        """
        Obtain the height of the handle of the Split Container.

        :param include_units: Dictates whether the returned height includes units of measurement.

        :returns: The height of the handle of the Split Container, potentially with units.
        """
        try:
            return self._split_handle.get_computed_height(include_units=include_units)
        except TimeoutException:
            return self._split_handle_invisible.get_computed_height(include_units=include_units)

    def get_split_handle_position_within_container(self) -> float:
        """
        Obtain the pixel location of the CENTER of the handle within the Split Container. Note that this pixel location
        is relative to the upper-left corner of the Split Container - not the Viewport.

        :returns: The pixel location of the CENTER of the handle of the Split Container, as a relative position within
            the Split Container.
        """
        if self.has_orientation(orientation=Orientation.HORIZONTAL):
            return float(self._first_pane.get_css_property(property_name=CSS.WIDTH).split("p")[0]) + \
                   (float(self.get_split_handle_width()) / 2)
        else:
            return float(self._first_pane.get_css_property(property_name=CSS.HEIGHT).split("p")[0]) + \
                   (float(self.get_split_handle_height()) / 2)

    def get_split_handle_width(self, include_units: bool = False) -> str:
        """
        Obtain the width of the handle of the Split Container.

        :param include_units: Dictates whether the returned width includes units of measurement.

        :returns: The width of the handle of the Split Container, potentially with units.
        """
        try:
            return self._split_handle.get_computed_width(include_units=include_units)
        except TimeoutException:
            return self._split_handle_invisible.get_computed_width(include_units=include_units)

    def has_orientation(self, orientation: Orientation) -> bool:
        """
        Determine if the Split Container has the specified orientation.

        :param orientation: The orientation we will attempt to verify.

        :returns: True, of the Split Container has the specified orientation - False otherwise.
        """
        return f'split-container-{orientation.value}' in self._content_wrapper.find().get_attribute('class')

    def release_split_handle_click(self) -> None:
        """
        Release any held click on the Split Container.
        """
        ActionChains(self.driver).release().perform()

    def split_handle_is_active(self) -> bool:
        """
        Determine if the handle of the Split Container is currently rendered as being in an active state.

        :returns: True, if the handle of the Split Container is rendered as 'active'.
        """
        return 'isActive' in self._split_handle.find().get_attribute('class')

    def split_handle_is_draggable(self) -> bool:
        """
        Determine if the handle is displaying as enabled/draggable.

        :returns: True, if the handle is displaying as enabled/draggable - False otherwise.
        """
        return 'split-handle-undraggable' not in self._split_handle.find().get_attribute('class')

    def split_handle_is_visible(self) -> bool:
        """
        Determine if the handle of the Split Container is visible to a user.

        :returns: True, if a user is able to see the handle of the Split Container - False otherwise.
        """
        try:
            return self._split_handle.find().is_displayed()
        except TimeoutException:
            return not self._split_handle_invisible.find().is_displayed()
