from typing import Optional, List, Tuple

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Components.PerspectiveComponents.Common.ComponentModal import ComponentModal
from Components.PerspectiveComponents.Common.Icon import CommonIcon
from Helpers.IASelenium import IASelenium


class HorizontalMenu(BasicPerspectiveComponent):
    """A Perspective Horizontal Menu Component."""
    _MENU_ITEM_LOCATOR = (By.CSS_SELECTOR, "div.horizontal-menu-menu-item")
    _CHILD_MENU_ITEM_LOCATOR = (By.CSS_SELECTOR, '.horizontal-menu-menu-item span')
    _SIDE_SCROLL_AREA_LOCATOR = (By.CSS_SELECTOR, 'div.side-nav')
    _SIDE_SCROLL_CLICKABLE_AREA_LOCATOR = (By.CSS_SELECTOR, "span.icon-wrapper")

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 5,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._menu_items = ComponentPiece(
            locator=self._MENU_ITEM_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._child_item_modal = ComponentModal(driver=driver)
        self._child_menu_items = ComponentPiece(
            locator=self._CHILD_MENU_ITEM_LOCATOR,
            driver=driver,
            parent_locator_list=self._child_item_modal.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._side_scroll_areas = ComponentPiece(
            locator=self._SIDE_SCROLL_AREA_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._side_scroll_clickable_area = ComponentPiece(
            locator=self._SIDE_SCROLL_AREA_LOCATOR,
            driver=driver,
            parent_locator_list=self._side_scroll_areas.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._menu_item_coll = {}
        self._child_item_coll = {}
        self._top_level_menu_item_icon_coll = {}

    def base_item_has_icon(self, text_of_base_item: str) -> bool:
        """
        Determine whether an option at the top-most level is displaying an icon.

        :returns: True, if an icon is displayed - False otherwise.
        """
        try:
            return self._get_top_level_item_icon(
                text_of_base_item=text_of_base_item).find().is_displayed()
        except TimeoutException:
            return False

    def base_item_is_visible(self, text_of_base_item: str) -> bool:
        """
        Determine whether an option with the supplied text is present at the top-most level.

        :returns: True, if an option with the supplied text is present at the top-most level - False otherwise.
        """
        try:
            return self._get_top_level_menu_item(
                text_of_base_item=text_of_base_item).find().is_displayed()
        except TimeoutException:
            return False

    def can_scroll_left(self) -> bool:
        """
        Determine if the Horizontal Menu currently allows for scrolling to the left.
        """
        try:
            return 'shown' in self._side_scroll_areas.find_all()[0].get_attribute('class')
        except TimeoutException:
            return False

    def can_scroll_right(self) -> bool:
        """
        Determine if the Horizontal Menu currently allows for scrolling to the right.
        """
        try:
            return 'shown' in self._side_scroll_areas.find_all()[1].get_attribute('class')
        except TimeoutException:
            return False

    def child_item_has_icon(self, text_of_child_item: str) -> bool:
        """
        Determine whether an item at any child level with the supplied text is displaying an icon.

        :returns: True, if a child item with the supplied text is displaying an icon  - False otherwise.
        """
        try:
            return self._get_child_item_icon(
                text_of_child_item=text_of_child_item).find() is not None
        except TimeoutException:
            return False

    def child_item_is_visible_by_text(self, text_of_child_item: str) -> bool:
        """
        Determine if a child item with the supplied text is displayed.

        :returns: True, if a child item is displayed which has the exact supplied text - False otherwise.
        """
        try:
            return self._get_child_menu_item(
                text_of_child_item=text_of_child_item).find().is_displayed()
        except TimeoutException:
            return False

    def child_items_are_visible(self) -> bool:
        """
        Determine if any child options are visible, meaning a top-level option with children was clicked. Note that
        due to the nature of the children this would also report True if any other modal is open on the
        screen - including Popups, Docked Views, or child items of other Horizontal Menus.

        :returns: True, if child items (or any modal) is found - False otherwise.
        """
        try:
            return len(self._child_menu_items.find_all()) > 0
        except TimeoutException:
            return False

    def click_visible_base_item(self, text_of_base_item: str, binding_wait_time: float = 0) -> None:
        """
        Click a base-level item by text.

        :raises NoSuchElementException: If unable to locate any top-level item with the supplied text.
        """
        while (not self.base_item_is_visible(
                text_of_base_item=text_of_base_item)) \
                and (self.is_compressed()) \
                and self.can_scroll_right():
            self.short_scroll(scroll_right=True)
        while (not self.base_item_is_visible(
                text_of_base_item=text_of_base_item)) \
                and (self.is_compressed()) \
                and self.can_scroll_left():
            self.short_scroll(scroll_right=False)
        if not self.base_item_is_visible(
                text_of_base_item=text_of_base_item):
            raise NoSuchElementException(f'No item with text of \'{text_of_base_item}\' could be found')
        self._get_top_level_menu_item(
            text_of_base_item=text_of_base_item).click(binding_wait_time=binding_wait_time)

    def click_visible_child_item(self, text_of_child_item: str) -> None:
        """
        Click a base-level item by text.

        :raises TimeoutException: If unable to locate any child item with the supplied text.
        """
        self._get_child_menu_item(
            text_of_child_item=text_of_child_item).click()

    def get_icon_id_from_base_item(self, text_of_base_item: str) -> str:
        """
        Obtain the library and id of the icon in use by the base-level item with the supplied text as a slash-delimited
        string.
        """
        return self._get_top_level_item_icon(
            text_of_base_item=text_of_base_item).get_icon_name()

    def get_icon_id_from_child_item(self, text_of_child_item: str) -> str:
        """
        Obtain the library and id of the icon in use by the child item with the supplied text as a slash-delimited
        string.
        """
        return self._get_child_item_icon(
            text_of_child_item=text_of_child_item).get_icon_name()

    def get_list_of_base_level_items(self) -> List[str]:
        """
        Obtain the text for all base-level items.
        """
        return [item.text for item in self._menu_items.find_all()]

    def is_compressed(self) -> bool:
        """
        Determine if the Horizontal Menu currently displays that a user may scroll either left or right.

        :returns: True, if a user may currently scroll the Horizontal Menu left, right, or both - False if a user
            may not scroll the Horizontal Menu in either direction.
        """
        try:
            return self.can_scroll_right() or self.can_scroll_left()
        except TimeoutException:
            return False

    def scroll_to_max(self, scroll_right: bool) -> None:
        """
        Scroll the Horizontal Menu as far as it can scroll (left/right).

        :param scroll_right: If True, the Horizontal Menu will be scrolled right. If False, the Horizontal Menu will
            be scrolled left.
        """
        can_scroll_in_direction = self.can_scroll_right if scroll_right else self.can_scroll_left()
        while can_scroll_in_direction():
            self.short_scroll(scroll_right=scroll_right)

    def short_scroll(self, scroll_right: bool) -> None:
        """
        Scroll the Horizontal Menu (left/right) a small amount. Useful when searching for a desired top-level item.

        :param scroll_right: If True, the Horizontal Menu will be scrolled right. If False, the Horizontal Menu
            will be scrolled left.
        """
        side_nav_to_click = self._side_scroll_clickable_area.find_all()[1 if scroll_right else 0]
        IASelenium(driver=self.driver).long_click(web_element=side_nav_to_click)

    def _get_child_menu_item(self, text_of_child_item: str) -> ComponentPiece:
        """
        Retrieve a child item Component, or construct a new one if it doesn't exist already.
        """
        item = self._child_item_coll.get(text_of_child_item)
        if not item:
            # Here, we're using the Component Modal as the direct parent WITHOUT including a reference to the actual
            # component, even though the modal is typically a CHILD of the component. There are edge cases
            # (fullscreen mode) where this is not always the case, so we can't force the longer locator.
            item = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'.horizontal-menu-menu-item[data-label="{text_of_child_item}"]'),
                driver=self.driver,
                parent_locator_list=self._child_item_modal.locator_list,
                wait_timeout=2,
                poll_freq=self.poll_freq)
            self._child_item_coll[text_of_child_item] = item
        return item

    def _get_top_level_menu_item(self, text_of_base_item: str) -> ComponentPiece:
        """
        Retrieve a top-level item Component, or construct a new one if it doesn't exist already.
        """
        item = self._menu_item_coll.get(text_of_base_item)
        if not item:
            item = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'{self._MENU_ITEM_LOCATOR[1]}[data-label="{text_of_base_item}"]'),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                wait_timeout=2,
                poll_freq=self.poll_freq)
            self._menu_item_coll[text_of_base_item] = item
        return item

    def _get_child_item_icon(self, text_of_child_item: str) -> CommonIcon:
        """
        Retrieve a child item ICON Component, or construct a new one if it doesn't exist already.
        """
        icon = self._top_level_menu_item_icon_coll.get(text_of_child_item)
        if not icon:
            icon = CommonIcon(
                locator=(By.CSS_SELECTOR, 'svg'),
                driver=self.driver,
                parent_locator_list=self._get_child_menu_item(
                    text_of_child_item=text_of_child_item).locator_list,
                wait_timeout=1,
                poll_freq=self.poll_freq)
            self._top_level_menu_item_icon_coll[text_of_child_item] = icon
        return icon

    def _get_top_level_item_icon(self, text_of_base_item: str) -> CommonIcon:
        """
        Retrieve a top-level item ICON Component, or construct a new one if it doesn't exist already.
        """
        icon = self._top_level_menu_item_icon_coll.get(text_of_base_item)
        if not icon:
            icon = CommonIcon(
                locator=(By.CSS_SELECTOR, 'svg'),
                driver=self.driver,
                parent_locator_list=self._get_top_level_menu_item(
                    text_of_base_item=text_of_base_item).locator_list,
                wait_timeout=1,
                poll_freq=self.poll_freq)
            self._top_level_menu_item_icon_coll[text_of_base_item] = icon
        return icon
