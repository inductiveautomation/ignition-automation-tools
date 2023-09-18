from typing import List, Optional, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Components.PerspectiveComponents.Common.Tree import CommonTree
from Helpers.IASelenium import IASelenium


class Tree(CommonTree, BasicPerspectiveComponent):
    """A Perspective Tree Component."""

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 3,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        CommonTree.__init__(
            self,
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        BasicPerspectiveComponent.__init__(
            self,
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._items_by_path = {}

    def item_exists_in_tree(self, item_path: str, item_label: str, wait_timeout: int = 2) -> bool:
        """
        Determine if an item exists in the Tree.

        :param item_path: The zero-indexed path of the item. A value of 0/0/1 translates to 'The 1th grandchild of the
            0th child of the 0th top-level node.'
        :param item_label: The label text of the item to verify the presence of.
        :param wait_timeout: The amount of time (in seconds) to wait for the item with the supplied path to appear.

        :returns: True, if an item with the supplied text exists at the specified location - False otherwise.
        """
        try:
            return self._get_item_by_path(
                path=item_path, wait_timeout=wait_timeout).get_text() == item_label
        except TimeoutException:
            return False

    def right_click(self, **kwargs) -> None:
        """
        Right-click the Tree. As individual items do not allow for their own events, this click will always target the
        0th top-level item (if one exists).
        """
        try:
            IASelenium(driver=self.driver).right_click(
                web_element=self._get_item_by_path(path="0", wait_timeout=1).find())
        except TimeoutException:
            super().right_click()

    def _get_item_by_path(self, path: str, wait_timeout: int = 2) -> ComponentPiece:
        """Obtain a specific item based on its zero-indexed path."""
        item_component = self._items_by_path.get(path)
        if not item_component:
            item_component = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'div[data-item-path="{path}"]'),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                wait_timeout=wait_timeout,
                poll_freq=self.poll_freq)
            self._items_by_path[path] = item_component
        return item_component
