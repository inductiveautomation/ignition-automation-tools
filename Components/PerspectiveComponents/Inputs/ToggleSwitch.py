from typing import Tuple, List, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from Components.BasicComponent import ComponentPiece, BasicPerspectiveComponent
from Helpers.CSSEnumerations import CSS
from Helpers.IAAssert import IAAssert
from Helpers.IAExpectedConditions import IAExpectedConditions as IAec


class ToggleSwitch(BasicPerspectiveComponent):
    """
    A Perspective Toggle Switch Component.

    The preferred term for referencing the state of the Toggle Switch is "active", instead of "on", "selected", or
    "True".
    """
    _TS_THUMB_LOCATOR = (By.CSS_SELECTOR, 'div.ia_toggleSwitch__thumb')
    _TS_TRACK_LOCATOR = (By.CSS_SELECTOR, 'div.ia_toggleSwitch__track')
    _TS_SELECTED_CLASS = 'ia_toggleSwitch__thumb--selected'
    _TS_DISABLED_CLASS = 'ia_toggleSwitch__thumb--disabled'

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
        self.ts_thumb = ComponentPiece(
            locator=self._TS_THUMB_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            description="The circle piece of the Toggle Switch, which slides back and forth within the track.",
            poll_freq=poll_freq)
        self.ts_track = ComponentPiece(
            locator=self._TS_TRACK_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            description="The horizontal oval in which the 'thumb' of the Toggle Switch slides back-and-forth.",
            poll_freq=poll_freq)

    def set_switch(self, should_be_active: bool = True, binding_wait_time: float = 0.5) -> None:
        """
        Set the state of the Toggle Switch. Takes no action if the Toggle Switch already has the specified state.

        :param should_be_active: The desired state of the Toggle Switch.
        :param binding_wait_time: The amount of time to wait after any click action is taken before continuing.

        :raises AssertionError: If unsuccessful in applying the desired state to the Toggle Switch.
        """
        if not self.has_state(expected_state=should_be_active):
            self.click(binding_wait_time=binding_wait_time)
        IAAssert.is_true(
            value=self.has_state(expected_state=should_be_active),
            failure_msg=f"Failed to set the state of a Toggle Switch to {should_be_active}.")

    def get_track_color(self) -> str:
        """
        Obtain the color of the track as a string. Note that different browsers may return this color in different
        formats (RGB vs hex).

        :returns: The color of the track of the Toggle Switch as a string.
        """
        return self.ts_track.get_css_property(property_name=CSS.BACKGROUND_COLOR)

    def has_state(self, expected_state: bool, wait_timeout: float = 1) -> bool:
        """
        Determine whether the Toggle Switch has the supplied state. Preferable to is_active because has_state works
        for both active/inactive states.

        :returns: True, if the Toggle Switch has the specified state - False otherwise.
        """
        try:
            if not expected_state:  # False
                # We are forced to wait a moment here, because Toggle Switches enter the DOM as inactive; attempts to
                # verify if they are False too early will almost always return True because the front-end has not caught
                # up to the backend. This is most prevalent when dealing with a Toggle Switch immediately after it has
                # entered the DOM, like when Popups are opened.
                self.wait_on_binding(0.25)
            return WebDriverWait(driver=self.driver, timeout=wait_timeout).until(
                IAec.function_returns_true(
                    custom_function=self._has_state,
                    function_args={'expected_state': expected_state}))
        except TimeoutException:
            return False

    def is_active(self, wait_timeout: float = 1) -> bool:
        """
        Determine whether the Toggle Switch is currently active (on, True, selected) while waiting up to the specified
        amount of time for the Toggle Switch to become active before reporting. Does not work for waiting until a Toggle
        Switch is inactive. Preferable to use :func:`has_state`.

        :returns: True, if the Toggle Switch becomes active before the specified wait period elapses - False otherwise.
        """
        try:
            return WebDriverWait(
                driver=self.driver, timeout=wait_timeout, poll_frequency=self.poll_freq).until(
                IAec.function_returns_true(
                    custom_function=self._is_active,
                    function_args={}))
        except TimeoutException:
            return False

    def is_enabled(self) -> bool:
        """Determine if the Toggle Switch is currently enabled."""
        return self._TS_DISABLED_CLASS not in self.ts_thumb.find().get_attribute('class')

    def _is_active(self) -> bool:
        """Determine if the Toggle Switch is currently active (on/selected/True/active)."""
        return self._TS_SELECTED_CLASS in self.ts_thumb.find(wait_timeout=0).get_attribute('class')

    def _has_state(self, expected_state: bool) -> bool:
        """Determine whether the Toggle Switch has the supplied state."""
        return self._is_active() == expected_state
