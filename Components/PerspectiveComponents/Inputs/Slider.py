from typing import Tuple, List, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece, BasicPerspectiveComponent


class Slider(BasicPerspectiveComponent):
    """A Perspective Slider Component."""
    _WRAPPER_LOCATOR = (By.CSS_SELECTOR, 'div.slider')
    _LABEL_LOCATOR = (By.CSS_SELECTOR, 'span.slider-mark-text')
    _HANDLE_LOCATOR = (By.CSS_SELECTOR, 'div[role="slider"]')
    _RAIL_LOCATOR = (By.CSS_SELECTOR, 'div.slider-rail')
    _TRACK_LOCATOR = (By.CSS_SELECTOR, 'div.slider-track')

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 3,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._wrapper = ComponentPiece(
            locator=self._WRAPPER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._rail = ComponentPiece(
            locator=self._RAIL_LOCATOR,
            driver=driver,
            parent_locator_list=self._wrapper.locator_list,
            poll_freq=poll_freq)
        self._track = ComponentPiece(
            locator=self._TRACK_LOCATOR,
            driver=driver,
            parent_locator_list=self._wrapper.locator_list,
            poll_freq=poll_freq)
        self._handle = ComponentPiece(
            locator=self._HANDLE_LOCATOR,
            driver=driver,
            parent_locator_list=self._wrapper.locator_list,
            poll_freq=poll_freq)
        self._labels = ComponentPiece(
            locator=self._LABEL_LOCATOR,
            driver=driver,
            parent_locator_list=self._wrapper.locator_list,
            poll_freq=poll_freq)

    def click(self, wait_timeout: int = 1, binding_wait_time: float = 0.5) -> None:
        """
        :raises NotImplementedError: Clicking a Slider serves no purpose and risks setting the Slider to an unknown
            value. Please use click_handle instead.
        """
        raise NotImplementedError("Please do not blindly click the Slider.")

    def click_handle(self, binding_wait_time: float = 0.5) -> None:
        """
        Click the handle of the Slider. Note that this has the potential to change the value of the slider because
        different browser drivers click in different locations within the handle.
        """
        self._handle.click(binding_wait_time=binding_wait_time)

    def drag_to_percent_of_axis(self, percent: float) -> None:
        """
        Drag the Slider to a percent of its axis. Typically only useful for stepped Sliders, where interstitial values
        may not be reached via traditional means anyway.
        """
        potential_distance = self.get_computed_height() if self.is_vertically_oriented() else self.get_computed_width()
        current_percent = float(self.get_current_value()) / float(self.get_max()) * 100.0
        percent = percent - current_percent
        pixels_to_drag = int(
            round(
                float(
                    potential_distance) * float(
                    percent) / 100.0,
                0))
        self._drag_by_pixel_count(
            pixel_count=pixels_to_drag)

    def drag_to_value(self, value: int, max_attempts: int = 150) -> None:
        """
        Drag the handle of the Slider to a specific value.

        :param value: The value you would like to have the Slider reflect.
        :param max_attempts: The count of times we will drag the Slider by 1 pixel before giving up. This argument
            acts as a safeguard against infinite loops when a value may not be reached for any reason. For sliders which
            span many pixels, you may need to provide higher values here.


        :raises ValueError: If the Slider is not successfully set to the supplied value.
        """
        value = int(value)
        x_step = 1
        y_step = 0
        if self.is_vertically_oriented():
            x_step = abs(x_step - 1)
            y_step = abs(y_step - 1)

        attempts = 0
        if int(self.get_current_value()) < value:
            ActionChains(driver=self.driver).click_and_hold(on_element=self._handle.find()).perform()
            while (int(self.get_current_value()) < value) \
                    and (int(self.get_max()) > int(self.get_current_value())) \
                    and (attempts < max_attempts):
                attempts += 1
                ActionChains(driver=self.driver).move_by_offset(x_step, (y_step * -1.0)).perform()
            ActionChains(driver=self.driver).release().perform()
        elif int(self.get_current_value()) > value:
            ActionChains(driver=self.driver).click_and_hold(on_element=self._handle.find()).perform()
            while (int(self.get_current_value()) > value) \
                    and (int(self.get_min()) < int(self.get_current_value())) \
                    and (attempts < max_attempts):
                attempts += 1
                ActionChains(driver=self.driver).move_by_offset((x_step * -1.0), y_step).perform()
            ActionChains(driver=self.driver).release().perform()
        if self.get_current_value() != value:
            raise ValueError(
                f"Failed to set the Slider to a value of {value} after trying up to {max_attempts} times.")

    def get_current_value(self) -> int:
        """Obtain the current value of the Slider."""
        return int(float(self._handle.find().get_attribute("aria-valuenow")))

    def get_handle_color(self) -> str:
        """Obtain the current color of the Slider handle as a string."""
        return self._handle.find().value_of_css_property('border-bottom-color')

    def get_labels_as_list(self) -> List[str]:
        """Obtain the labels currently displayed by the Slider. An empty list denotes no labels are displayed."""
        try:
            return [_.text for _ in self._labels.find_all()]
        except TimeoutException:
            return []

    def get_max(self) -> int:
        """Obtain the maximum value the Slider may be set to."""
        return int(float(self._handle.find().get_attribute("aria-valuemax")))

    def get_min(self) -> int:
        """Obtain the minimum value the Slider may be set to."""
        return int(float(self._handle.find().get_attribute("aria-valuemin")))

    def get_track_color(self) -> str:
        """Obtain the current color of the Slider track as a string."""
        return self._track.find().value_of_css_property('background-color')

    def is_displaying_labels(self) -> bool:
        """Determine if the Slider is currently displaying any labels."""
        return len(self.get_labels_as_list()) > 0

    def is_enabled(self) -> bool:
        """Determine if the Slider is currently enabled."""
        return self._handle.find().get_attribute("aria-disabled") == "false"

    def is_vertically_oriented(self) -> bool:
        """
        Determine if the Slider is vertically oriented. A vertical orientation means the Slider handle would be dragged
        up and down instead of left-to-right.
        """
        return 'slider-vertical' in self._wrapper.find().get_attribute("class")

    def _drag_by_pixel_count(self, pixel_count: int) -> None:
        """
        Drag the Slider handle by some number of pixels.
        """
        x_step = 0 if self.is_vertically_oriented() else pixel_count
        y_step = pixel_count if self.is_vertically_oriented() else 0
        ActionChains(driver=self.driver)\
            .click_and_hold(on_element=self._handle.find())\
            .move_by_offset(xoffset=x_step, yoffset=y_step)\
            .release()\
            .perform()
