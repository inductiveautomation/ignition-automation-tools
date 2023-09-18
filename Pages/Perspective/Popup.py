from enum import Enum
from typing import TypeVar

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece
from Components.PerspectiveComponents.Common.Icon import CommonIcon
from Helpers.IAAssert import IAAssert
from Helpers.IASelenium import IASelenium
from Pages.Perspective.View import View

V = TypeVar("V", bound=View)  # specifies that any subclass of View is acceptable.


class Popup(ComponentPiece):
    """
    Popups are glorified View wrappers which provide access to the view as a public attribute.
    """
    class ResizeHandle(Enum):
        """The resize handles available to Popups."""
        EAST = "e"
        NORTH = "n"
        NORTHWEST = "nw"
        NORTHEAST = "ne"
        SOUTH = "s"
        SOUTHEAST = "se"
        SOUTHWEST = "sw"
        WEST = "w"

    _GENERIC_POPUP_LOCATOR = (By.CSS_SELECTOR, "div.popup")
    _HEADER_LOCATOR = (By.CSS_SELECTOR, "div.popup-header")
    _BODY_LOCATOR = (By.CSS_SELECTOR, "div.popup-body")
    _CLOSE_ICON_LOCATOR = (By.CSS_SELECTOR, "svg.close-icon")
    _DRAG_HANDLE_LOCATOR = (By.CSS_SELECTOR, "div.popup-drag")
    _RESIZE_ZONE_LOCATOR = (By.CSS_SELECTOR, "div.resize-zone")
    _MODAL_LOCATOR = (By.CSS_SELECTOR, "div.modal")

    def __init__(
            self,
            driver: WebDriver,
            popup_id: str,
            view: V = None):
        """
        :param driver: The WebDriver in use.
        :param popup_id: The ID in use for the popup as configured in the Designer. Do NOT supply the HTML id attribute
            for this value. On the backend, Perspective will prepend "popup-" to all popups - it is important you supply
            this ID value exactly as you have it configured in the Designer.
        :param view: An instance of a View.
        """
        # build the formatted ID first
        self.formatted_id = f"popup-{popup_id}"
        ComponentPiece.__init__(
            self,
            locator=(By.ID, self.formatted_id),
            driver=driver,
            parent_locator_list=None)
        self.view = view
        self._selenium = IASelenium(driver=driver)
        self.title_bar = ComponentPiece(  # needs to be public for drag testing
            locator=self._HEADER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            description="The title bar of the Popup, where the title text and close icon are displayed.",
            wait_timeout=0)
        self._drag_handle = ComponentPiece(
            locator=self._DRAG_HANDLE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            description="The drag handle located within the title bar.",
            wait_timeout=0)
        self._popup_body = ComponentPiece(
            locator=self._BODY_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            description="The internal contents of the Popup, where the View is visible.",
            wait_timeout=0)
        self._close_icon = CommonIcon(
            locator=self._CLOSE_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            description="The 'X' used to close the Popup.",
            wait_timeout=0)
        self._modal = ComponentPiece(
            locator=self._MODAL_LOCATOR,
            driver=driver,
            description="The overlay displayed when a Popup is opened as a modal.",
            parent_locator_list=None,
            wait_timeout=0)
        self._resize_zones = {}
        self._make_resize_zones()

    def click_modal_overlay(self) -> None:
        """
        Click the modal overlay. We accomplish this by hovering over the title bar, and then clicking slightly above
        the title bar.

        Clicking the overlay is a bit tricky because of browser differences; Chrome might click in the top-left, and
        Firefox might click in the middle - where your Popup is likely to intercept the click. To get around this, we
        actually target the title bar (if present) or Popup, then specify a location some number of pixels directly
        above the Popup, blindly clicking at the location instead of targeting the modal itself.

        :raises AssertionError: If the Popup is not a modal, or the overlay is not present.
        """
        IAAssert.is_true(
            value=self.is_modal(),
            failure_msg=f"Either this popup ({self.formatted_id}) is not a modal, or the overlay is not present.")
        if self.has_title_bar():
            # Targeting the title bar when available reduces the vertical offset, which reduces potential issues.
            self.title_bar.hover()
            height = self.title_bar.find().size.get('height')
        else:
            self.hover()
            height = self.find().size.get('height')
        y_offset = (height / 2 * -1) - 20  # safety handling for firefox vs chrome click location discrepancy
        self._selenium.click_at_offset(y=y_offset)

    def drag_popup_by_offset(self, x_offset: int = 0, y_offset: int = 0) -> None:
        """
        Drag the Popup some direction by clicking the drag handle in the title bar.

        :param x_offset: The left/right value to drag the Popup. Positive values are right, and negative values are
            left.
        :param y_offset: The up/down value to drag the Popup. Positive values are DOWN, negative values are UP.

        :raises TimeoutException: If the Popup is not present, or if the Popup is not configured to be draggable.
        """
        self._selenium.click_drag_release(web_element=self._drag_handle.find(), x=x_offset, y=y_offset)

    def close_popup(self) -> None:
        """
        Close the Popup by clicking the close icon.

        :raises TimeoutException: If the Popup is not configured to display the close icon.
        """
        self._close_icon.click()

    def get_height_of_popup_body(self, include_units: bool = False) -> str:
        """
        Obtain the height of the area used to display the View of this Popup.

        :param include_units: Dictates whether the returned value includes units of measurement.

        :returns: The height of the area available to the View used within this Popup as a string.
        """
        return self._popup_body.get_computed_height(include_units=include_units)

    def get_width_of_popup_body(self, include_units: bool = False) -> str:
        """
        Obtain the width of the area used to display the View of this Popup.

        :param include_units: Dictates whether the returned value includes units of measurement.

        :returns: The width of the area available to the View used within this Popup as a string.
        """
        return self._popup_body.get_computed_width(include_units=include_units)

    def get_title(self) -> str:
        """
        Obtain the text displayed within the title bar of this Popup.

        :returns: The text displayed within the title bar of the Popup.
        """
        return self.title_bar.get_text()

    def has_close_icon(self) -> bool:
        """
        Determine if this Popup contains a close icon.

        :returns: True, if this Popup contains a close icon - False otherwise.
        """
        try:
            return self._close_icon.find(wait_timeout=0) is not None
        except TimeoutException:
            return False

    def has_title_bar(self) -> bool:
        """
        Determine if this Popup is displaying a Title Bar. Note that the title bar may be displayed even if no text is
        configured, as the title bar also contains the close icon.

        :returns: True, if the Popup is currently displaying a title bar at the top of the Popup.
        """
        try:
            return self.title_bar.find(wait_timeout=0) is not None
        except TimeoutException:
            return False

    def is_modal(self) -> bool:
        """
        Determine if the Popup is currently displayed as a modal. As modal overlays are not directly attached to the
        Popup itself, the best we can do is verify the Popup is self-reporting as a modal and that an overlay is
        currently in place on the Page.

        :returns: True, if the Popup is declaring itself to be a modal AND an overlay exists - False otherwise.
        """
        return 'popup-modal' in self.find(wait_timeout=0).get_attribute('class') and self.overlay_is_present()

    def is_draggable(self) -> bool:
        """
        Determine if the Popup is draggable.

        :returns: True, if the Popup has a draggable handle within the title bar - False otherwise.
        """
        try:
            return self._drag_handle.find(wait_timeout=0) is not None
        except TimeoutException:
            return False

    def is_resizable(self) -> bool:
        """
        Determine if the Popup is resizable.

        :returns: True, if the Popup contains resize handles as part of its boundaries - False otherwise.
        """
        try:
            return self._resize_zones[Popup.ResizeHandle.NORTH].find() is not None
        except TimeoutException:
            return False

    def overlay_is_present(self) -> bool:
        """
        Determine if an overlay is currently displayed. Will return true even if the overlay does not belong to this
        Popup as there is no direct connection in the DOM.

        :returns: True if ANY overlay is present, even if for another Popup. False if no overlays are displayed.
        """
        try:
            return self._modal.find(wait_timeout=0) is not None
        except TimeoutException:
            return False

    def is_displayed(self) -> bool:
        """
        Determine if this Popup is currently displayed.

        :returns: True, if this Popup is currently displayed - False otherwise.
        """
        try:
            return self.find(wait_timeout=0).is_displayed()
        except TimeoutException:
            return False

    def resize_popup(self, x_drag: int, y_drag: int, resize_handle: ResizeHandle) -> None:
        """
        Resizes this Popup by dragging the specified resize handle.

        :param x_drag: The horizontal distance to drag the resize handle. Positive values are to the right, and negative
            values are to the left.
        :param y_drag: The vertical distance to drag the resize handle. Positive values are DOWN, and negative values
            are UP.
        :param resize_handle: The handle to use for resizing.

        :raises TimeoutException: If the Popup is not present, or is not configured to be resizable.
        """
        ActionChains(driver=self.driver)\
            .click_and_hold(on_element=self._resize_zones.get(resize_handle).find())\
            .move_by_offset(xoffset=x_drag, yoffset=y_drag)\
            .release()\
            .perform()

    def _make_resize_zones(self) -> None:
        """
        Initialize all the potential resize zones of the Popup.
        """
        for resize_zone in Popup.ResizeHandle:
            self._resize_zones[resize_zone] = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'{self._RESIZE_ZONE_LOCATOR[1]}.-{resize_zone.value}'),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                description=f"The resize zone of the {self.formatted_id} Popup in the {resize_zone.value} region "
                            f"({resize_zone}).",
                wait_timeout=0)
