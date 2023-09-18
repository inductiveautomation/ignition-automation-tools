from typing import List, Optional, Tuple, Union

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.color import Color

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Helpers.CSSEnumerations import CSS
from Helpers.IAExpectedConditions import IAExpectedConditions


class Thermometer(BasicPerspectiveComponent):
    """A Perspective Thermometer Component."""
    _GLASS_LOCATOR = (By.CSS_SELECTOR, 'g > path.ia_thermometerComponent__glass')
    _INTERVAL_LOCATOR = (By.CSS_SELECTOR, 'line.ia_thermometerComponent__interval')
    _LABELS_LOCATOR = (By.TAG_NAME, 'text')
    _LIQUID_LOCATOR = (By.CSS_SELECTOR, 'g > path.ia_thermometerComponent__liquid')
    _STROKE_LOCATOR = (By.CSS_SELECTOR, 'g')
    _TICK_LABEL_LOCATOR = (By.CSS_SELECTOR, 'text.ia_thermometerComponent__tickLabel')
    _TICK_LOCATOR = (By.CSS_SELECTOR, 'line.ia_thermometerComponent__tick')
    _UNIT_LABEL_LOCATOR = (By.CSS_SELECTOR, 'text.ia_thermometerComponent__unit')
    _VALUE_LABEL_LOCATOR = (By.CSS_SELECTOR, 'text.ia_thermometerComponent__valueDisplay')

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 2,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._glass = ComponentPiece(
            locator=self._GLASS_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._interval = ComponentPiece(
            locator=self._INTERVAL_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._labels = ComponentPiece(
            locator=self._LABELS_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._liquid = ComponentPiece(
            locator=self._LIQUID_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._stroke = ComponentPiece(
            locator=self._STROKE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._tick = ComponentPiece(
            locator=self._TICK_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._tick_label = ComponentPiece(
            locator=self._TICK_LABEL_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._unit_label = ComponentPiece(
            locator=self._UNIT_LABEL_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._value_label = ComponentPiece(
            locator=self._VALUE_LABEL_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)

    def get_all_interval_colors(self, wait_timeout: float = 0) -> List[str]:
        """
        Obtain a list of all interval colors as strings.

        :param wait_timeout: The amount of time (in seconds) to wait for the Thermometer to appear before returning.

        :returns: A list containing the color of all intervals of the thermometer as strings. Note that different
            browsers may return these values in different formats (RGB vs hex).

        :raises TimeoutException: If no intervals are found.
        """
        return [
            Color.from_string(interval.value_of_css_property(CSS.STROKE.value)).hex
            for interval in self._interval.find_all(wait_timeout=wait_timeout)
        ]

    def get_all_tick_colors(self, wait_timeout: float = 0) -> List[str]:
        """
        Obtain a list of all tick colors as strings.

        :param wait_timeout: The amount of time (in seconds) to wait for the Thermometer to appear before returning.

        :returns: A list containing the color of all ticks of the thermometer as strings. Note that different
            browsers may return these values in different formats (RGB vs hex).

        :raises TimeoutException: If no ticks are found.
        """
        return [
            Color.from_string(tick.value_of_css_property(CSS.STROKE.value)).hex
            for tick in self._tick.find_all(wait_timeout=wait_timeout)
        ]

    def get_all_tick_label_colors(self, wait_timeout: float = 0) -> List[str]:
        """
        Obtain a list of all tick label colors as strings.

        :param wait_timeout: The amount of time (in seconds) to wait for the Thermometer to appear before returning.

        :returns: A list containing the color of all tick labels of the thermometer as strings. Note that different
            browsers may return these values in different formats (RGB vs hex).

        :raises TimeoutException: If no tick labels are found.
        """
        return [
            Color.from_string(tick_label.value_of_css_property(CSS.FILL.value)).hex
            for tick_label in self._tick_label.find_all(wait_timeout=wait_timeout)
        ]

    def get_color_of_labels(self, label_index=0) -> str:
        """
        Obtain the color in use for a specific label.

        :param label_index: The zero-based index of the label you would like the color of. These labels include the
            units label, all tick labels, and the value label, and so the count of labels is dependent on the
            configuration of the Thermometer.

        :raises TimeoutException: If no labels are found.
        :raises IndexError: If the supplied index is invalid based on the count of labels found.
        """
        return Color.from_string(
            self._labels.find_all()[label_index].value_of_css_property(CSS.COLOR.value)
        ).hex

    def get_displayed_value(self) -> float:
        """
        Obtain the displayed value of the Thermometer.

        :raises TimeoutException: If the Thermometer is not currently displaying a value label.
        """
        return float(self._value_label.get_text())

    def get_displayed_value_font_size(self) -> str:
        """
        Obtain the font size of the value label.

        :raises TimeoutException: If the Thermometer is not currently displaying a value label.
        """
        return self._value_label.find().value_of_css_property(CSS.FONT_SIZE.value)

    def get_glass_color(self, wait_timeout: float = 0) -> str:
        """
        Obtain the color of the glass of the Thermometer as a string.

        :param wait_timeout: The amount of time (in seconds) to wait for the Thermometer to appear before returning.

        :returns: The color of the Thermometer's glass as a string. Note that different
            browsers may return these values in different formats (RGB vs hex).

        :raises TimeoutException: In the event the glass of the Thermometer could not be located.
        """
        return Color.from_string(
            self._glass.find(wait_timeout=wait_timeout).value_of_css_property(CSS.STROKE.value)
        ).hex

    def get_list_of_levels(self) -> List[str]:
        """
        Obtain the text of all tick labels.

        :returns: All tick labels as strings.

        :raises TimeoutException: If no tick labels are found.
        """
        return self.wait.until(
            IAExpectedConditions.function_returns_true(
            custom_function=self._get_list_of_levels,
            function_args={}
        ))

    def get_mercury_color(self, wait_timeout: float = 0) -> str:
        """
        Obtain the color (fill) of the mercury within the Thermometer.

        :param wait_timeout: The amount of time (in seconds) to wait for the Thermometer to appear before returning.

        :returns: The mercury color (fill) for the Thermometer as a string.  Note that different
            browsers may return these values in different formats (RGB vs hex).

        :raises TimeoutException: In the event no mercury could be located.
        """
        return Color.from_string(
            self._liquid.find(wait_timeout=wait_timeout).value_of_css_property(CSS.FILL.value)
        ).hex

    def get_count_of_intervals(self, wait_timeout: float = 0) -> int:
        """
        Obtain a count of currently displayed tick labels.

        :param wait_timeout: The amount of time (in seconds) to wait for the Thermometer to appear before returning.

        :returns: A count of interval displayed for the Thermometer.
        """
        try:
            return len(self._interval.find_all(wait_timeout=wait_timeout))
        except TimeoutException:
            return 0

    def get_stroke_width_of_glass(self) -> float:
        """
        Obtain the width of the glass of the Thermometer.

        :raises TimeoutException: In the event the glass could not be located.
        """
        return float(self._stroke.find().value_of_css_property(
            CSS.STROKE_WIDTH.value).split("px")[0])

    def get_temperature_font_color(self) -> str:
        """
        Obtain the font color in use for the value label.

        :returns: The color in use for the value label as a string. Note that different
            browsers may return these values in different formats (RGB vs hex).

        :raises TimeoutException: If the value label is not currently displayed.
        """
        return Color.from_string(self._value_label.find().value_of_css_property(CSS.COLOR.value)).hex

    def get_unit_type(self,  wait_timeout: float = 0) -> str:
        """
        Obtain the units in use for the Thermometer.

        :param wait_timeout: The amount of time (in seconds) to wait for the Thermometer to appear before returning.

        :returns: The units displayed in the unit label.

        :raises TimeoutException: If the units label is not currently displayed.
        """
        return self._unit_label.find(wait_timeout=wait_timeout).text[1:]

    def get_unit_color(self, wait_timeout: float = 0) -> str:
        """
        Obtain the font color in use for the units label.

        :param wait_timeout: The amount of time (in seconds) to wait for the Thermometer to appear before returning.

        :returns: The color in use for the units label as a string. Note that different
            browsers may return these values in different formats (RGB vs hex).

        :raises TimeoutException: If the units label is not currently displayed.
        """
        return Color.from_string(
            self._unit_label.find(wait_timeout=wait_timeout).value_of_css_property(CSS.FILL.value)
        ).hex

    def _get_list_of_levels(self) -> Union[List[str], bool]:
        """Obtain the text of all tick labels."""
        try:
            all_labels = self._labels.find_all()
            levels = []
            for label in all_labels:
                # this is less than ideal, but we're checking that we are only using the labels
                # on the side of the thermometer.
                if label.get_attribute('x') == all_labels[0].get_attribute('x'):
                    levels.append(label.text)
            return levels
        except StaleElementReferenceException:
            # doesn't raise the exception - it just returns that it failed to get the values
            return False
