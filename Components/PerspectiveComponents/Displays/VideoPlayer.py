from enum import Enum
from typing import List, Optional, Tuple, Union

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece, BasicPerspectiveComponent
from Helpers.CSSEnumerations import CSS


class VideoPlayer(BasicPerspectiveComponent):
    """
    A Perspective Video Player Component.

    Note that unlike some other components, the Video Player does not raise AssertionErrors in the event it fails to
    apply some sort of setting. This is because other setting values on other components might drive behaviors and
    logic for a project, whereas setting values on the Video Player is highly likely to only affect an end-user.
    """
    _ERROR_MESSAGE_LOCATOR = (By.CSS_SELECTOR, "span.error-message")
    # central panel
    _PAUSED_OVERLAY_LOCATOR = (By.CSS_SELECTOR, "div.ia_videoPlayerComponent__videoOverlay--paused")
    _CENTRAL_PLAY_BUTTON_LOCATOR = (By.CSS_SELECTOR, "div.central-container.play span")
    _VIDEO_PANEL_LOCATOR = (By.CSS_SELECTOR, "video-element-wrapper")
    # control container
    _CONTROL_CONTAINER_LOCATOR = (By.CSS_SELECTOR, "div.control-container")
    _BASE_CONTROL_LOCATOR = By.CSS_SELECTOR, "div.base-control"
    _PLAY_BUTTON_LOCATOR = (By.CSS_SELECTOR, "div.ia_videoPlayerComponent__controlContainer__playControl")
    _PAUSE_CLASS = "ia_videoPlayerComponent__controlContainer__playControl--playing"
    _PAUSE_BUTTON_LOCATOR = (By.CSS_SELECTOR, f"div.{_PAUSE_CLASS}")
    _SEEK_BAR_LOCATOR = (By.CSS_SELECTOR, "div.ia_videoPlayerComponent__controlContainer__seekBar")
    _SEEK_BAR_HANDLE_LOCATOR = (By.CSS_SELECTOR, "span.slider-handle")
    _ELAPSED_TIME_LOCATOR = (By.CSS_SELECTOR, "span.current-time")
    _DURATION_TIME_LOCATOR = (By.CSS_SELECTOR, "span.duration")
    _VOLUME_CONTROL_ICON_LOCATOR = (By.CSS_SELECTOR, "div.ia_videoPlayerComponent__controlContainer__volumeControl svg")
    _RATE_CONTROL_ICON_LOCATOR = (By.CSS_SELECTOR, "div.ia_videoPlayerComponent__controlContainer__playRateControl svg")
    _FULL_SCREEN_ICON_LOCATOR = (
        By.CSS_SELECTOR, "div.ia_videoPlayerComponent__controlContainer__fullscreenControl svg")
    _CONTROL_POPOVER_LOCATOR = (By.CSS_SELECTOR, "div.ia_videoPlayerComponent__controlPopupContainer")
    _VOLUME_MODAL_SLIDER_HANDLE_LOCATOR = (
        By.CSS_SELECTOR, _SEEK_BAR_HANDLE_LOCATOR[1])
    _VOLUME_PERCENT_LOCATOR = (By.CSS_SELECTOR, "div.slider-active-background")
    _PLAY_RATE_LIST_OPTIONS_LOCATOR = (By.CSS_SELECTOR, 'ul.generic-select-list li')
    _SELECTED_PLAY_RATE_OPTION = (By.CSS_SELECTOR, ".selected")

    class PlayRate(Enum):
        """An enumeration of available options for play-rate."""
        ONE_QUARTER = "0.25"
        ONE_HALF = "0.5"
        NORMAL = "Normal"
        ONE_AND_ONE_QUARTER = "1.25"
        ONE_AND_ONE_HALF = "1.5"
        DOUBLE = "2"
        QUINTUPLE = "5"
        DECUPLE = "10"

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
        self._error_message = ComponentPiece(
            locator=self._ERROR_MESSAGE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._central_panel = ComponentPiece(
            locator=self._VIDEO_PANEL_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._control_container = ComponentPiece(
            locator=self._CONTROL_CONTAINER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._base_controls = ComponentPiece(
            locator=self._BASE_CONTROL_LOCATOR,
            driver=driver,
            parent_locator_list=self._control_container.locator_list,
            poll_freq=poll_freq)
        self._central_play_button = ComponentPiece(
            locator=self._CENTRAL_PLAY_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self._central_panel.locator_list,
            poll_freq=poll_freq)
        self._pause_button = ComponentPiece(
            locator=self._PAUSE_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self._control_container.locator_list,
            poll_freq=poll_freq)
        self._pause_icon = ComponentPiece(
            locator=(By.TAG_NAME, "svg"),
            driver=driver,
            parent_locator_list=self._pause_button.locator_list,
            poll_freq=poll_freq)
        self._play_button = ComponentPiece(
            locator=self._PLAY_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self._control_container.locator_list,
            poll_freq=poll_freq)
        self._play_icon = ComponentPiece(
            locator=(By.TAG_NAME, "svg"),
            driver=driver,
            parent_locator_list=self._play_button.locator_list,
            poll_freq=poll_freq)
        self._seek_bar = ComponentPiece(
            locator=self._SEEK_BAR_LOCATOR,
            driver=driver,
            parent_locator_list=self._control_container.locator_list,
            poll_freq=poll_freq)
        self._seek_handle = ComponentPiece(
            locator=self._SEEK_BAR_HANDLE_LOCATOR,
            driver=driver,
            parent_locator_list=self._seek_bar.locator_list,
            poll_freq=poll_freq)
        self._elapsed_time = ComponentPiece(
            locator=self._ELAPSED_TIME_LOCATOR,
            driver=driver,
            parent_locator_list=self._control_container.locator_list,
            poll_freq=poll_freq)
        self._duration_time = ComponentPiece(
            locator=self._DURATION_TIME_LOCATOR,
            driver=driver,
            parent_locator_list=self._control_container.locator_list,
            poll_freq=poll_freq)
        self._volume_icon = ComponentPiece(
            locator=self._VOLUME_CONTROL_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self._control_container.locator_list,
            poll_freq=poll_freq)
        self._play_rate_icon = ComponentPiece(
            locator=self._RATE_CONTROL_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self._control_container.locator_list,
            poll_freq=poll_freq)
        self._fullscreen_icon = ComponentPiece(
            locator=self._FULL_SCREEN_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self._control_container.locator_list,
            poll_freq=poll_freq)
        self._control_popover = ComponentPiece(
            locator=self._CONTROL_POPOVER_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            poll_freq=poll_freq)
        self._volume_slider_handle = ComponentPiece(
            locator=self._VOLUME_MODAL_SLIDER_HANDLE_LOCATOR,
            driver=driver,
            parent_locator_list=self._control_popover.locator_list,
            poll_freq=poll_freq)
        self._volume_percent = ComponentPiece(
            locator=self._VOLUME_PERCENT_LOCATOR,
            driver=driver,
            parent_locator_list=self._control_popover.locator_list,
            poll_freq=poll_freq)
        self._play_rate_options = ComponentPiece(
            locator=self._PLAY_RATE_LIST_OPTIONS_LOCATOR,
            driver=driver,
            parent_locator_list=self._control_popover.locator_list,
            poll_freq=poll_freq)
        self._selected_play_rate = ComponentPiece(
            locator=self._SELECTED_PLAY_RATE_OPTION,
            driver=driver,
            parent_locator_list=self._control_popover.locator_list,
            poll_freq=poll_freq)

    def all_controls_are_disabled(self) -> bool:
        """
        Determine if all base controls for the Video Player are currently disabled.

        :returns: True, if all controls are currently disabled - False otherwise.

        :raises TimeoutException: If the base controls could not be found.
        """
        all_base_controls = self._base_controls.find_all()
        for elem in all_base_controls:
            if 'disabled' not in elem.get_attribute("class"):
                return False
        return True

    def any_error_message_is_displayed(self) -> bool:
        """
        Determine if any error message is currently displayed.

        :returns: True, if any error message is displayed - False otherwise.
        """
        try:
            return self._error_message.find(1) is not None
        except TimeoutException:
            return False

    def central_play_button_is_displayed(self) -> bool:
        """
        Determine if the central play button is currently displayed.

        :returns: True, if the play button within the video panel is displayed - False otherwise.
        """
        try:
            return self._central_play_button.find(0.5) is not None
        except TimeoutException:
            return False

    def click_central_play_button_if_displayed(self) -> None:
        """
        Click the central play button if it is currently displayed, otherwise do nothing.
        """
        if self.central_play_button_is_displayed():
            self._central_play_button.click()

    def click_central_play_button(self) -> None:
        """
        Click the central play button located in the video panel.

        :raises TimeoutException: If the central play button is not found.
        """
        self._central_play_button.click()

    def click_fullscreen_icon(self) -> None:
        """
        Click the full-screen icon.

        :raises TimeoutException: If the full-screen icon is not present.
        """
        self._fullscreen_icon.click()

    def click_pause(self) -> None:
        """
        Click the pause option in the bottom-left of the Video Player.

        :raises TimeoutException: If the pause option is not present. Expected while the Video Player is already paused.
        :raises ElementClickInterceptedException: If the base controls are configured to hide during times of
            inactivity.
        """
        self._pause_icon.click()

    def click_play(self) -> None:
        """
        Click the play option in the bottom-left of the Video Player.

        :raises TimeoutException: If the play option is not present. Expected while the Video Player is already playing.
        :raises ElementClickInterceptedException: If the base controls are configured to hide during times of
            inactivity.
        """
        self._play_icon.click()

    def click_play_rate_icon(self) -> None:
        """
        Click the play-rate icon (gauge) located in the controls panel.

        :raises ElementClickInterceptedException: If the base controls are configured to hide during times of
            inactivity.
        """
        self._play_rate_icon.click()

    def click_volume_icon(self) -> None:
        """
        Click the volume icon (speaker) located in the controls panel.

        :raises ElementClickInterceptedException: If the base controls are configured to hide during times of
            inactivity.
        """
        self._volume_icon.click(binding_wait_time=0.25)

    def controls_are_displayed(self) -> bool:
        """
        Determine if the controls panel is currently displayed.

        :returns: True, if the controls panel which contains the play/pause options, scrubber, volume, play-rate, and
            full-screen options is displayed.
        """
        try:
            # verify the bottom of the controls panel is 0 relative to the bottom of its parent (the Video Player)
            bottom = self._control_container.get_css_property(property_name=CSS.BOTTOM)
            return (bottom is not None) and (len(bottom.split('px')) > 1) and (int(float(bottom.split('px')[0])) == 0)
        except TimeoutException:
            return False

    def drag_seek_handle_to_time(self, time_as_hour_minute_second_string: str) -> None:
        """
        Drag the seek handle (scrubber) to a specific colon-delimited time. Currently only supports changes in seconds.
        This function takes longer the larger the Video Player is because it drags one pixel at a time.

        :raises ElementClickInterceptedException: If the base controls are configured to hide during times of
            inactivity.
        """
        desired_seconds = time_as_hour_minute_second_string.split(':')[-1]
        current_seconds = self.get_elapsed_time().split(':')[-1]
        directional_modifier = 1 if desired_seconds > current_seconds else -1
        value_needs_adjustment = desired_seconds != current_seconds
        if value_needs_adjustment:
            ActionChains(driver=self.driver).click_and_hold(on_element=self._seek_handle.find()).perform()
        if desired_seconds < current_seconds:
            while desired_seconds < current_seconds:
                ActionChains(driver=self.driver).move_by_offset(xoffset=directional_modifier, yoffset=0).perform()
                current_seconds = self.get_elapsed_time().split(':')[-1]
        elif desired_seconds > current_seconds:
            while desired_seconds > current_seconds:
                ActionChains(driver=self.driver).move_by_offset(xoffset=directional_modifier, yoffset=0).perform()
                current_seconds = self.get_elapsed_time().split(':')[-1]
        if value_needs_adjustment:
            ActionChains(driver=self.driver).release().perform()

    def get_current_play_rate(self) -> str:
        """
        Obtain the current play rate of the Video Player.

        :raises ElementClickInterceptedException: If the base controls are configured to hide during times of
            inactivity.
        """
        if not self._play_rate_options_displayed():
            self._play_rate_icon.click()
        try:
            return self._selected_play_rate.get_text()
        finally:
            self._play_rate_icon.click()

    def get_current_volume(self) -> int:
        """
        Obtain the current volume of the Video Player.

        :returns: The current volume of the Video Player as an integer value.

        :raises ElementClickInterceptedException: If the base controls are configured to hide during times of
            inactivity.
        """
        # When working on QA-1563, we found that .get_css_property() always returns px value instead of %
        # This is on the Selenium side so this method remains using .get_attribute('style') for it to work
        modal_displayed_originally = self._volume_modal_is_displayed()
        if not modal_displayed_originally:
            self._volume_icon.click()
        try:
            return int(self._volume_percent.find(wait_timeout=1).get_attribute("style").split(' ')[-1].split('%')[0])
        finally:
            if not modal_displayed_originally:
                self.click_volume_icon()

    def get_duration(self) -> str:
        """
        Obtain the duration (length) of the currently-loaded video.

        :returns: The duration of the current video as a colon-delimited string. The structure of this string may change
            depending on the length of the video. For example, videos less than one hour long only return minutes and
            seconds (MM:SS).
        """
        return self._duration_time.get_text()

    def get_duration_in_seconds(self) -> int:
        """
        Obtain the duration of the video in a measurement of seconds.

        :returns: The duration of the video in seconds, instead of HH:MM:SS.
        """
        return VideoPlayer._convert_time_to_seconds(time_as_str=self.get_duration())

    def get_elapsed_time(self) -> str:
        """
        Obtain the elapsed time of the video.

        :returns: The elapsed time of the current video as a colon-delimited string. The structure of this string may
            change depending on the length of the video. For example, videos less than one hour long only return minutes
            and seconds (MM:SS).
        """
        return self._elapsed_time.find().text

    def get_elapsed_time_in_seconds(self) -> int:
        """
        Obtain the elapsed time of the video in a measurement of seconds.

        :returns: The elapsed time of the video in seconds, instead of HH:MM:SS.
        """
        return VideoPlayer._convert_time_to_seconds(time_as_str=self.get_elapsed_time())

    def pause_icon_is_displayed(self) -> bool:
        """
        Determine if the pause icon is currently displayed.

        :returns: True, if the pause icon is currently displayed in the control panel. False if the pause icon is not
            currently displayed - expected while the video is currently paused.
        """
        try:
            return self._pause_button.find() is not None
        except TimeoutException:
            return False

    def play_icon_is_displayed(self) -> bool:
        """
        Determine if the play icon is currently displayed.

        :returns: True, if the play icon is currently displayed in the control panel. False if the play icon is not
            currently displayed - expected while the video is currently playing.
        """
        try:
            return self._PAUSE_CLASS not in self._play_button.find().get_attribute("class")
        except TimeoutException:
            return False

    def set_play_rate(self, desired_rate: PlayRate) -> None:
        """
        Set the play rate of the Video Player.

        :param desired_rate: The desired rate as an enumeration.

        :raises ElementClickInterceptedException: If the base controls are configured to hide during times of
            inactivity.
        """
        if desired_rate.value != self.get_current_play_rate():
            if not self._play_rate_options_displayed():
                self._play_rate_icon.click()
                self._select_play_rate(desired_rate=desired_rate)
                self._play_rate_icon.click()

    def set_volume(self, desired_volume: Union[int, str]) -> None:
        """
        Set the volume of the Video Player.

        :param desired_volume: The value (0<=desired_value<=100) to which the volume will be set.

        :raises ElementClickInterceptedException: If the base controls are configured to hide during times of
            inactivity.
        :raises ValueError: If the value is invalid.
        """
        desired_volume = int(desired_volume)
        if (0 > desired_volume) or (desired_volume > 100):
            raise ValueError("Volume only accepts values between 0 and 100.")
        if desired_volume != self.get_current_volume():
            self._set_volume(desired_volume)

    def _play_rate_options_displayed(self) -> bool:
        """Determine if the play-rate options are displayed."""
        return len(self._play_rate_options.find_all(wait_timeout=0.5)) > 0

    def _select_play_rate(self, desired_rate: PlayRate) -> None:
        """Set the play rate of the Video Player."""
        options = self._play_rate_options.find_all()
        for option in options:
            if option.text == desired_rate.value:
                option.click()
                break

    def _set_volume(self, desired_volume: int) -> None:
        """Set the volume of the Video Player."""
        desired_volume = int(desired_volume)
        current_volume = self.get_current_volume()
        directional_modifier = 1 if current_volume > desired_volume else -1
        value_needs_adjustment = current_volume != desired_volume
        if value_needs_adjustment:
            self.click_volume_icon()
            ActionChains(driver=self.driver).click_and_hold(on_element=self._volume_slider_handle.find()).perform()
        while current_volume != desired_volume:
            ActionChains(driver=self.driver).move_by_offset(xoffset=0, yoffset=directional_modifier).perform()
            current_volume = int(self._volume_percent.find(
                wait_timeout=1).get_attribute("style").split(' ')[-1].split('%')[0])
        if value_needs_adjustment:
            ActionChains(driver=self.driver).release().perform()
        if self._volume_modal_is_displayed():
            self.click_volume_icon()

    def _volume_modal_is_displayed(self) -> bool:
        """Determine if the volume modal is displayed."""
        try:
            return self._volume_slider_handle.find(wait_timeout=0.5) is not None
        except TimeoutException:
            return False

    @staticmethod
    def _convert_time_to_seconds(time_as_str: str) -> int:
        """Convert a colon-delimited time string to a count of seconds."""
        if len(time_as_str.split(":")) == 2:
            # ensure the presence of hours in the string
            time_as_str = "00:" + time_as_str
        ftr = [3600, 60, 1]  # seconds in hour, seconds in minute, seconds in second
        return sum([a * b for a, b in zip(ftr, map(int, time_as_str.split(':')))])
