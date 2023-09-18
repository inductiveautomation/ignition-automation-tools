from typing import Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from Components.BasicComponent import BasicPerspectiveComponent
from Helpers.CSSEnumerations import CSS
from Helpers.Point import Point
from Pages.Perspective.View import View


class ViewCanvasInstancedView(View):
    """
    View Canvas Instanced Views are extremely similar to regular Views except the expectation is that each Instanced
    View have a unique locator at the root node and that each instance may have different positioning attributes
    applied.
    """

    def __init__(
            self,
            driver: WebDriver,
            root_locator: Tuple,
            view_resource_path: str = None):
        """
        :param driver: The WebDriver in use for the browser window.
        :param root_locator: The CSS locator of the root node of the View. XPATH is not allowed.
        :param view_resource_path: The path to the View within the Designer, after `Perspective/Views`.
        """
        View.__init__(
            self,
            driver=driver,
            primary_locator=root_locator,
            view_resource_path=view_resource_path)
        self._root = BasicPerspectiveComponent(
            locator=root_locator,
            driver=driver)

    def get_z_index(self) -> int:
        """
        Obtain the z-index in use by this instance of the View.

        :returns: The z-index in use by this Instanced View.
        
        :raises TimeoutException: If the root node (and therefore the View) is not found in the DOM.
        """
        return int(self._get_wrapper_div().value_of_css_property(property_name=CSS.Z_INDEX.value))

    def get_height(self, include_units: bool = False) -> str:
        """
        Get the computed height of the root node. Must return as a string because of the possibility of included units.

        :param include_units: Include the units of height (typically "px") if True, otherwise return only the numeric
            value (as a str).

        :returns: The computed height of the root node as a string.

        :raises TimeoutException: If the root node (and therefore the View) is not found in the DOM.
        """
        return self._root.get_computed_height(include_units=include_units)

    def get_width(self, include_units: bool = False) -> str:
        """
        Get the computed width of the root node. Must return as a string because of the possibility of included units.

        :param include_units: Include the units of width (typically "px") if True, otherwise return only the numeric
            value (as a str).

        :returns: The computed width of the root node as a string.

        :raises TimeoutException: If the root node (and therefore the View) is not found in the DOM.
        """
        return self._root.get_computed_width(include_units=include_units)

    def get_origin(self) -> Point:
        """
        Get the Cartesian Coordinate of the upper-left corner of the root node, measured from the
        top-left of the viewport.

        :returns: The Cartesian Coordinate of the upper-left corner of the root node, measured from the
            top-left of the viewport.

        :raises TimeoutException: If the root node (and therefore the View) is not found in the DOM.
        """
        return self._root.get_origin()

    def is_using_absolute_position(self) -> bool:
        """
        Determine if this instance of the View is using absolute positioning (as opposed to relative).

        :returns: True, if this instance of the View is using absolute positioning - False otherwise.

        :raises TimeoutException: If the root node (and therefore the View) is not found in the DOM.
        """
        return self._get_wrapper_div().value_of_css_property(property_name=CSS.POSITION.value) == 'absolute'

    def _get_wrapper_div(self) -> WebElement:
        """
        Obtain the wrapper <div> as a WebElement.

        :returns: The actual WebElement which is the wrapper of the `root` node.

        :raises TimeoutException: If the root node (and therefore the View) is not found in the DOM.
        """
        return self._root.find().find_element(By.XPATH, '..')
