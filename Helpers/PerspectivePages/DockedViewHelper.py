from enum import Enum
from typing import Optional, List

from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from Components.BasicComponent import ComponentPiece
from Pages.PagePiece import PagePiece


class ConfigurationOptions:
    """
    These configuration options define what is available for Docked Views
    """
    class Display(Enum):
        AUTO = "auto"
        ON_DEMAND = "onDemand"
        VISIBLE = "visible"

    class Content(Enum):
        AUTO = "auto"
        COVER = "cover"
        PUSH = "push"

    class Anchor(Enum):
        FIXED = "fixed"
        SCROLLABLE = "scrollable"

    class Handle(Enum):
        AUTOHIDE = "autoHide"
        HIDE = "hide"
        SHOW = "show"


class Side(Enum):
    """The sides a Docked View may belong to. Used most commonly for interaction with handles."""
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"


class DockedViewHelper(PagePiece):
    """
    Used for interacting with Docked Views and determining their current state. The terms "displayed" and "expanded"
    may be used interchangeably.
    """
    _DOCKED_VIEW_UNFORMATTED_DIV_CSS = 'div.docked-view-{0} '
    _RESIZE_HANDLES_UNFORMATTED_DIV_CSS = '{0}div.dock-border.drag-border div.resize-zone'
    _DOCK_MODAL_LOCATOR = (By.CSS_SELECTOR, "div.modal.dock-modal")

    def __init__(self, driver: WebDriver):
        super().__init__(driver=driver)
        self._modal = ComponentPiece(
            locator=self._DOCK_MODAL_LOCATOR, driver=driver, wait_timeout=1)
        self._docked_views = {}

    def click_modal_overlay(self) -> None:
        """Click a Docked View modal overlay, if present. If no overlay is present, no action is taken."""
        if self.modal_overlay_is_present():
            self._modal.click(wait_timeout=1, binding_wait_time=1)

    def docked_view_with_root_id_is_expanded(
            self, docked_view_root_container_id: str, side: Optional[Side] = None) -> bool:
        """
        Determine if a Docked View with a specified `root` id is expanded. The `root` ID should not be confused with
        the ID of the Docked View configuration.

        :param docked_view_root_container_id: The ID in use by the `root` node of the View we will verify the
            expansion status of.
        :param side: The side you expect the View to be expanded on. If not supplied, we only look for basic
            visibility; usages of the View OUTSIDE of a Docked View will result in a returned value of True.

        :returns: True, if the supplied `root` ID identifies a View which is expanded on the specified side - False
            otherwise.
        """
        locator_text = 'div[id="{0}"]'.format(docked_view_root_container_id)
        if side:
            side = side.value
            side_locator = self._DOCKED_VIEW_UNFORMATTED_DIV_CSS.format(side)
            locator_text = " ".join([side_locator, locator_text])
        try:
            return WebDriverWait(self.driver, 1).until(
                ec.visibility_of_element_located((By.CSS_SELECTOR, locator_text))) is not None
        except TimeoutException:
            return False

    def docked_view_is_resizable(self, side: Side) -> bool:
        """
        Determine if resize handles are displayed for the currently expanded Docked View on the given side.

        :param side: The side of the Page which we will check for resize handles.

        :returns: True, if resize handles are present for the currently expanded Docked View on the specified side -
            False otherwise.
        """
        side_css_as_str = self._DOCKED_VIEW_UNFORMATTED_DIV_CSS.format(side.value)
        css_selector = self._RESIZE_HANDLES_UNFORMATTED_DIV_CSS.format(side_css_as_str)
        try:
            return self.driver.find_element(By.CSS_SELECTOR, css_selector).is_displayed()
        except NoSuchElementException:
            return False

    def drag_docked_view(self, side: Side, distance_in_px: int) -> None:
        """
        Drag the Docked View on the supplied side some number of pixels. The distance is always measured from the
        edge which the Docked View originates from.

        Example:
            A distance of 50 will drag a left-based Docked View 50 pixels to the right and will drag a
            right-based Docked View 50 pixels to the left.

        :param side: The side the Docked View to be dragged belongs to.
        :param distance_in_px: The numeric count of pixels to drag the Docked View.

        :raises NoSuchElementException: If the specified side does not have a Docked View currently expanded which
            is resizable.
        """
        if side in [Side.RIGHT, Side.BOTTOM]:
            distance_in_px = int(float(distance_in_px)) * -1.0
        if side in [Side.LEFT, Side.RIGHT]:
            x = distance_in_px
            y = 0
        else:
            x = 0
            y = distance_in_px
        handle_locator = f'{self._DOCKED_VIEW_UNFORMATTED_DIV_CSS.format(side.value)} ' \
                         f'div.dock-border.drag-border svg.drag-icon'
        self.selenium.click_drag_release(
            web_element=self.driver.find_element(By.CSS_SELECTOR, handle_locator), x=x, y=y)

    def get_count_of_docked_views_open_by_side(self, side: Side) -> int:
        """
        Returns a count of all Docked Views on a given side.

        :param side: The side of the Page from which you would like a count of configured Docked Views.

        :returns: a count of Docked Views for the specified side.
        """
        try:
            return len(self._get_all_displayed_docked_views_by_side(side=side))
        except TimeoutException:
            return 0

    def get_path_of_custom_icon(self, side: Side) -> str:
        """
        Returns the icon path in use for the FIRST Docked View handle on the supplied side. This function is unsafe
        to use when dealing with multiple Docked Views on a given side.

        :param side: The side the Docked View to be dragged belongs to.

        :returns: The slash-delimited path of the icon in use for the FIRST handle found on the specified side.

        :raises AssertionError: If not EXACTLY ONE Docked View is open on the supplied side.
        :raises NoSuchElementException: If the displayed Docked View does not contain a handle.
        """
        return self._get_all_displayed_docked_views_by_side(
            side=side)[0].find_element(*(By.TAG_NAME, "svg")).get_attribute("data-icon")

    def get_width_of_displayed_docked_view_by_side(self, side: Side, include_units: bool = False) -> str:
        """
        Obtain the width of the displayed Docked View on a given side of the page.

        :param side: The side the Docked View to be dragged belongs to.
        :param include_units: Dictates whether the returned value includes units of measurement.

        :returns: The width of the displayed Docked View on the specified side, as a string value. Units may be included
            depending on supplied arguments.
        """
        return self._get_docked_view(side=side).get_computed_width(include_units=include_units)

    def docked_view_is_using_default_icon_path(self, side: Side) -> bool:
        """
        Determine if the Docked View on a specified side of the Page is using the default icon. Will always check the
        first available handle.

        :param side: The side the Docked View to be dragged belongs to.

        :returns: True, if the first available Docked View handle on the specified side is using the default icon -
            False otherwise.
        """
        return self.get_path_of_custom_icon(side=side) is None

    def handle_with_custom_icon_path_exists_on_side(self, side: Side, custom_icon_path: str) -> bool:
        """
        Determine if any Docked View handle on the specified side is using the specified custom icon path.

        :param side: The side the Docked View to be dragged belongs to.
        :param custom_icon_path: The slash-delimited path you expect to be in use by a Docked View handle on the
            specified side.

        :returns: True, if any Docked View handle on the specified side is using the supplied custom icon path - False
            otherwise.
        """
        try:
            handles = self.driver.find_elements(By.CSS_SELECTOR, f'div.toggle-{side.value} svg')
            for handle in handles:
                if handle.get_attribute("data-icon") == custom_icon_path:
                    return True
            return False
        except NoSuchElementException:
            return False

    def handle_with_custom_icon_path_is_visible_on_side(self, side: Side, custom_icon_path: str) -> bool:
        """
        Determine if any Docked View handle on the specified side is using the specified custom icon path and is
        currently visible.

        :param side: The side the Docked View to be dragged belongs to.
        :param custom_icon_path: The slash-delimited path you expect to be in use by a Docked View handle on the
            specified side.

        :returns: True, if any Docked View handle on the specified side is using the supplied custom icon path and is
            currently visible - False otherwise.
        """
        try:
            docked_views = self.driver.find_elements(By.CSS_SELECTOR, f'div.toggle-{side.value}')
            for docked_view in docked_views:
                handle = docked_view.find_element(By.TAG_NAME, "svg")
                if handle.get_attribute("data-icon") == custom_icon_path:
                    return "toggle-visible" in docked_view.get_attribute("class")
            return False
        except NoSuchElementException:
            return False
        except StaleElementReferenceException:
            return False

    def modal_overlay_is_present(self) -> bool:
        """
        Determine if the overlay in use by Docked Views is currently present in the session.

        :returns: True, if a Docked View is currently displaying in a modal form, where an overlay is covering the
            primary view - False otherwise.
        """
        try:
            return self._modal.find() is not None
        except TimeoutException:
            return False

    def _get_all_displayed_docked_views_by_side(self, side: Side) -> List[WebElement]:
        """
        Obtain all Docked Views which are visible on a given side. There should only ever be either 0 or 1.

        :param side: The side from which we would like all of the visible Docked Views.

        :returns: A list of WebElements, where each WebElement is a visible Docked View on the specified side.

        :raises AssertionError: If there is some number other than 0 or 1 visible on a specified side.
        """
        docked_view = self._get_docked_view(side=side)
        assert len(docked_view.find_all()) in [0, 1], "There should only ever be 0 or 1 Docked Views visible on a side."
        return docked_view.find_all() if self._is_visible(side=side) else []

    def _is_visible(self, side: Side) -> bool:
        """
        Determine if the Specified side currently has a visible Docked View.

        :param side: The side to check for any visible Docked Views.

        :returns: True, if the specified side has a visible Docked View - False otherwise.
        """
        docked_view = self._get_docked_view(side=side)
        if side in [Side.LEFT, Side.RIGHT]:
            origin = docked_view.get_origin().X
            width_or_height = docked_view.get_computed_width(include_units=False)
            viewport_width_or_height = self.selenium.get_inner_width()
        else:
            origin = docked_view.get_origin().Y
            width_or_height = docked_view.get_computed_height(include_units=False)
            viewport_width_or_height = self.selenium.get_inner_height()
        if float(width_or_height) < 1:  # return now because Docked View is not visible
            return False
        # Bottom/Right: If the top-left corner is between 0 and the width of the viewport.
        # Top: If the top-left corner plus the height of the Docked View is between 0 and the height of the viewport.
        # Left: If the top-left corner plus the width of the Docked View is between 0 and the width of the viewport.
        return (0 < float(origin) < float(viewport_width_or_height)) or \
               (0 < (float(origin) + float(width_or_height)) < viewport_width_or_height)

    def _get_docked_view(self, side: Side) -> ComponentPiece:
        """
        Obtain a generic Docked View definition based on the side of the Page.

        :param side: The side of the page for which you would like a generic Docked View definition.

        :returns: A Component Piece which defines a Docked View on the specified side.
        """
        side = side.value
        docked_view = self._docked_views.get(side)
        if not docked_view:
            docked_view = ComponentPiece(
                locator=(By.CSS_SELECTOR, f"{self._DOCKED_VIEW_UNFORMATTED_DIV_CSS.format(side)}"),
                driver=self.driver)
            self._docked_views[side] = docked_view
        return docked_view
