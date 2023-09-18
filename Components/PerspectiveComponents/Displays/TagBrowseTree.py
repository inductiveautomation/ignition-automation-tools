from typing import List, Optional, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent
from Components.PerspectiveComponents.Common.TagBrowseTree import CommonTagBrowseTree


class TagBrowseTree(CommonTagBrowseTree, BasicPerspectiveComponent):
    """A Perspective Tag Browse Tree Component."""

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 3,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        CommonTagBrowseTree.__init__(
            self,
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            description=description,
            poll_freq=poll_freq)
        BasicPerspectiveComponent.__init__(
            self,
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            poll_freq=poll_freq)

    def multi_select_tags(self, tag_name_list: [str], inclusive_multi_selection: bool, wait_timeout: int = 5) -> None:
        """
        Select multiple tags within the Tag Browse Tree.

        :param tag_name_list: A list of tag names to be selected. If multiple tags with the same name are visible, only
            the first of each such tag will be selected.
        :param inclusive_multi_selection: A True value specifies that all tags between the supplied tags should also be
            selected, and so SHIFT will be held. A False value specifies that ONLY the supplied tags should be selected,
            and so CONTROL will be held.
        :param wait_timeout: The amount of time to wait (in seconds) for each tag to become visible.

        :raises TimeoutException: If any of the supplied tags did not exist.
        """
        self.multi_select_items(
            item_labels=tag_name_list, inclusive_multi_selection=inclusive_multi_selection, wait_timeout=wait_timeout)

    def select_tag_from_tree(self, tag_name: str, wait_timeout: int = 5) -> None:
        """
        Select a tag from the Tag Browse Tree.

        :param tag_name: The name of the tag to select. If multiple tags with the same name are displayed, the first
            tag with this name will be selected.
        :param wait_timeout: The amount of time (in seconds) to wait for the supplied tag to appear.

        :raises TimeoutException: If no such tag exists.
        """
        self.select_item_in_tree(item_label=tag_name, wait_timeout=wait_timeout)
