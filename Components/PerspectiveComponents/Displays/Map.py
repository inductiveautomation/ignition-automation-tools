from typing import Optional, List, Tuple

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece


class Map(BasicPerspectiveComponent):
    """A Perspective Map Component."""
    _MARKER_CSS = 'div.leaflet-marker-icon.leaflet-interactive'
    _POPUP_CSS = 'div.leaflet-popup'
    _VECTOR_CSS = 'path.leaflet-interactive'
    _ZOOM_IN_BUTTON_LOCATOR = (By.CSS_SELECTOR, '.leaflet-control-zoom-in')
    _ZOOM_OUT_BUTTON_LOCATOR = (By.CSS_SELECTOR, '.leaflet-control-zoom-out')
    _CONTAINER_VIEW_TOOLTIP_PANE_LOCATOR = (By.CSS_SELECTOR, 'div>div>div.view')
    _TOOLTIP_PANE_LOCATOR = (By.CSS_SELECTOR, 'div.leaflet-tooltip-pane')
    _DISPLAYED_VIEW_LOCATOR = (By.CSS_SELECTOR, 'div.view-marker')

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
        self._map_marker = ComponentPiece(
            locator=(By.CSS_SELECTOR, self._MARKER_CSS),
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._map_vector = ComponentPiece(
            locator=(By.CSS_SELECTOR, self._VECTOR_CSS),
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._map_tooltip_pane = ComponentPiece(
            locator=self._TOOLTIP_PANE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._map_container_from_tooltip_pane = ComponentPiece(
            locator=self._CONTAINER_VIEW_TOOLTIP_PANE_LOCATOR,
            driver=driver,
            parent_locator_list=self._map_tooltip_pane.locator_list,
            poll_freq=poll_freq)
        self._map_displayed_view = ComponentPiece(
            locator=self._DISPLAYED_VIEW_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._map_zoom_in = ComponentPiece(
            locator=self._ZOOM_IN_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._map_zoom_out = ComponentPiece(
            locator=self._ZOOM_OUT_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)

    def click(self, **kwargs) -> None:
        """
        :raises NotImplementError: Please do not blindly click the Map.
        """
        raise NotImplementedError

    def click_marker_by_expected_index(self, marker_index: int) -> None:
        """
        Click a Map marker.

        :param marker_index: The zero-based index of the marker you would like to click.

        :raises TimeoutException: If no markers are present.
        :raises IndexError: If the supplied index is invalid, based on the number of markers found.
        """
        self._map_marker.find_all()[int(marker_index)].click()

    def click_vector_by_expected_index(self, vector_index: int) -> None:
        """
        Click a Map vector.

        :param vector_index: The zero-based index of the vector you would like to click.

        :raises TimeoutException: If no vectors are present.
        :raises IndexError: If the supplied index is invalid, based on the number of vectors found.
        """
        self._map_vector.find_all()[int(vector_index)].click()

    def click_zoom_in_button(self) -> None:
        """
        Click the built-in zoom-in button of the Map.

        :raises TimeoutException: If the built-in zoom-in button is not present.
        """
        self._map_zoom_in.click(binding_wait_time=1)

    def click_zoom_out_button(self) -> None:
        """
        Click the built-in zoom-out button of the Map.

        :raises TimeoutException: If the built-in zoom-out button is not present.
        """
        self._map_zoom_out.click(binding_wait_time=1)

    def get_height_of_popup_wrapper(self, include_units: bool = False) -> str:
        """
        Obtain the height of the container which houses the View inside the internal Popup which was opened by clicking
        on a marker or vector.

        :param include_units: Dictates whether the returned value contains units of measurement.

        :returns: The height of the open Popup as a string value.
        """
        return self._map_container_from_tooltip_pane.get_computed_height(include_units=include_units)

    def get_height_of_tooltip_view_container(self, include_units: bool = False) -> str:
        """
        Obtain the height of the internal tooltip displayed while hovering over a marker or vector.

        :param include_units: Dictates whether the returned value contains units of measurement.

        :returns: The height of the displayed tooltip as a string value.
        """
        return self._map_container_from_tooltip_pane.get_computed_height(include_units=include_units)

    def get_height_of_view_wrapper_div(self, include_units: bool = False) -> str:
        """
        Obtain the height of the internal Popup which was opened by clicking on a marker or vector.

        :param include_units: Dictates whether the returned value contains units of measurement.

        :returns: The height of the open Popup as a string value.
        """
        return self._map_displayed_view.get_computed_height(include_units=include_units)

    def get_width_of_popup_wrapper(self, include_units: bool = False) -> str:
        """
        Obtain the width of the container which houses the View inside the internal Popup which was opened by clicking
        on a marker or vector.

        :param include_units: Dictates whether the returned value contains units of measurement.

        :returns: The width of the open Popup as a string value.
        """
        return self._map_container_from_tooltip_pane.get_computed_width(include_units=include_units)

    def get_width_of_tooltip_view_container(self, include_units: bool = False) -> str:
        """
        Obtain the width of the internal tooltip displayed while hovering over a marker or vector.

        :param include_units: Dictates whether the returned value contains units of measurement.

        :returns: The width of the displayed tooltip as a string value.
        """
        return self._map_container_from_tooltip_pane.get_computed_width(include_units=include_units)

    def get_width_of_view_wrapper_div(self, include_units: bool = False) -> str:
        """
        Obtain the width of the internal Popup which was opened by clicking on a marker or vector.

        :param include_units: Dictates whether the returned value contains units of measurement.

        :returns: The width of the open Popup as a string value.
        """
        return self._map_displayed_view.get_computed_width(include_units=include_units)

    def hover_over_map_marker_by_expected_index(self, index: int) -> None:
        """
        Hover over a map marker in the Map.

        :param index: The zero-based index of the marker to hover over.

        :raises TimeoutException: If no markers are present.
        :raises IndexError: If the supplied index is invalid, based on the number of markers found.
        """
        ActionChains(self.driver).move_to_element(self._map_marker.find_all()[index]).perform()
