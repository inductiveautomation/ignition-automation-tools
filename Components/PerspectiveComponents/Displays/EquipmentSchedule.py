from enum import Enum
from typing import List, Optional, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece, BasicPerspectiveComponent
from Components.PerspectiveComponents.Common.Dropdown import CommonDropdown
from Components.PerspectiveComponents.Inputs.Button import Button


class Direction(Enum):
    LEFT = 'left'
    RIGHT = 'right'


class EquipmentSchedule(BasicPerspectiveComponent):
    _PRIMARY_HEADER_LOCATOR = (By.CSS_SELECTOR, '.time-range-label')
    _SECONDARY_HEADER_LOCATOR = (By.CSS_SELECTOR, 'div#grouping-header-cells div > span')
    _TERTIARY_HEADER_LOCATOR = (By.CSS_SELECTOR, 'div#header-cells div > p')
    _ZOOM_LEVEL_LOCATOR = (By.CSS_SELECTOR, '.button-group .ia_dropdown')
    _DELETE_BUTTON_LOCATOR = (By.CSS_SELECTOR, '.delete')
    _INCREMENT_BUTTON_LOCATOR = (By.CSS_SELECTOR, '.increment')
    _DECREMENT_BUTTON_LOCATOR = (By.CSS_SELECTOR, '.decrement')
    _ITEMS_LOCATOR = (By.CSS_SELECTOR, 'div.itemList div > span')
    _EVENTS_LOCATOR = (By.CSS_SELECTOR, 'div.scheduled-event')
    _BREAK_EVENTS_LOCATOR = (By.CSS_SELECTOR, '.ia_equipmentScheduleComponent__breakEvent')
    _DOWNTIME_EVENTS_LOCATOR = (By.CSS_SELECTOR, '.ia_equipmentScheduleComponent__downtimeEvent')
    _OVERLAPPING_EVENTS_LOCATOR = (By.CSS_SELECTOR, '.overlapping-event')
    _VISIBLE_OVERLAPPING_EVENTS_LOCATOR = (By.CSS_SELECTOR, '.overlapping-visible-event div > p')

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
        self._primary_header = ComponentPiece(locator=self._PRIMARY_HEADER_LOCATOR, driver=driver, poll_freq=poll_freq)
        self._secondary_header = ComponentPiece(
            locator=self._SECONDARY_HEADER_LOCATOR,
            driver=driver,
            poll_freq=poll_freq)
        self._tertiary_header = ComponentPiece(
            locator=self._TERTIARY_HEADER_LOCATOR,
            driver=driver,
            poll_freq=poll_freq)
        self._zoom_level = CommonDropdown(locator=self._ZOOM_LEVEL_LOCATOR, driver=driver, poll_freq=poll_freq)
        self._delete_button = Button(locator=self._DELETE_BUTTON_LOCATOR, driver=driver, poll_freq=poll_freq)
        self._increment_button = Button(locator=self._INCREMENT_BUTTON_LOCATOR, driver=driver, poll_freq=poll_freq)
        self._decrement_button = Button(locator=self._DECREMENT_BUTTON_LOCATOR, driver=driver, poll_freq=poll_freq)
        self._items = ComponentPiece(locator=self._ITEMS_LOCATOR, driver=driver, poll_freq=poll_freq)
        self._events = ComponentPiece(locator=self._EVENTS_LOCATOR, driver=driver, poll_freq=poll_freq)
        self._break_events = ComponentPiece(locator=self._BREAK_EVENTS_LOCATOR, driver=driver, poll_freq=poll_freq)
        self._downtime_events = ComponentPiece(
            locator=self._DOWNTIME_EVENTS_LOCATOR,
            driver=driver,
            poll_freq=poll_freq)
        self._overlapping_events = ComponentPiece(
            locator=self._OVERLAPPING_EVENTS_LOCATOR,
            driver=driver,
            poll_freq=poll_freq)
        self._visible_overlapping_events = ComponentPiece(
            locator=self._VISIBLE_OVERLAPPING_EVENTS_LOCATOR,
            driver=driver,
            poll_freq=poll_freq)
        self._internal_pieces = {}

    def click_increment_zoom_level(self) -> None:
        """
        Increment the zoom level of the Equipment Schedule by clicking the built-in UI.
        Method scrolls to the zoom level element because increment button is out of frame with FireFox automation.
        """
        self._zoom_level.scroll_to_element()
        self._increment_button.click(binding_wait_time=1)

    def click_decrement_zoom_level(self) -> None:
        """
        Decrement the zoom level of the Equipment Schedule by clicking the built-in UI.
        Method scrolls to the zoom level element because decrement button is out of frame with FireFox automation.
        """
        self._zoom_level.scroll_to_element()
        self._decrement_button.click(binding_wait_time=1)

    def click_delete_event_button(self) -> None:
        """
        Click the delete button.

        :raises TimeoutException: If the Delete button is configured to not be allowed, and is therefore not present.

        Method scrolls to zoom level element because delete button is out of frame with Firefox automation.
        """
        self._zoom_level.scroll_to_element()
        self._delete_button.click(binding_wait_time=1)

    def delete_button_is_displayed(self) -> bool:
        """
        Determine if the Delete button is currently displayed.

        :returns: True, if the Delete button is currently displayed - False otherwise.
        """
        try:
            return self._delete_button.find().is_displayed()
        except TimeoutException:
            return False

    def get_count_of_break_events(self) -> int:
        """
        Obtain a count of "break" events from the Equipment Schedule Component.

        :returns: A count of events which are classified as a break.
        """
        try:
            return len(self._break_events.find_all())
        except TimeoutException:
            return 0

    def get_count_of_downtime_events(self) -> int:
        """
        Obtain a count of "downtime" events from the Equipment Schedule Component.

        :returns: A count of events which are classified as downtime.
        """
        try:
            return len(self._downtime_events.find_all())
        except TimeoutException:
            return 0

    def get_count_of_overlapping_events(self) -> int:
        """
        Obtain a count of "overlapping" events from the Equipment Schedule Component.

        :returns: A count of events which are overlapping other events.
        """
        try:
            return len(self._overlapping_events.find_all())
        except TimeoutException:
            return 0

    def get_count_of_scheduled_events(self) -> int:
        """
        Obtain a count of all events displayed in the Equipment Schedule Component.

        :returns: A count of all events displayed in the Equipment Schedule Component, regardless of type.
        """
        try:
            return len(self._events.find_all())
        except TimeoutException:
            return 0

    def get_text_of_primary_header(self) -> str:
        """
        Obtain the text of the Primary Header.

        :returns: The text of the primary.

        :raises TimeoutException: If the Primary Header is not Present.
        """
        return self._primary_header.get_text()

    def get_text_of_secondary_headers(self) -> List[str]:
        """
        Obtain the text of all currently displayed secondary headers.

        :returns: A list which contains the text of every displayed secondary header.

        :raises TimeoutException: If no secondary headers are present.
        """
        return [_.text for _ in self._secondary_header.find_all()]

    def get_text_of_tertiary_headers(self) -> List[str]:
        """
        Obtain the text of all currently displayed tertiary headers.

        :returns: A list which contains the text of every displayed tertiary header.

        :raises TimeoutException: If no tertiary headers are present.
        """
        return [_.text for _ in self._tertiary_header.find_all()]

    def get_text_of_items(self) -> List[str]:
        """
        Obtain the text of every configured item which is currently displayed.

        :returns: A list which contains the text of every displayed item configured for the Equipment Schedule
            Component.

        :raises TimeoutException: If no items are present.
        """
        return [_.text for _ in self._items.find_all()]

    def get_text_of_scheduled_events(self) -> List[str]:
        """
        Obtain the text of every displayed scheduled event for the Equipment Schedule Component.

        :returns: A list which contains the text of every displayed event.

        :raises TimeoutException: If no events are present.
        """
        return [_.text for _ in self._events.find_all()]

    def get_text_of_visible_overlapping_events(self) -> List[str]:
        """
        Obtain the text of every overlapping scheduled event for the Equipment Schedule Component.

        :returns: A list which contains the text of every overlapping displayed event.

        :raises TimeoutException: If no overlapping events are present.
        """
        return [_.text for _ in self._visible_overlapping_events.find_all()]

    def add_event(self, row_index: int, column_index: int, count_of_columns_to_span: int) -> None:
        """
        Add an event to the Equipment Schedule Component. Presumes the supplied row and column indices do not already
        have an event present.

        :param row_index: The zero-based index for the row we will target while adding the new event.
        :param column_index: The zero-based index for the column we will target while adding the new event.
        :param count_of_columns_to_span: The count of columns the new event should span.

        :raises ClickInterceptedException: If the supplied indices identify a cell which already has an event in place.
        """
        cell_element = self._get_internal_piece(
            locator=(By.CSS_SELECTOR, f'[data-column="{column_index}"][data-row="{row_index}"]'))
        cell_element.scroll_to_element(align_to_top=True)
        offset = int(cell_element.get_computed_width(include_units=False))
        ActionChains(driver=self.driver) \
            .click_and_hold(on_element=cell_element.find()) \
            .pause(2) \
            .move_by_offset(xoffset=offset * count_of_columns_to_span, yoffset=0) \
            .release() \
            .perform()
        cell_element.wait_on_binding(1)

    def move_event(self, item_id: str, event_id: str, count_of_columns_to_drag: int) -> None:
        """
        Move an existing event within the Equipment Schedule Component.

        :param item_id: The id of the item which contains the event. This is not necessarily the name of the item.
        :param event_id: The id of the event which will be moved.
        :param count_of_columns_to_drag: The count of columns to drag the event. Negative values will drag the event to
            the left, and positive values will drag the event to the right.

        :raises TimeoutException: If no event with the specified ids is present.
        """
        event_element = self._get_internal_piece(
            locator=(By.CSS_SELECTOR, f'[data-itemid="{item_id}"][data-eventid="{event_id}"]'))
        event_element.scroll_to_element(align_to_top=True)
        offset = int(float(event_element.get_computed_width(include_units=False)))
        ActionChains(driver=self.driver) \
            .click_and_hold(on_element=event_element.find()) \
            .move_by_offset(xoffset=offset * count_of_columns_to_drag, yoffset=0) \
            .release() \
            .perform()
        event_element.wait_on_binding(1)

    def resize_event(self, item_id: str, event_id: str, count_of_columns_to_drag: int, direction: Direction) -> None:
        """
        Resize an existing event within the Equipment Schedule Component.

        :param item_id: The id of the item which contains the event. This is not necessarily the name of the item.
        :param event_id: The id of the event which will be moved.
        :param count_of_columns_to_drag: The count of columns to drag the event. Negative values will drag the event
            resize handle to the left, and positive values will drag the event resize handle to the right.
        :param direction: Dictates whether we are resizing the left or the right of the event.

        :raises TimeoutException: If no event with the specified ids is present.
        """
        self.select_event(item_id=item_id, event_id=event_id)
        event_element = self._get_internal_piece(
            locator=(By.CSS_SELECTOR, f'[data-itemid="{item_id}"][data-eventid="{event_id}"]'))
        offset = int(float(event_element.get_computed_width(include_units=False)))  # we need the width of the event
        event_resize_element = self._get_internal_piece(
            locator=(
                By.CSS_SELECTOR,
                f'[data-itemid-eventid="{item_id}_{event_id}"][data-direction="{direction.value}"]'))
        event_resize_element.scroll_to_element(align_to_top=True)
        ActionChains(driver=self.driver) \
            .click_and_hold(on_element=event_resize_element.find()) \
            .pause(2) \
            .move_by_offset(xoffset=offset * count_of_columns_to_drag, yoffset=0) \
            .release() \
            .perform()
        event_resize_element.wait_on_binding(1)

    def event_is_resizable(self, item_id: str, event_id: str, direction: Direction) -> bool:
        """
        Determine if an event is resizable on a given side.

        :param item_id: The id of the item which contains the event. This is not necessarily the name of the item.
        :param event_id: The id of the event which will checked.
        :param direction: Dictates which side of the event we are checking for the ability to be resized.

        :returns: True, if the specified event may be resized on the specified side - False otherwise.

        :raises TimeoutException: If no event with the specified ids is present.
        """
        try:
            event = self._get_internal_piece(
                locator=(
                    By.CSS_SELECTOR,
                    f'[data-itemid-eventid="{item_id}_{event_id}"][data-direction="{direction.value}"]'))
            return event.find() is not None
        except TimeoutException:
            return False

    def select_event(self, item_id: str, event_id: str) -> None:
        """
        Select an event by clicking it.

        :param item_id: The id of the item which contains the event. This is not necessarily the name of the item.
        :param event_id: The id of the event which will selected/clicked.

        :raises TimeoutException: If no event with the specified ids is present.
        """
        self._get_internal_piece(
            locator=(
                By.CSS_SELECTOR,
                f'[data-itemid="{item_id}"][data-eventid="{event_id}"]')).click(binding_wait_time=1)

    def set_zoom_level(self, text: str):
        self._zoom_level.select_option_by_text_if_not_selected(option_text=text, binding_wait_time=1)

    def _get_internal_piece(self, locator: Tuple[By, str]) -> ComponentPiece:
        """
        Obtain some internal piece of the Equipment Schedule (almost always an event) via the locator which uniquely
        identifies the internal piece.

        :returns: The ComponentPiece identified by the provided locator.
        """
        event = self._internal_pieces.get(locator)
        if not event:
            event = ComponentPiece(
                locator=locator,
                driver=self.driver,
                parent_locator_list=self.locator_list)
            self._internal_pieces[locator] = event
        return event
