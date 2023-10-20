import logging
from typing import Tuple, Optional, Union

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec

from Components.BasicComponent import BasicComponent, ComponentPiece
from Components.PerspectiveComponents.Common.Icon import CommonIcon
from Helpers.CSSEnumerations import CSSPropertyValue
from Helpers.Point import Point
from Pages.IgnitionPageObject import IgnitionPageObject
from Pages.Perspective.AppBar import AppBar


class PerspectivePageObject(IgnitionPageObject):
    _PERSPECTIVE_PATH_PREFIX = '/data/perspective/client'
    _LAPSED_TRIAL_HEADER_LOCATOR = (By.CSS_SELECTOR, 'h1.terminal-state-header')
    _LOADING_SPINNER = (By.CLASS_NAME, 'ignition-loading-spinner')
    _KNOWN_ERROR_CLASSES = [
        'component-error-boundary',
        'error-pie',
        'ia-xy-error'
    ]

    class ComponentContextMenu(BasicComponent):
        _ITEM_LOCATOR = (By.CSS_SELECTOR, "div.menu-item.ia_componentContextMenu__item")
        _MENU_LOCATOR = (By.ID, "context-menu")
        _SEPARATOR_LOCATOR = (By.CSS_SELECTOR, "div.separator hr")
        _SUBMENU_EXPANSION_ICON_LOCATOR = (By.CSS_SELECTOR, "div.ia_componentContextMenu__submenu--icon svg")

        def __init__(
                self,
                driver: WebDriver):
            """
            :param driver: The WebDriver in use by the browser.
            """
            BasicComponent.__init__(
                self,
                locator=self._MENU_LOCATOR,
                driver=driver,
                parent_locator_list=None)
            self._separators = ComponentPiece(
                locator=self._SEPARATOR_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                wait_timeout=1)
            self._item_coll = {}
            self._icon_coll = {}

        def click_item(
                self, item_text: str, submenu_depth: Optional[int] = None, binding_wait_time: float = 0.5) -> None:
            """
            Click an item within the context menu. For items within submenus, you must first hover over whichever other
            items would expand the submenus.

            :param item_text: The text of the item to click.
            :param submenu_depth: The depth of the submenu to which the item belongs.
            :param binding_wait_time: The amount of time to wait after clicking the item before allowing code to
                continue.
            """
            if submenu_depth is not None:
                # For sub-menu items, we must first hover over the 0th element in that sub-menu, otherwise
                # the sub-menu collapses as we leave our current item
                self._get_item(submenu_depth=submenu_depth).hover()
            self._get_item(item_text=item_text, submenu_depth=submenu_depth).click(binding_wait_time=binding_wait_time)

        def get_path_of_expansion_icon(self, item_text: str, submenu_depth: Optional[int] = None) -> str:
            """
            Obtain the library path in use by an expansion icon of the context menu.

            :param item_text: The text of the item the expansion icon belongs to.
            :param submenu_depth: The depth of the item in any submenus.

            :return: The library path in use by the expansion icon which belongs to the specified context menu item.
            """
            return self._get_expansion_icon(item_text=item_text, submenu_depth=submenu_depth).get_icon_name()

        def get_path_of_icon(self, item_text: str, submenu_depth: Optional[int] = None) -> str:
            """
            Obtain the library path in use by an icon of the context menu.

            :param item_text: The text of the item the icon belongs to.
            :param submenu_depth: The depth of the item in any submenus.

            :return: The library path in use by the icon which belongs to the specified context menu item.
            """
            return self._get_icon(item_text=item_text, submenu_depth=submenu_depth).get_icon_name()

        def get_property_of_icon(
                self, item_text: str, property_name: CSSPropertyValue, submenu_depth: Optional[int] = None) -> str:
            """
            Obtain the CSS value of a property of an icon which belongs to the described context menu item.

            :param item_text: The text of the item the icon belongs to.
            :param property_name: The name of the CSS property you would like a value for.
            :param submenu_depth: The depth of the item/icon.

            :return: The CSS value of the requested property for the icon of the specified context menu item.
            """
            return self._get_icon(
                item_text=item_text, submenu_depth=submenu_depth).get_css_property(property_name=property_name)

        def get_property_of_separator(self, index: int, property_name: CSSPropertyValue) -> str:
            """
            Obtain the CSS value of a property of a separator. Does not currently support submenus.

            :param index: The zero-based index of the separator from which you would like a CSS value.
            :param property_name: The name of the CSS property you would like a value for.

            :return: The CSS value of the specified property for the specified separator.

            :raises TimeoutException: If no separators are found.
            :raises IndexError: If separators are found, but fewer than the specified index.
            """
            # allow IndexError to bubble up if encountered
            return self._separators.find_all(wait_timeout=0)[index].get_attribute(property_name.value)

        def hover_over_item(
                self, item_text: str, submenu_depth: Optional[int] = None, binding_wait_time: float = 0) -> None:
            """
            Hover over an item of the context menu. This is extremely important while dealing with submenus.

            :param item_text: The text of the item to hover over.
            :param submenu_depth: The depth of the item which will be hovered over.
            :param binding_wait_time: The amount of time after hovering over the item to wait before allowing code to
                continue.
            """
            if submenu_depth is not None:
                # For sub-menu items, we MUST first hover over the 0th element in that sub-menu, otherwise
                # the sub-menu collapses as we leave our current item
                self._get_item(submenu_depth=submenu_depth).hover()
            self._get_item(item_text=item_text, submenu_depth=submenu_depth).hover()
            self._get_item(
                item_text=item_text,
                submenu_depth=submenu_depth).wait_on_binding(time_to_wait=binding_wait_time)

        def is_displayed(self) -> bool:
            """
            Determine if a context menu is currently displayed on the Page.

            :return: True, if a context menu is displayed on the current Page - False otherwise.
            """
            try:
                return self.find(wait_timeout=0) is not None
            except TimeoutException:
                return False

        def item_contains_configured_icon(self, item_text: str, submenu_depth: Optional[int] = None) -> bool:
            """
            Determine if an item is currently displaying an icon.

            :param item_text: The text of the item to search for an icon.
            :param submenu_depth: The depth of the item to check.

            :return: True, if the specified item of the context menu is displaying an icon - False otherwise.
            """
            try:
                return self._get_icon(
                    item_text=item_text, submenu_depth=submenu_depth).find(wait_timeout=0).is_displayed()
            except TimeoutException:
                return False

        def item_contains_submenu_expansion_icon(self, item_text: str, submenu_depth: Optional[int] = None) -> bool:
            """
            Determine if an item of the context menu is currently displaying an expansion icon.

            :param item_text: The text of the item to check for an expansion icon.
            :param submenu_depth: The depth of the item within submenus.

            :return: True, if the item is currently displaying an expansion icon - False otherwise.
            """
            try:
                return self._get_expansion_icon(
                    item_text=item_text, submenu_depth=submenu_depth).find(wait_timeout=0).is_displayed()
            except TimeoutException:
                return False

        def item_is_displayed(self, item_text: str, submenu_depth: Optional[int] = None) -> bool:
            """
            Determine if an item is currently displayed.

            :param item_text: The text of the item to search for.
            :param submenu_depth: The submenu depth of the item to search for. A None value implies the item belongs to
                the top-most level of the context menu, while a 0 value implies the item must belong to the 0th
                submenu, etc.

            :return: True, if the described item is currently displayed - False otherwise.
            """
            try:
                item = self._get_item(item_text=item_text, submenu_depth=submenu_depth)
                return item.find(wait_timeout=0).is_displayed() and item.get_text() == item_text
            except TimeoutException:
                return False

        def submenu_is_displayed(self, submenu_depth: int = 0) -> bool:
            """
            Determine if a submenu at the specified depth is currently displayed.

            :param submenu_depth: The depth of the submenu to query for.

            :return: True, if a submenu with the specified depth is currently displayed - False otherwise.
            """
            try:
                return ComponentPiece(
                    locator=self._get_submenu_locator(
                        submenu_depth=submenu_depth),
                    driver=self.driver,
                    parent_locator_list=None,
                    wait_timeout=1).find(wait_timeout=0).is_displayed()
            except TimeoutException:
                return False

        def _get_expansion_icon(self, item_text: str, submenu_depth: Optional[int] = None) -> CommonIcon:
            """
            Obtain the expansion icon in use for an item of the context menu, based on the item's text and submenu
                depth.

            :param item_text: The text of the item from which you would like the expansion icon.
            :param submenu_depth: The submenu depth of the expansion icon to be obtained. A None value implies the icon
                is at the top-most level of the context menu, while 0 implies the icon is within the 0th nested submenu,
                etc.

            :return: The ComponentPiece which defines the expansion icon of the item with the supplied text at the
                specified submenu depth.
            """
            identifier = (item_text, submenu_depth)
            icon = self._icon_coll.get(identifier)
            if not icon:
                icon = CommonIcon(
                    locator=self._SUBMENU_EXPANSION_ICON_LOCATOR,
                    driver=self.driver,
                    parent_locator_list=self._get_item(item_text=item_text, submenu_depth=submenu_depth).locator_list,
                    wait_timeout=1)
                self._icon_coll[identifier] = icon
            return icon

        def _get_icon(self, item_text: str, submenu_depth: Optional[int] = None) -> CommonIcon:
            """
            Obtain the icon in use for an item of the context menu, based on the item's text and submenu depth.

            :param item_text: The text of the item from which you would like the icon.
            :param submenu_depth: The submenu depth of the icon to be obtained. A None value implies the icon is
                at the top-most level of the context menu, while 0 implies the icon is within the 0th nested submenu,
                etc.

            :return: The ComponentPiece which defines the icon of the item with the supplied text at the specified
                submenu depth.
            """
            identifier = (item_text, submenu_depth)
            icon = self._icon_coll.get(identifier)
            if not icon:
                parent_locator_list = self._get_item(item_text=item_text, submenu_depth=submenu_depth).locator_list
                icon = CommonIcon(
                    locator=(By.CSS_SELECTOR, 'svg'),
                    driver=self.driver,
                    parent_locator_list=parent_locator_list,
                    wait_timeout=1)
                self._icon_coll[identifier] = icon
            return icon

        def _get_item(self, item_text: Optional[str] = None, submenu_depth: Optional[int] = None) -> ComponentPiece:
            """
            Obtain the Component Piece defined by text and depth.

            :param item_text: The text of the item you wish to obtain.
            :param submenu_depth: The submenu depth of the item to be obtained. A None value implies the menu item is
                at the top-most level of the context menu, while 0 implies the item is within the 0th nested submenu,
                etc.

            :return: The Component Piece defined by the supplied text and submenu depth.
            """
            identifier = (item_text, submenu_depth)
            item = self._item_coll.get(identifier)
            if not item:
                parent_locator_list = self.locator_list if submenu_depth is None \
                    else [self._get_submenu_locator(submenu_depth=submenu_depth)]
                # if item_text is None, we're looking for the submenu wrapper, so ignore any label attribute
                label_piece = f'[data-label="{item_text}"]' if item_text is not None else ""
                item = ComponentPiece(
                    locator=(By.CSS_SELECTOR, f'{self._ITEM_LOCATOR[1]}{label_piece}'),
                    driver=self.driver,
                    parent_locator_list=parent_locator_list,
                    wait_timeout=1)
                self._item_coll[identifier] = item
            return item

        @classmethod
        def _get_submenu_locator(cls, submenu_depth: int = 0) -> Tuple[Union[By, str], str]:
            return By.CSS_SELECTOR, f'#context-submenu-{submenu_depth}'

    def __init__(
            self,
            driver: WebDriver,
            gateway_address: str,
            page_config_path: str,
            primary_view_resource_path: str = None,
            primary_locator: Tuple = None,
            configured_tab_title: str = None,
            wait_timeout: int = 10):
        """
        :param driver: The WebDriver in use for the browser window.
        :param gateway_address: The address of the Gateway this page belongs to.
        :param page_config_path: The path as configured in the Page Configuration panel of the Designer.
        :param primary_view_resource_path: The path of the primary View in use for this Page.
        :param primary_locator: A tuple which describes an element unique to this Page.
        :param configured_tab_title: The title configured for this tab.
        :param wait_timeout: The amount of time (in seconds) to implicitly wait.
        """
        self._internal_page_url_path = page_config_path
        self._full_perspective_path = self._PERSPECTIVE_PATH_PREFIX + self._internal_page_url_path
        super().__init__(
            driver=driver,
            gateway_address=gateway_address,
            destination_path=self._full_perspective_path,
            primary_locator=primary_locator,
            wait_timeout=wait_timeout)
        self.app_bar = AppBar(driver=driver)
        self._primary_view_resource_path = primary_view_resource_path
        self.configured_page_title = configured_tab_title
        self._component_context_menu = PerspectivePageObject.ComponentContextMenu(
            driver=driver)

    def click_item_of_component_context_menu(
            self, item_text: str, submenu_depth: Optional[int] = None, binding_wait_time: float = 0.5) -> None:
        """
        Click an item within the context menu displayed on the Page.
        :param item_text: The text of the item you wish to click.
        :param submenu_depth: The depth of the submenu to query for.
        :param binding_wait_time: The amount of time to wait after clicking the specified item before allowing code to
            continue.
        """
        self._component_context_menu.click_item(
            item_text=item_text, submenu_depth=submenu_depth, binding_wait_time=binding_wait_time)

    def component_context_menu_is_displayed(self) -> bool:
        """
        Determine if a context menu is currently displayed on the Page.

        :return: True, if a context menu is displayed on the current Page - False otherwise.
        """
        return self._component_context_menu.is_displayed()

    def component_context_menu_submenu_is_displayed(self, submenu_depth: int = 0) -> bool:
        """
        Determine if a submenu at the specified depth is currently displayed.

        :param submenu_depth: The depth of the submenu to query for.

        :return: True, if a submenu with the specified depth is currently displayed - False otherwise.
        """
        return self._component_context_menu.submenu_is_displayed(submenu_depth=submenu_depth)

    def get_count_of_components_with_errors(self) -> int:
        """
        Obtain a count of components which are currently displaying a Quality Overlay.

        :return: A count of all components on this Page which are currently displaying a Quality Overlay.
        """
        try:
            error_over_lay_list = self.wait.until(ec.presence_of_all_elements_located((By.TAG_NAME, 'div.cqfo-error')))
        except TimeoutException:
            error_over_lay_list = []
        errors_caught_in_boundary_list = []
        for error_class in self._KNOWN_ERROR_CLASSES:
            errors_caught_in_boundary_list += self.driver.find_elements(By.CSS_SELECTOR, f'div.{error_class}')
        return len(error_over_lay_list + errors_caught_in_boundary_list)

    def get_origin_of_component_context_menu(self) -> Point:
        """
        Get the Cartesian Coordinate of the upper-left corner of the Context Menu, measured from the
        top-left of the viewport.

        :returns: The Cartesian Coordinate of the upper-left corner of the Context Menu, measured from the
            top-left of the viewport.
        """
        return self._component_context_menu.get_origin()

    def get_path_of_expansion_icon_in_submenu_item(self, item_text: str, submenu_depth: Optional[int] = None) -> str:
        """
        Obtain the library path in use by an expansion icon of the context menu.

        :param item_text: The text of the item the expansion icon belongs to.
        :param submenu_depth: The depth of the item in any submenus.

        :return: The library path in use by the expansion icon which belongs to the specified context menu item.
        """
        return self._component_context_menu.get_path_of_expansion_icon(item_text=item_text, submenu_depth=submenu_depth)

    def get_path_of_icon_in_component_context_menu(self, item_text: str, submenu_depth: Optional[int] = None) -> str:
        """
        Obtain the library path in use by an icon of the context menu.

        :param item_text: The text of the item the icon belongs to.
        :param submenu_depth: The depth of the item in any submenus.

        :return: The library path in use by the icon which belongs to the specified context menu item.
        """
        return self._component_context_menu.get_path_of_icon(item_text=item_text, submenu_depth=submenu_depth)

    def get_primary_view_resource_path(self) -> str:
        """
        :return: The path and name of the View used to construct the Page
        """
        if self._primary_view_resource_path is None:
            logging.getLogger(PerspectivePageObject.__name__).warning(
                f'A request was made for a primary view resource path, but none was configured during init() '
                f'for {self._internal_page_url_path}')
        return self._primary_view_resource_path

    def get_page_url_as_configured_in_designer(self) -> str:
        """
        :return: The configured url of the current page WITHOUT the preceding '/project_name'.
        """
        return self._internal_page_url_path

    def get_property_of_component_context_menu_item_icon(
            self, property_name: CSSPropertyValue, item_text: str, submenu_depth: Optional[int] = None) -> str:
        """
        Obtain the CSS value of a property of an icon which belongs to the described context menu item.

        :param item_text: The text of the item the icon belongs to.
        :param property_name: The name of the CSS property you would like a value for.
        :param submenu_depth: The depth of the item/icon.

        :return: The CSS value of the requested property for the icon of the specified context menu item.
        """
        return self._component_context_menu.get_property_of_icon(
            property_name=property_name, item_text=item_text, submenu_depth=submenu_depth)

    def get_property_of_component_context_menu_separator(self, index: int, property_name: CSSPropertyValue) -> str:
        """
        Obtain the CSS value of a property of a separator. Does not currently support submenus.

        :param index: The zero-based index of the separator from which you would like a CSS value.
        :param property_name: The name of the CSS property you would like a value for.

        :return: The CSS value of the specified property for the specified separator.

        :raises TimeoutException: If no separators are found.
        :raises IndexError: If separators are found, but fewer than the specified index.
        """
        return self._component_context_menu.get_property_of_separator(index=index, property_name=property_name)

    def get_termination_of_component_context_menu(self) -> Point:
        """
        Get the Cartesian Coordinate of the bottom-right corner of the Context Menu, measured from the
        top-left of the viewport.

        :returns: The Cartesian Coordinate of the bottom-right corner of the Context Menu, measured from the
            top-left of the viewport.
        """
        return self._component_context_menu.get_termination()

    def hover_over_item_of_component_context_menu(
            self, item_text: str, submenu_depth: Optional[int] = None, binding_wait_time: float = 0) -> None:
        """
        Hover over an item of the context menu. This is extremely important while dealing with submenus.

        :param item_text: The text of the item to hover over.
        :param submenu_depth: The depth of the item which will be hovered over.
        :param binding_wait_time: The amount of time after hovering over the item to wait before allowing code to
            continue.
        """
        self._component_context_menu.hover_over_item(
            item_text=item_text, submenu_depth=submenu_depth, binding_wait_time=binding_wait_time)

    def item_in_component_context_menu_contains_icon(self, item_text: str, submenu_depth: Optional[int] = None) -> bool:
        """
        Determine if an item is currently displaying an icon.

        :param item_text: The text of the item to search for an icon.
        :param submenu_depth: The depth of the item to check.

        :return: True, if the specified item of the context menu is displaying an icon - False otherwise.
        """
        return self._component_context_menu.item_contains_configured_icon(
            item_text=item_text, submenu_depth=submenu_depth)

    def item_is_displayed_in_component_context_menu(self, item_text: str, submenu_depth: Optional[int] = None) -> bool:
        """
        Determine if an item is currently displayed.

        :param item_text: The text of the item to search for.
        :param submenu_depth: The submenu depth of the item to search for. A None value implies the item belongs to
            the top-most level of the context menu, while a 0 value implies the item must belong to the 0th
            submenu, etc.

        :return: True, if the described item is currently displayed - False otherwise.
        """
        return self._component_context_menu.item_is_displayed(item_text=item_text, submenu_depth=submenu_depth)

    def navigate_to(self, **kwargs):
        raise NotImplementedError("You must provide your own navigation pattern for this page.")

    def submenu_item_in_component_context_menu_contains_expansion_icon(
            self, item_text: str, submenu_depth: Optional[int] = None) -> bool:
        """
        Determine if an item of the context menu is currently displaying an expansion icon.

        :param item_text: The text of the item to check for an expansion icon.
        :param submenu_depth: The depth of the item within submenus.

        :return: True, if the item is currently displaying an expansion icon - False otherwise.
        """
        return self._component_context_menu.item_contains_submenu_expansion_icon(
            item_text=item_text, submenu_depth=submenu_depth)

    def wait_for_perspective_page(self) -> None:
        """
        Wait for the page to load, and for the App Bar to render. For projects which do NOT have the App Bar configured
        to display, this function should be overridden or usages should be wrapped in a try/except block to capture
        the TimeoutException which would be raised.

        :raise TimeoutException: If the page does not load, or the App Bar never renders.
        """
        self._wait_for_page()
        self.app_bar.wait_for_revealer_or_app_bar_to_be_displayed()
