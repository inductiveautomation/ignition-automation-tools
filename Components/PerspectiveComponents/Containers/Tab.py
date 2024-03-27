from typing import Union, List, Optional, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Helpers.CSSEnumerations import CSS


class Tab(BasicPerspectiveComponent):
    """A Perspective Tab Container."""
    _TAB_CSS_STRING = 'div.tab-menu-item'
    _ACTIVE_TAB_CLASS = 'tab-active'
    _ACTIVE_TAB_LOCATOR = (By.CSS_SELECTOR, f"{_TAB_CSS_STRING}.{_ACTIVE_TAB_CLASS}")
    _CLASSIC_MODE_CLASS = 'menu-classic'
    _MODERN_MODE_CLASS = 'menu-modern'
    _VIEW_PARENT_CLASS = 'view-parent'
    _TAB_DISABLED_CLASS = 'tab-disabled'
    _TAB_LOCATOR = (By.CSS_SELECTOR, f'{_TAB_CSS_STRING} span')

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
        self._tabs = ComponentPiece(
            locator=self._TAB_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=wait_timeout,
            poll_freq=poll_freq)
        self._tabs_by_index = {}
        self._active_tab = ComponentPiece(
            locator=self._ACTIVE_TAB_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            poll_freq=poll_freq)

    def click_tab_by_index(self, index: Union[int, str]) -> None:
        """
        Click a tab based on its index.

        :param index: The zero-based index of the tab you would like to click.

        :raises TimeoutException: If the supplied index is not present.
        """
        self._get_tab_by_index(index=index).click(binding_wait_time=0.5)

    def _get_tab_by_index(self, index: int) -> ComponentPiece:
        """
        Obtain a ComponentPiece which defines a tab of the container by its index.

        :param index: The zero-based index of the tab this ComponentPiece will define.
        """
        index = int(index)
        tab_element = self._tabs_by_index.get(index)
        if not tab_element:
            tab_element = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'div[data-index="{index}"]'),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                poll_freq=self.poll_freq)
            self._tabs_by_index[index] = tab_element
        return tab_element

    def get_active_tab_index(self) -> int:
        """
        Obtain the index of the currently active tab.

        :returns: The zero-based index of the tab which is currently active for the container.
        """
        return int(self._active_tab.find().get_attribute("data-index"))

    def get_count_of_tabs(self) -> int:
        """
        Obtain a count of tabs currently present for the container.

        :returns: The count of tabs which belong to this container.
        """
        try:
            return len(self._tabs.find_all(wait_timeout=1))
        except TimeoutException:
            return 0

    def click_tab_by_text(self, text: str) -> None:
        """
        Click a tab for this container based on the text of the tab. The supplied text must be an exact match of all
        text contained within the tab. No action is taken if no tab contains the supplied text.

        :param text: The exact text contained within the tab to click.
        """
        for tab in self._tabs.find_all():
            if tab.text == text:
                tab.click()

    def tab_is_rendering_view(self, index: int) -> bool:
        """
        Determine if the specified tab is rendering as a View.

        :param index: The zero-based index of the tab to check.

        :returns: True, if the specified tab is rendering as a View - False otherwise.
        """
        return self._VIEW_PARENT_CLASS in self._get_tab_by_index(index=index).find().get_attribute("class")

    def tab_is_disabled(self, index: int) -> bool:
        """
        Determine if a tab is currently disabled.

        :param index: The zero-based index of the tab to check.

        :returns: True, if the specified tab is disabled - False otherwise.
        """
        return self._TAB_DISABLED_CLASS in self._get_tab_by_index(index=index).find().get_attribute("class")

    def get_tab_computed_width(self, index: int, include_units: bool = False) -> str:
        """
        Obtain the width of a tab which belongs to this container.

        :param index: The zero-based index of the tab to check.
        :param include_units: Dictates whether the returned value contains units of measurement.

        :returns: The width of the specified tab, potentially with units of measurement.
        """
        return self._get_tab_by_index(index=index).get_computed_width(include_units=include_units)

    def get_tab_background_color(self, index: int) -> str:
        """
        Obtain the background color in use for a tab of this container. Note that different browsers may return this
        color value in different formats (RGB vs hex).

        :param index: The zero-based index of the tab from which you would like the background color.

        :returns: The background color in use for the specified tab as a string.
        """
        return self._get_tab_by_index(index=index).get_css_property(property_name=CSS.BACKGROUND_COLOR)

    def get_tab_container_computed_width(self, include_units: bool = False) -> str:
        """
        Obtain the width of the container which contains all of the tabs which belongs to this container.

        :param include_units: Dictates whether the returned value contains units of measurement.

        :returns: The width of the container which contains all of the tabs, potentially with units of measurement.
        """
        return self.get_computed_width(include_units=include_units)

    def get_names_of_tabs(self) -> List[str]:
        """
        Obtain the names of all tabs of this container.

        :returns: A list, where each string element is the text displayed within the tab.
        """
        return [tab.text for tab in self._tabs.find_all()]

    def tabs_are_in_classic_mode(self) -> bool:
        """
        Determine if tabs are rendering in 'classic' mode.

        :returns: True, if all tabs are rendering in the 'classic' mode - False if even one of the tabs is not rendering
            in the 'classic' mode.
        """
        for tab in self._tabs.find_all():
            if self._CLASSIC_MODE_CLASS not in tab.get_attribute("class"):
                return False
        return True

    def tabs_are_in_modern_mode(self) -> bool:
        """
        Determine if tabs are rendering in 'modern' mode.

        :returns: True, if all tabs are rendering in the 'modern' mode - False if even one of the tabs is not rendering
            in the 'modern' mode.
        """
        for tab in self._tabs.find_all():
            if self._MODERN_MODE_CLASS not in tab.get_attribute("class"):
                return False
        return True
