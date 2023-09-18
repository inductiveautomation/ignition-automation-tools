from typing import Union, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from Components.BasicComponent import ComponentPiece
from Helpers.CSSEnumerations import CSS
from Helpers.IAExpectedConditions import IAExpectedConditions as IAec
from Helpers.Point import Point


class Tooltip(ComponentPiece):
    """
    A Tooltip for a Perspective Component, driven by the META category within props. Note that tooltips defined by
    properties outside of META will not work with this class.

    Also, tooltips do not provide insight into their originating component, so all functions contained within this class
    will report on or interact with any tooltip which is displayed.
    """
    _COMPONENT_TOOLTIP_LOCATOR = (By.CSS_SELECTOR, 'div.component-tooltip')
    _TAIL_LOCATOR = (By.CSS_SELECTOR, 'div.tail')

    def __init__(
            self,
            driver: WebDriver,
            wait_timeout: Union[int, float] = 2,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=self._COMPONENT_TOOLTIP_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._tail = ComponentPiece(
            locator=self._TAIL_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=wait_timeout,
            poll_freq=poll_freq)

    def any_component_tooltip_is_displayed(self) -> bool:
        """
        Determine if any tooltips is displayed for any component.

        :returns: True, if any tooltip is displayed for any component.
        """
        try:
            return self.find() is not None
        except TimeoutException:
            return False

    def component_tooltip_has_tail(self) -> bool:
        """
        Determine if the displayed tooltip is rendering a tail as part of its appearance.

        :returns: True, if the displayed tooltip is currently rendering a tail.
        """
        try:
            return self._tail.find() is not None
        except TimeoutException:
            return False

    def get_count_of_tooltips(
            self, expected_count: int = 1, wait_timeout: Union[int, float] = 5, poll_frequency: float = 0.5) -> int:
        """
        Obtain a count of all displayed tooltips.

        :param expected_count: If supplied, we will attempt to wait until this many tooltips are displayed before
            returning a value.
        :param wait_timeout: The amount of time (in seconds) to wait for any tooltips to appear. Use this when tooltips
            contain any configured delay.
        :param poll_frequency: How often to poll the DOM as we wait for an expected count of tooltips.

        :returns: A count of displayed tooltips.
        """
        try:
            WebDriverWait(driver=self.driver, timeout=wait_timeout, poll_frequency=poll_frequency).until(
                IAec.function_returns_true(
                    custom_function=self._expected_number_of_tooltips_displayed,
                    function_args={'expected_count': expected_count}))
            return expected_count
        except TimeoutException:
            pass
        try:
            return len(self.find_all(wait_timeout=1))
        except TimeoutException:
            return 0

    def _get_origin_of_component_tooltip(self) -> Point:
        """
        Obtain the origin (upper-left corner) of a tooltip. If multiple tooltips are present, this will return the
        origin of the tooltip which was rendered first.

        :returns: A two-dimensional point which represents the upper-left corner of the tooltip.

        :raises TimeoutException: If no tooltips are rendered.
        """
        return self.get_origin()

    def get_height_of_component_tooltip(self, include_units: bool = False) -> str:
        """
        Obtain the height of a tooltip, with or without units (usually px). If multiple tooltips are present, this will
        return the height of the tooltip which was rendered first.

        :param include_units: Dictates whether the returned value contains units of measurement (almost always 'px').

        :returns: The height of the first rendered tooltip - with or without units.

        :raises TimeoutException: If no tooltips are rendered.
        """
        return self.get_computed_height(include_units=include_units)

    def get_tail_color(self) -> str:
        """
        Obtain the color in use for the tail of a tooltip as a string.

        :returns: The color in use for the tail of a tooltip. Note that the format of this value will change based on
            the browser in use.

        :raises TimeoutException: If no tooltips are rendered.
        """
        return self._tail.get_css_property(property_name=CSS.BORDER_TOP_COLOR)

    def get_width_of_component_tooltip(self, include_units: bool = False) -> str:
        """
        Obtain the width of a tooltip, with or without units (usually px). If multiple tooltips are present, this will
        return the width of the tooltip which was rendered first.

        :param include_units: Dictates whether the returned value contains units of measurement (almost always 'px').

        :returns: The width of the first rendered tooltip - with or without units.

        :raises TimeoutException: If no tooltips are rendered.
        """
        return self.get_computed_width(include_units=include_units)

    def get_text_of_tooltip(self) -> str:
        """
        Obtain the text present within the tooltip.

        :returns: The currently rendered text of the tooltip. If multiple tooltips are present, this will return the
            text of the tooltip which was rendered first.

        :raises TimeoutException: If no tooltips are rendered.
        """
        return self.get_text()

    def _expected_number_of_tooltips_displayed(self, expected_count: int) -> bool:
        """
        Determine if a specific number of tooltips are displayed.

        :param expected_count: The count of tooltips you expect to be rendered.

        :returns: True, if the currently rendered count of tooltips matches the supplied expected_count value - False
            otherwise.
        """
        try:
            return len(self.find_all(wait_timeout=0)) == expected_count
        except TimeoutException:
            return False
