from typing import Optional, List, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece


class GoogleMap(BasicPerspectiveComponent):
    """A Perspective Google Map Component."""
    _DISMISS_OVERLAY_BUTTON_LOCATOR = (By.CLASS_NAME, 'dismissButton')
    _ZOOM_OUT_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button[title="Zoom out"]')
    _ZOOM_IN_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button[title="Zoom in"]')
    _FULL_SCREEN_BUTTON_LOCATOR = (By.CLASS_NAME, 'fullscreen-control')
    _TILT_MAP_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button[title="Tilt map"]')
    _ROTATE_TILT_MAP_CLOCKWISE_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button[title="Rotate map clockwise"]')
    _ROTATE_TILT_MAP_COUNTERCLOCKWISE_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button[title="Rotate map counterclockwise"]')

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
        self._dismiss_overlay_button = ComponentPiece(
            locator=self._DISMISS_OVERLAY_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._zoom_out_button = ComponentPiece(
            locator=self._ZOOM_OUT_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._zoom_in_button = ComponentPiece(
            locator=self._ZOOM_IN_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._full_screen_button = ComponentPiece(
            locator=self._FULL_SCREEN_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._tilt_map_button = ComponentPiece(
            locator=self._TILT_MAP_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._rotate_tilt_map_clockwise_button = ComponentPiece(
            locator=self._ROTATE_TILT_MAP_CLOCKWISE_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._rotate_tilt_map_counterclockwise_button = ComponentPiece(
            locator=self._ROTATE_TILT_MAP_COUNTERCLOCKWISE_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=1,
            poll_freq=poll_freq)

    def click_dismiss_overlay_button(self) -> None:
        """
        Clicks the dismiss overlay button found when no API key is applied.
        """
        self._dismiss_overlay_button.find().click()

    def click_full_screen_button(self) -> None:
        """
        Clicks the toggle full screen button.
        """
        self._full_screen_button.find().click()

    def click_zoom_out_button(self) -> None:
        """
        Clicks the zoom out button.
        """
        self._zoom_out_button.find().click()

    def click_zoom_in_button(self) -> None:
        """
        Clicks the zoom in button.
        """
        self._zoom_in_button.find().click()

    def click_tilt_map_button(self) -> None:
        """
        Clicks the button to toggle tilt mode, which enables the rotate buttons for supported areas.
        """
        self._tilt_map_button.find().click()

    def click_rotate_tilt_map_clockwise_button(self) -> None:
        """
        Clicks the rotate clockwise button (only visible when tilt is enabled).
        """
        self._rotate_tilt_map_clockwise_button.find().click()

    def click_rotate_tilt_map_counterclockwise_button(self) -> None:
        """
        Clicks the rotate counterclockwise button (only visible when tilt is enabled).
        """
        self._rotate_tilt_map_counterclockwise_button.find().click()
