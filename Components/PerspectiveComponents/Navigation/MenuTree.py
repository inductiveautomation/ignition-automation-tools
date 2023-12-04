from typing import Tuple, Union, Optional, List

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Components.PerspectiveComponents.Common.Icon import CommonIcon
from Helpers.CSSEnumerations import CSSPropertyValue
from Helpers.IAAssert import IAAssert
from Helpers.IAExpectedConditions import IAExpectedConditions as IAec
from Helpers.Point import Point


class MenuTree(BasicPerspectiveComponent):

    def __init__(
            self,
            driver: WebDriver,
            locator: Tuple[Union[By, str], str],
            parent_locator_list: Optional[Tuple[Union[By, str], str]] = None,
            wait_timeout: float = 1):
        BasicPerspectiveComponent.__init__(
            self,
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout)
        self._item_icons = {}
        self._item_nav_icons = {}
        self._items = {}
        self._submenu_icons = {}
        self._submenu_items = {}
        self._submenu_nav_icons = {}
        self._submenu_group = ComponentPiece(
            locator=(By.CSS_SELECTOR, "div.submenu-group"),
            driver=driver,
            parent_locator_list=self.locator_list)
        self._header = ComponentPiece(
            locator=(By.CSS_SELECTOR, "div.menu-header"),
            driver=driver,
            parent_locator_list=self._submenu_group.locator_list
        )

    def back_action_is_present_in_submenu(self) -> bool:
        """
        Determine if a 'Back' action is present in the current submenu.

        :return: True, if a 'Back' action is available to the user - False otherwise.
        """
        try:
            return self._get_submenu_back_action().find(wait_timeout=0) is not None
        except TimeoutException:
            return False

    def click_back_action_within_submenu(self, until_at_top_level: bool = False) -> None:
        """
        Click the 'Back' action available for the currently expanded submenu. If no submenu is expanded, no action is
        taken.

        :raises TimeoutException: If no 'Back' action is currently available, or if no submenu is displayed.
        """
        if self.submenu_is_expanded():
            self._get_submenu_back_action().find_all(wait_timeout=0)[-1].click()
            self._get_submenu_back_action().wait_on_binding(0.5)  # allow submenu time to be removed from DOM
            try:
                if until_at_top_level and self._get_submenu_back_action().find(wait_timeout=0) is not None:
                    self.click_back_action_within_submenu(until_at_top_level=until_at_top_level)
            except TimeoutException:
                pass
        if until_at_top_level:
            IAAssert.is_not_true(
                value=self.submenu_is_expanded(),
                failure_msg="Failed to get the Menu Tree back to the top level.")

    def click_menu_item(self, item_text: str, is_in_submenu: bool = False) -> None:
        """
        Click an item or submenu item within the Menu Tree
        :param item_text: The text of the item you would like to click.
        :param is_in_submenu: Clarifies if this item should be expected in the top-level menu or a submenu.

        :raises ElementClickInterceptedException: If the item is covered by a submenu item at a deeper level.

        :raises TimeoutException: If no item (or submenu item) exists with the specified text.
        """
        target = self._get_submenu_item(item_text=item_text) if is_in_submenu else self._get_item(item_text=item_text)
        target.click(binding_wait_time=0.5)  # wait for potential submenu animation

    def get_css_value_of_icon_in_use_by_menu_item(
            self,
            item_text: str,
            property_name: Union[CSSPropertyValue, str],
            is_in_submenu: bool = False) -> str:
        """
        Obtain the CSS property value of the specified property for.

        :param property_name: The CSS property name of which you would like the value.
        :param item_text: The text of the item for which you would like information about the icon.
        :param is_in_submenu: Clarifies if this item should be expected in the top-level menu or a submenu.

        :returns: The CSS property value in use by the icon identified by the specified item text.

        :raises TimeoutException: If no icon is displayed for the specified item.
        """
        return self._get_item_icon(
            item_text=item_text, is_in_submenu=is_in_submenu).get_css_property(property_name=property_name)

    def get_css_value_of_nav_icon_in_use_by_menu_item(
            self,
            item_text: str,
            property_name: Union[CSSPropertyValue, str],
            is_in_submenu: bool = False) -> str:
        """
        Obtain the CSS property value in use by the nav icon identified by the specified item text.

        :param property_name: The CSS property name of which you would like the value.
        :param item_text: The text of the item for which you would like information about the icon.
        :param is_in_submenu: Clarifies if this item should be expected in the top-level menu or a submenu.

        :returns: The CSS property value in use by the nav icon identified by the specified item text.

        :raises TimeoutException: If no nav icon is displayed for the specified item.
        """
        return self._get_item_nav_icon(
            item_text=item_text, is_in_submenu=is_in_submenu).get_css_property(property_name=property_name)

    def get_header_text(self) -> str:
        """
        Obtain the current header text of the submenu.

        :return: The header text of the currently displayed submenu.

        :raises TimeoutException: If no header text or no submenu is displayed.
        """
        """
        Unfortunately, nested submenus render over other submenus instead of replacing them, so we must always look
        for the last (top-most) header text.
        """
        return self._header.find_all()[-1].text

    def get_name_of_icon_in_use_by_menu_item(self, item_text: str, is_in_submenu: bool = False) -> str:
        """
        Obtain the library and id of the Icon as a slash-delimited string.

        Example: material/perm_identity denotes the 'perm_identity' svg from the 'material' library.

        :param item_text: The text of the item for which you would like information about the icon.
        :param is_in_submenu: Clarifies if this item should be expected in the top-level menu or a submenu.

        :returns: The library and id of the svg in use by the Icon Component as a slash-delimited string.

        :raises TimeoutException: If no icon is displayed for the specified item.
        """
        return self._get_item_icon(item_text=item_text, is_in_submenu=is_in_submenu).get_icon_name()

    def get_name_of_nav_icon_in_use_by_menu_item(self, item_text: str, is_in_submenu: bool = False) -> str:
        """
        Obtain the library and id of the Icon as a slash-delimited string.

        Example: material/perm_identity denotes the 'perm_identity' svg from the 'material' library.

        :param item_text: The text of the item for which you would like information about the icon.
        :param is_in_submenu: Clarifies if this item should be expected in the top-level menu or a submenu.

        :returns: The library and id of the svg in use by the Icon Component as a slash-delimited string.

        :raises TimeoutException: If no nav icon is displayed for the specified item.
        """
        return self._get_item_nav_icon(item_text=item_text, is_in_submenu=is_in_submenu).get_icon_name()

    def get_origin_of_icon(self, item_text: str, is_in_submenu: bool = False) -> Point:
        """
        Obtain the origin of an item icon.

        :param item_text: The text of the associated item.
        :param is_in_submenu: Clarifies whether to search for the item in a submenu.

        :return: A two-dimensional Point which defines the position of the upper-left corner of the icon.
        """
        return self._get_item_icon(item_text=item_text, is_in_submenu=is_in_submenu).get_origin()

    def get_origin_of_nav_icon(self, item_text: str, is_in_submenu: bool = False) -> Point:
        """
        Obtain the origin of an item's nav icon.

        :param item_text: The text of the associated item.
        :param is_in_submenu: Clarifies whether to search for the item in a submenu.

        :return: A two-dimensional Point which defines the position of the upper-left corner of the nav icon.
        """
        return self._get_item_nav_icon(item_text=item_text, is_in_submenu=is_in_submenu).get_origin()

    def get_termination_of_icon(self, item_text: str, is_in_submenu: bool = False) -> Point:
        """
        Obtain the termination of an item icon.

        :param item_text: The text of the associated item.
        :param is_in_submenu: Clarifies whether to search for the item in a submenu.

        :return: A two-dimensional Point which defines the position of the bottom-right corner of the icon.
        """
        return self._get_item_icon(item_text=item_text, is_in_submenu=is_in_submenu).get_origin()

    def get_termination_of_nav_icon(self, item_text: str, is_in_submenu: bool = False) -> Point:
        """
        Obtain the termination of an item's nav icon.

        :param item_text: The text of the associated item.
        :param is_in_submenu: Clarifies whether to search for the item in a submenu.

        :return: A two-dimensional Point which defines the position of the bottom-right corner of the nav icon.
        """
        return self._get_item_nav_icon(item_text=item_text, is_in_submenu=is_in_submenu).get_origin()

    def get_text_of_all_submenu_items(self) -> List[str]:
        """
        Obtain the text of all submenu items available within all expanded submenus of the Menu Tree.

        :return: A List, where each entry is the text of an item present in an expanded submenu of the Menu Tree.
        """
        return [_.text for _ in self._get_submenu_item().find_all()]

    def get_text_of_all_top_level_items(self) -> List[str]:
        """
        Obtain the text of all items available at the top level of the Menu Tree.

        :return: A List, where each entry is the text of an item at the top level of the Menu Tree.
        """
        return [_.text for _ in self._get_item().find_all()]

    def get_text_of_current_back_action(self) -> str:
        """
        Obtain the text displayed by the currently displayed Back action in the submenu.

        :return: The text displayed within the 'Back' action at the top of the submenu.

        :raises TimeoutException: If no Back action is displayed, or if no submenu is displayed.
        """
        return self._get_submenu_back_action().find_all(wait_timeout=0)[-1].text

    def header_text_is_displayed(self) -> bool:
        """
        Determine if the Menu Tree is currently displaying a header within the submenu.

        :return: True, if a header is currently displayed within a submenu - False otherwise.
        """
        try:
            return self._header.find(wait_timeout=0) is not None
        except TimeoutException:
            return False

    def icon_is_displayed_for_item(self, item_text: str, is_in_submenu: bool) -> bool:
        """
        Determine if an icon is displayed alongside an item of the Menu Tree.

        :param item_text: The item you wish to query against.
        :param is_in_submenu: Clarifies if the specified item is expecetd to be within a submenu.

        :return: True, if an icon is displayed for the specified item - False otherwise.
        """
        try:
            return self._get_item_icon(
                item_text=item_text, is_in_submenu=is_in_submenu).find(wait_timeout=0).is_displayed()
        except TimeoutException:
            return False

    def item_is_displayed(self, item_text: str, is_in_submenu: bool = False) -> bool:
        """
        Determine if an item is displayed.


        :param item_text: The text of the item to search for.
        :param is_in_submenu: Clarifies if the item should be searched for as a submenu item.

        :return: True, if the specified item is displayed - False otherwise.
        """
        try:
            item = self._get_submenu_item(item_text=item_text) if is_in_submenu else self._get_item(item_text=item_text)
            return item.find(wait_timeout=0).is_displayed()
        except TimeoutException:
            return False

    def item_is_present(self, item_text: str, is_in_submenu: bool = False) -> bool:
        """
        Determine if an item with the specified text is present in the Menu Tree. This function does not convey
        information about the visibility of an item - only that it is present within the Menu Tree.

        :param item_text: The text of the item to search for.
        :param is_in_submenu: Clarifies if the item should be searched for as a submenu item.

        :return: True, if the item is present as part of the Menu Tree.
        """
        try:
            return self._get_item_or_submenu_item(
                item_text=item_text, is_in_submenu=is_in_submenu).find(wait_timeout=0) is not None
        except TimeoutException:
            return False
        
    def nav_icon_is_displayed_for_item(self, item_text: str, is_in_submenu: bool) -> bool:
        """
        Determine if an item entry is currently displaying a nav icon.
        
        :param item_text: The text of the item to check for a nav icon.
        :param is_in_submenu: clarifies whether the item to be checked is expected in a submenu.
        
        :return: True, if the specified item has a nav icon associated with it.
        """
        try:
            return self._get_item_nav_icon(
                item_text=item_text, is_in_submenu=is_in_submenu).find(wait_timeout=0).is_displayed()
        except TimeoutException:
            return False

    def scroll_to_item(self, item_text: str, align_to_top: bool, is_in_submenu: bool = False) -> None:
        self._get_item_or_submenu_item(
            item_text=item_text, is_in_submenu=is_in_submenu).scroll_to_element(align_to_top=align_to_top)

    def submenu_is_expanded(self) -> bool:
        """
        Determine if a submenu is currently expanded.

        :return: True, if a submenu is currently expanded - False otherwise.
        """
        try:
            return self._get_submenu_back_action().find(wait_timeout=0) is not None
        except TimeoutException:
            return False

    def wait_on_item_presence(
            self,
            item_text: str,
            should_be_present: bool,
            is_in_submenu: bool = False,
            wait_timeout: Optional[float] = None):
        """
        Wait some period of time until an item either becomes present in the Menu Tree or is removed from the Menu Tree.

        :param item_text: The text of the item to query for until it has the expected presence.
        :param should_be_present: Specifies whether you are waiting for the item to be present or to not be present.
        :param is_in_submenu: Clarifies whether the item should be expected as a top-level item or within a submenu.
        :param wait_timeout: How long (in seconds) to remain polling for the item.

        :return: True, if the item presence state matches the state specified in `should_be_present` - False otherwise.
        """
        item = self._get_item_or_submenu_item(item_text=item_text, is_in_submenu=is_in_submenu)
        wait = self.wait if wait_timeout is None else WebDriverWait(driver=self.driver, timeout=wait_timeout)

        def check_for_presence():
            nonlocal item
            nonlocal should_be_present
            try:
                return (item.find(wait_timeout=0) is not None) == should_be_present
            except TimeoutException:
                return should_be_present is False  # item wasn't found, which might be expected

        try:
            return wait.until(IAec.function_returns_true(custom_function=check_for_presence, function_args={}))
        except TimeoutException:
            return False

    def _get_item(self, item_text: Optional[str] = None) -> ComponentPiece:
        item = self._items.get(item_text)
        if not item:
            locator_string = 'div.menu-wrapper div.menu-item'
            if item_text is not None:
                locator_string += f'[data-label="{item_text}"]'
            item = ComponentPiece(
                locator=(By.CSS_SELECTOR, locator_string),
                driver=self.driver,
                parent_locator_list=self.locator_list)  # higher level
            self._items[item_text] = item
        return item

    def _get_item_icon(self, item_text: str, is_in_submenu: bool) -> CommonIcon:
        icon = self._item_icons.get(item_text)
        if not icon:
            icon = CommonIcon(
                locator=(By.CSS_SELECTOR, "div.label-icon svg"),
                driver=self.driver,
                parent_locator_list=self._get_item_or_submenu_item(
                    item_text=item_text, is_in_submenu=is_in_submenu).locator_list)
            self._item_icons[item_text] = icon
        return icon

    def _get_item_nav_icon(self, item_text: str, is_in_submenu: bool) -> CommonIcon:
        icon = self._item_nav_icons.get(item_text)
        if not icon:
            icon = CommonIcon(
                locator=(By.CSS_SELECTOR, "div.nav-icon svg"),
                driver=self.driver,
                parent_locator_list=self._get_item_or_submenu_item(
                    item_text=item_text, is_in_submenu=is_in_submenu).locator_list)
            self._item_nav_icons[item_text] = icon
        return icon
    
    def _get_item_or_submenu_item(self, item_text: str, is_in_submenu: bool) -> ComponentPiece:
        return self._get_submenu_item(item_text=item_text) if is_in_submenu else self._get_item(item_text=item_text)

    def _get_submenu_back_action(self, text: Optional[str] = None) -> ComponentPiece:
        locator_string = "div.menu-back-action"
        if text is not None:
            locator_string += f'[data-label="{text}"]'
        return ComponentPiece(
            locator=(By.CSS_SELECTOR, locator_string),
            driver=self.driver,
            parent_locator_list=self._submenu_group.locator_list,
            wait_timeout=1)

    def _get_submenu_item(self, item_text: Optional[str] = None) -> ComponentPiece:
        item = self._items.get(item_text)
        if not item:
            locator_string = 'div.menu-item'
            if item_text is not None:
                locator_string += f'[data-label="{item_text}"]'
            item = ComponentPiece(
                locator=(By.CSS_SELECTOR, locator_string),
                driver=self.driver,
                parent_locator_list=self._submenu_group.locator_list)  # nested in wrapper
            self._items[item_text] = item
        return item

    @staticmethod
    def _item_is_present(item: ComponentPiece) -> bool:
        try:
            return item.find(wait_timeout=0) is not None
        except TimeoutException:
            return False
