import re
from enum import Enum
from typing import Optional, List, Tuple, Union

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Helpers.GeographicPoint import GeographicPoint
from Helpers.IAExpectedConditions import IAExpectedConditions as IAec


class MapType(Enum):
    """
    The selectable main map types displayed by both versions of the UI that drive how the map is rendered.

    Selecting 'Map' renders the Google Map as a roadmap while selecting 'Satellite' renders the map with
    satellite imagery.
    """
    MAP = 'Map'
    SATELLITE = 'Satellite'


class MapSubtype(Enum):
    """
    The selectable map subtypes that are uniquely available to each main map type('Map' or 'Satellite').

    With type 'Map' selected the 'Terrain' subtype is available to render the Google Map with a topographical overlay.
    With type 'Satellite' selected the 'Labels' subtype is available to render the Google Map with labels for
    geographical locations.
    """
    TERRAIN = 'Terrain'
    LABELS = 'Labels'


class GoogleMap(BasicPerspectiveComponent):
    """A Perspective Google Map Component."""
    _DISMISS_OVERLAY_BUTTON_LOCATOR = (By.CLASS_NAME, 'dismissButton')
    _ZOOM_OUT_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button[title="Zoom out"]')
    _ZOOM_IN_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button[title="Zoom in"]')
    _FULL_SCREEN_BUTTON_LOCATOR = (By.CLASS_NAME, 'fullscreen-control')
    _TILT_MAP_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button[title="Tilt map"]')
    _ROTATE_TILT_MAP_CLOCKWISE_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button[title="Rotate map clockwise"]')
    _ROTATE_TILT_MAP_COUNTERCLOCKWISE_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button[title="Rotate map counterclockwise"]')
    _EXTERNAL_LINK_LOCATOR = (By.CSS_SELECTOR, 'a[title="Open this area in Google Maps (opens a new window)"]')
    _GENERAL_CLOSE_POPUP_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button[title="Close"]')
    # Map type controls div classes will be one of the following, depending on its layout (configured by
    # mapType.controlStyle). The wildcard allows us to locate it in either layout.
    # In dropdown mode: gmnoprint gm-style-mtc
    # In horizontal_bar mode: gmnoprint gm-style-mtc-bbw
    _MAP_TYPE_CONTROLS_LOCATOR = (By.CSS_SELECTOR, 'div.gmnoprint[class*=" gm-style-mtc"]')

    class _MapTypeControls(ComponentPiece):
        """
        An interface for the Google Map's mapType controls UI.
        Google Map's mapType controls can either appear as a dropdown menu or as a horizontal bar.
        """
        _DROPDOWN_MAP_TYPE_CONTROLS_LOCATOR = (By.CSS_SELECTOR, 'button[title="Change map style"]')
        _MAP_CONTROL_LOCATOR = (By.CSS_SELECTOR, 'li[title="Show street map"], button[title="Show street map"]')
        _SATELLITE_CONTROL_LOCATOR = (By.CSS_SELECTOR, 'li[title="Show satellite imagery"], '
                                                       'button[title="Show satellite imagery"]')
        _LABELS_LIST_ITEM_LOCATOR = (By.CSS_SELECTOR, 'li[aria-label="Labels"]')
        _TERRAIN_LIST_ITEM_LOCATOR = (By.CSS_SELECTOR, 'li[aria-label="Terrain"]')

        def __init__(
                self,
                locator: Tuple[By, str],
                driver: WebDriver,
                parent_locator_list: Optional[list] = None,
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
            self._dropdown_map_type_controls = ComponentPiece(
                locator=self._DROPDOWN_MAP_TYPE_CONTROLS_LOCATOR,
                driver=driver,
                parent_locator_list=None,
                wait_timeout=1,
                poll_freq=poll_freq)
            self._map_control = ComponentPiece(
                locator=self._MAP_CONTROL_LOCATOR,
                driver=driver,
                parent_locator_list=None,
                wait_timeout=1,
                poll_freq=poll_freq)
            self._satellite_control = ComponentPiece(
                locator=self._SATELLITE_CONTROL_LOCATOR,
                driver=driver,
                parent_locator_list=None,
                wait_timeout=1,
                poll_freq=poll_freq)
            self._labels_list_item = ComponentPiece(
                locator=self._LABELS_LIST_ITEM_LOCATOR,
                driver=driver,
                parent_locator_list=None,
                wait_timeout=1,
                poll_freq=poll_freq)
            self._terrain_list_item = ComponentPiece(
                locator=self._TERRAIN_LIST_ITEM_LOCATOR,
                driver=driver,
                parent_locator_list=None,
                wait_timeout=1,
                poll_freq=poll_freq)

        def set_map_type(self, map_type: Union[MapType, MapSubtype], should_be_selected: bool) -> None:
            """
            Sets the map to the map type option whose text matches the supplied map type parameter.

            :param map_type: The map type or subtype to set the Google Map to.
            :param should_be_selected: Decides what selected state the subtype should be in.

            :raises TimeoutException: If the MapType UI is not found.
            """
            if self.map_type_dropdown_is_displayed():
                self.expand_map_type_dropdown()
            if type(map_type) == MapType:
                self._set_map_base_type(map_type=map_type)
            else:
                self._set_map_subtype(map_subtype=map_type, should_be_selected=should_be_selected)
            if self.map_type_dropdown_is_displayed():
                self.collapse_map_type_dropdown()

        def get_selected_map_type(self) -> Union[MapType, MapSubtype]:
            """
            Obtains the selected map type option.

            :returns: The selected type or subtype option found.

            :raises TimeoutException: If the MapType UI is not found.
            """
            main_map_type = self._check_selected_main_map_type()
            if main_map_type.value == MapType.MAP.value and self.terrain_checkbox_is_selected():
                return MapSubtype.TERRAIN
            elif main_map_type.value == MapType.SATELLITE.value and self.labels_checkbox_is_selected():
                return MapSubtype.LABELS
            else:
                return main_map_type

        def labels_checkbox_is_selected(self) -> bool:
            """
            Checks if the 'Labels' option is selected.

            :returns: True if the 'Labels' checkbox is selected, False otherwise.

            :raises TimeoutException: If the MapType UI is not found.
            """
            return self._labels_list_item.find(wait_timeout=0).get_attribute('aria-checked') == 'true'

        def terrain_checkbox_is_selected(self) -> bool:
            """
            Checks if the 'Terrain' option is selected.

            :returns: True if the 'Terrain' checkbox is selected, False otherwise.

            :raises TimeoutException: If the MapType UI is not found.
            """
            return self._terrain_list_item.find(wait_timeout=0).get_attribute('aria-checked') == 'true'

        def map_type_dropdown_is_displayed(self):
            """
            Determines if the dropdown menu version of the map type control UI is displayed.

            :returns: True if the dropdown menu is displayed, False otherwise.
            """
            try:
                return self._dropdown_map_type_controls.find(wait_timeout=0) is not None
            except TimeoutException:
                return False

        def map_type_dropdown_is_expanded(self) -> bool:
            """
            Determines if the dropdown menu version of the map type control UI is expanded.

            :returns: True if the dropdown menu is expanded, False otherwise.

            :raises TimeoutException: If the MapType UI is not found or dropdown is not displayed.
            """
            return self._dropdown_map_type_controls.find(wait_timeout=0).get_attribute(name='aria-expanded') == 'true'

        def expand_map_type_dropdown(self):
            """
            Clicks the dropdown menu version of the map type controls UI to expand the dropdown.

            :raises TimeoutException: If the MapType UI is not found or dropdown is not displayed.
            """
            if not self.map_type_dropdown_is_expanded():
                self._dropdown_map_type_controls.click()
                self.wait.until(method=IAec.function_returns_true(
                    custom_function=self.map_type_dropdown_is_expanded,
                    function_args={}))

        def collapse_map_type_dropdown(self):
            """
            Clicks the dropdown menu version of the map type controls UI to collapse the dropdown.

            :raises TimeoutException: If the MapType UI is not found or dropdown is not displayed.
            """
            if self.map_type_dropdown_is_expanded():
                self._dropdown_map_type_controls.click()
                self.wait.until(method=IAec.function_returns_false(
                    custom_function=self.map_type_dropdown_is_expanded,
                    function_args={}))

        def _set_map_base_type(self, map_type: MapType) -> None:
            """
            Sets the Google Map base type to the type that matches the supplied type.

            :param map_type: The type to set the Google Map to.

            :raises TimeoutException: If the MapType UI is not found or if this method is called for the dropdown menu
                version.
            """
            if map_type.value == MapType.MAP.value:
                self._map_control.click()
                if self.terrain_checkbox_is_selected():
                    self._terrain_list_item.click(wait_timeout=0)
            else:
                self._satellite_control.click()
                if self.labels_checkbox_is_selected():
                    self._labels_list_item.click(wait_timeout=0)

        def _set_map_subtype(self, map_subtype: MapSubtype, should_be_selected: bool) -> None:
            """
            Sets the Google Map to the type that matches the supplied subtype.

            :param map_subtype: The subtype to set the Google Map to.
            :param should_be_selected: Decides what selected state the subtype should be in.

            :raises TimeoutException: If the MapType UI is not found or if this method is called for the dropdown menu
                version.
            """
            if map_subtype.value == MapSubtype.TERRAIN.value:
                self._map_control.click()
                if self.terrain_checkbox_is_selected() != should_be_selected:
                    self.wait.until(ec.presence_of_element_located(self._TERRAIN_LIST_ITEM_LOCATOR)).click()
                    self.wait_on_binding()
            else:
                self._satellite_control.click()
                if self.labels_checkbox_is_selected() != should_be_selected:
                    self.wait.until(ec.presence_of_element_located(self._LABELS_LIST_ITEM_LOCATOR)).click()
                    self.wait_on_binding()

        def _check_selected_main_map_type(self) -> MapType:
            """
            Obtains the selected main map type.

            :returns: The currently selected main map type.
            """
            if self.map_type_dropdown_is_displayed():
                return MapType.MAP if MapType.MAP.value == self._dropdown_map_type_controls.get_text() \
                    else MapType.SATELLITE
            else:
                if self._map_control.find(wait_timeout=0).get_attribute(name='aria-checked') == 'true':
                    return MapType.MAP
                else:
                    return MapType.SATELLITE

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
        self._external_link = ComponentPiece(
            locator=self._EXTERNAL_LINK_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._map_type_controls = self._MapTypeControls(
            locator=self._MAP_TYPE_CONTROLS_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._general_close_popup_button = ComponentPiece(
            locator=self._GENERAL_CLOSE_POPUP_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=1,
            poll_freq=poll_freq)

    def click_dismiss_overlay_button(self) -> None:
        """
        Clicks the dismiss overlay button found when no API key is applied.
        """
        self._dismiss_overlay_button.click()

    def click_full_screen_button(self, binding_wait_time: float = 0.5) -> None:
        """
        Clicks full screen button.

        :param binding_wait_time: The amount of time (in seconds) to wait after the click before allowing code
            to continue.
        """
        self._full_screen_button.click(binding_wait_time=binding_wait_time)

    def click(self, x_offset: int = 0, y_offset: int = 0) -> None:
        """
        Attempts to find the Google Map component and then click at the supplied pixel offset.

        :param x_offset: The x offset in pixels to move the cursor to after locating the component.
        :param y_offset: The y offset in pixels to move the cursor to after locating the component.
        """
        ActionChains(driver=self.driver)\
            .move_to_element_with_offset(to_element=self.find(), xoffset=x_offset, yoffset=y_offset) \
            .click()\
            .perform()

    def click_rotate_map_clockwise_button(self, binding_wait_time: float = 0.5) -> None:
        """
        Clicks the rotate clockwise button.

        :param binding_wait_time: The amount of time (in seconds) to wait after the click before allowing code
            to continue.

        :raises TimeoutException: If the rotate clockwise button is not found.
        """
        self._rotate_tilt_map_clockwise_button.click(binding_wait_time=binding_wait_time)

    def click_rotate_map_counterclockwise_button(self, binding_wait_time: float = 0.5) -> None:
        """
        Clicks the rotate counterclockwise button.

        :param binding_wait_time: The amount of time (in seconds) to wait after the click before allowing code
            to continue.

        :raises TimeoutException: If the rotate counterclockwise button is not found.
        """
        self._rotate_tilt_map_counterclockwise_button.click(binding_wait_time=binding_wait_time)

    def click_tilt_map_button(self, binding_wait_time: float = 0.5) -> None:
        """
        Clicks the tilt control button.

        :param binding_wait_time: The amount of time (in seconds) to wait after the click before allowing code
            to continue.
        """
        self._tilt_map_button.click(binding_wait_time=binding_wait_time)

    def click_zoom_in_button(self, binding_wait_time: float = 0.5) -> None:
        """
        Clicks the zoom in button.

        :param binding_wait_time: The amount of time (in seconds) to wait before allowing code to continue.
        """
        self._zoom_in_button.click(binding_wait_time=binding_wait_time)

    def click_zoom_out_button(self, binding_wait_time: float = 0.5) -> None:
        """
        Clicks the zoom out button.

        :param binding_wait_time: The amount of time (in seconds) to wait after the click before allowing code
            to continue.
        """
        self._zoom_out_button.click(binding_wait_time=binding_wait_time)

    def close_all_expanded_popups(self) -> None:
        """
        Closes all general popups such as popups from markers, KML, and clickable icons.
        The list is reversed before iterating to close popups in the highest z-order first.
        """
        all_general_popups = self._general_close_popup_button.find_all(wait_timeout=0)
        all_general_popups.reverse()
        for close_popup_button in all_general_popups:
            close_popup_button.click()

    def dismiss_overlay_button_is_displayed(self) -> bool:
        """
        Determines if the dismiss overlay button is displayed when no API key is applied.

        :returns: True if the button is found, False otherwise.
        """
        try:
            return self._dismiss_overlay_button.find(wait_timeout=0).is_displayed()
        except TimeoutException:
            return False

    def double_click(self, x_offset: int = 0, y_offset: int = 0) -> None:
        """
        Double-click the Google Map at the supplied pixel offset.

        :param x_offset: The x offset in pixels to move the cursor to after locating the component.
        :param y_offset: The y offset in pixels to move the cursor to after locating the component.
        """
        ActionChains(driver=self.driver)\
            .move_to_element_with_offset(to_element=self.find(wait_timeout=0), xoffset=x_offset, yoffset=y_offset)\
            .double_click()\
            .perform()

    def double_right_click_map_with_offset(self, x_offset: int = 0, y_offset: int = 0) -> None:
        """
        Attempts to find the Google Map component and then double right click at the supplied pixel offset.

        :param x_offset: The x offset in pixels to move the cursor to after locating the component.
        :param y_offset: The y offset in pixels to move the cursor to after locating the component.
        """
        ActionChains(driver=self.driver)\
            .move_to_element_with_offset(to_element=self.find(wait_timeout=0), xoffset=x_offset, yoffset=y_offset)\
            .context_click()\
            .context_click()\
            .perform()

    def get_full_screen_button_height(self, include_units: bool = False) -> str:
        """
        Obtains the computed height of the full screen button.

        :returns: The computed height of the full screen button.
        """
        return self._full_screen_button.get_computed_height(include_units=include_units)

    def get_full_screen_button_width(self, include_units: bool = False) -> str:
        """
        Obtains the computed width of the full screen button.

        :returns: The computed width of the full screen button.
        """
        return self._full_screen_button.get_computed_width(include_units=include_units)

    def get_map_center(self) -> GeographicPoint:
        """
        Obtains the central latitude and longitude point of the Google Map's current position.

        :returns: A GeographicPoint representing the latitude and longitude of the center of the map.
        """
        try:
            self.wait.until(ec.presence_of_element_located(self._EXTERNAL_LINK_LOCATOR))
        except TimeoutException as toe:
            raise TimeoutException(
                f"Failed to get the map center position because the link that we parse it from was not present.") \
                from toe
        center = re.search(
            '(?<=ll=)(.*)(?=&z)',
            self._external_link.find(wait_timeout=0).get_attribute('href')).group().split(',')
        return GeographicPoint(latitude=float(center[0]), longitude=float(center[1]))

    def get_map_type(self) -> Union[MapType, MapSubtype]:
        """
        Obtains the selected map type option.

        :returns: The selected map type option.
        """
        return self._map_type_controls.get_selected_map_type()

    def get_map_type_controls_height(self, include_units: bool = False) -> str:
        """
        Obtains the computed width of the map type controls, in either layout setting (dropdown or horizontal bar.)

        :returns: The computed height of the map type controls.
        """
        return self._map_type_controls.get_computed_height(include_units=include_units)

    def get_map_type_controls_width(self, include_units: bool = False) -> str:
        """
        Obtains the computed width of the map type controls, in either layout setting (dropdown or horizontal bar.)

        :returns: The computed width of the map type controls.
        """
        return self._map_type_controls.get_computed_width(include_units=include_units)

    def get_map_zoom(self) -> float:
        """
        Obtains the current zoom of the Google Map.

        :returns: A float representation of the current zoom level of the map.
        """
        return float(re.search('(?<=&z=)(.*)(?=&t)', self._external_link.find().get_attribute('href')).group())

    def get_popup_count(self) -> int:
        """
        Obtains the count of all general popups.

        :returns: The number of all open general popups.
        """
        try:
            return len(self._general_close_popup_button.find_all(wait_timeout=0))
        except TimeoutException:
            return 0

    def get_zoom_in_button_height(self, include_units: bool = False) -> str:
        """
        Obtains the computed height of the zoom in button.

        :returns: The computed height of the zoom in button.
        """
        return self._zoom_in_button.get_computed_height(include_units=include_units)

    def get_zoom_in_button_width(self, include_units: bool = False) -> str:
        """
        Obtains the computed width of the zoom in button.

        :returns: The computed width of the zoom in button.
        """
        return self._zoom_in_button.get_computed_width(include_units=include_units)

    def get_zoom_out_button_height(self, include_units: bool = False) -> str:
        """
        Obtains the computed height of the zoom out button.

        :returns: The computed height of the zoom out button.
        """
        return self._zoom_out_button.get_computed_height(include_units=include_units)

    def get_zoom_out_button_width(self, include_units: bool = False) -> str:
        """
        Obtains the computed width of the zoom out button.

        :returns: The computed width of the zoom out button.
        """
        return self._zoom_out_button.get_computed_width(include_units=include_units)

    def right_click(self, x_offset: int = 0, y_offset: int = 0) -> None:
        """
        Attempts to find the Google Map component and then right click at the supplied pixel offset.

        :param x_offset: The x offset in pixels to move the cursor to after locating the component.
        :param y_offset: The y offset in pixels to move the cursor to after locating the component.
        """
        ActionChains(driver=self.driver)\
            .move_to_element_with_offset(to_element=self.find(), xoffset=x_offset, yoffset=y_offset)\
            .context_click()\
            .perform()

    def select_google_map_type(self, selection_option: MapType, should_be_selected: bool = True) -> None:
        """
        Selects the Google Map type option that corresponds to the supplied option.

        :param selection_option: The map type option to select.
        :param should_be_selected:
        """
        self._map_type_controls.set_map_type(map_type=selection_option, should_be_selected=should_be_selected)

    def tilt_controls_are_displayed(self) -> bool:
        """
        Determines if the tilt map control button is displayed.

        :returns: True if the tilt map control button is displayed, False otherwise.
        """
        try:
            return self._tilt_map_button.find().is_displayed()
        except TimeoutException:
            return False

    def wait_for_popup_to_appear(self) -> bool:
        """
        Waits for a general popup to appear. The popup source can be from markers, KML, clickable icons, etc.
        """
        try:
            return self.wait.until(IAec.element_is_fully_in_viewport(
                driver=self.driver,
                locator=self._GENERAL_CLOSE_POPUP_BUTTON_LOCATOR)) is not None
        except TimeoutException:
            return False

    def wait_for_tilt_control_button_to_appear(self) -> bool:
        """
        Waits for the tilt control button to be displayed.
        """
        try:
            return self.wait.until(IAec.element_is_fully_in_viewport(
                driver=self.driver,
                locator=self._TILT_MAP_BUTTON_LOCATOR)) is not None
        except TimeoutException:
            return False

    def zoom_in_button_is_enabled(self) -> bool:
        """
        Determines if the zoom in button is enabled.

        :returns: True if the zoom in button is enabled, False otherwise.
        """
        return self._zoom_in_button.find(wait_timeout=0).is_enabled()

    def zoom_out_button_is_enabled(self) -> bool:
        """
        Determines if the zoom out button is enabled.

        :returns: True if the zoom out button is enabled, False otherwise.
        """
        return self._zoom_out_button.find(wait_timeout=0).is_enabled()
