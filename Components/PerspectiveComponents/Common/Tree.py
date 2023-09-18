import sys
from typing import List, Optional, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece
from Components.PerspectiveComponents.Common.Icon import CommonIcon


class CommonTree(ComponentPiece):
    """
    A Tree of items, as is found as part of the Tree Component, the Tag Browse Tree, and the Power Chart.

    Selenium is limited in how it locates items for interaction, and so if two visible nodes share the same label text
    the first (top-most) item is the one which will be interacted with.

    https://youtrack.ia.local/issue/IGN-7575 exists to move the data-label attribute up higher, which would allow
    for us to target specific items which have duplicated text by item path instead of zero-index.
    """
    _EXPANDED_ICON_CLASS = "ia_treeComponent__expandIcon--expanded"
    _FOLDER_EXPAND_ICON_LOCATOR = (
        By.CSS_SELECTOR, 'svg.expand-icon.ia_treeComponent__expandIcon')
    _LABEL_LOCATOR = (
        By.CSS_SELECTOR, 'div.label-wrapper-text')
    _TOP_LEVEL_ITEMS_LOCATOR = (By.CSS_SELECTOR, 'div.tree>div>div>div.tree-row')
    _ITEM_CLASS = "tree-item"
    _TREE_ITEM_LOCATOR = (By.CSS_SELECTOR, f".{_ITEM_CLASS}")

    def __init__(
            self,
            driver: WebDriver,
            locator: Tuple[By, str],
            parent_locator_list: Optional[List] = None,
            wait_timeout: float = 3,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._folder_icons = ComponentPiece(
            locator=self._FOLDER_EXPAND_ICON_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._expanded_folders = ComponentPiece(
            locator=(By.CSS_SELECTOR, f'div[class*="expanded"] div.text-scroll'),
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._top_level_items = ComponentPiece(
            locator=self._TOP_LEVEL_ITEMS_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._tree_items = ComponentPiece(
            locator=self._TREE_ITEM_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._items = {}
        self._item_icons = {}
        self._expand_collapse_icons = {}
        self._labels = {}

    def click_expansion_icon_for_item(self, item_label: str, binding_wait_time: int = 0) -> None:
        """
        Click the expand icon for an item regardless of expansion state. If you are attempting to set the expansion
        state, you should use :func:`set_expansion_state_for_item`

        :param item_label: The text of the item for which we will click the expansion icon.
        :param binding_wait_time: The amount of time (in seconds) to wait after the click event before allowing code to
            continue.

        :raises TimeoutException: If no icon exists or if no item with the supplied label exists.
        """
        self._get_expansion_icon(item_label=item_label).click(binding_wait_time=binding_wait_time)

    def click_item_label(self, item_label: str, binding_wait_time: float = 0) -> None:
        """
        Click the label of an item.

        :param item_label: The text of the item you would like to click.
        :param binding_wait_time: The amount of time (in seconds) to wait after the click event before allowing code to
            continue.

        :raises TimeoutException: If no item with the supplied text is available to be clicked. This could either mean
            no item with that text exists, or the target item could be inside an item which has not yet been expanded.
        """
        label = self._labels.get(item_label)
        if not label:
            label = ComponentPiece(
                locator=self._LABEL_LOCATOR,
                driver=self.driver,
                parent_locator_list=self._get_item_by_label(item_label=item_label).locator_list,
                poll_freq=self.poll_freq)
            self._labels[item_label] = label
        label.click(binding_wait_time=binding_wait_time)

    def expansion_icon_is_present_for_item(self, item_label: str) -> bool:
        """
        Determine if an item is currently displaying an expansion icon.

        :returns: True, if an expansion icon is displayed for the first item with the supplied text. False, if an
            expansion icon is not displayed, or if no item with the supplied text exists.
        """
        try:
            return ComponentPiece(
                locator=(By.CSS_SELECTOR, "g"),
                driver=self.driver,
                parent_locator_list=self._get_expansion_icon(item_label=item_label).locator_list,
                wait_timeout=1,
                poll_freq=self.poll_freq).find().is_displayed()
        except TimeoutException:
            return False

    def get_fill_color_of_expansion_icon_for_item(self, item_label: str) -> str:
        """
        Obtain the fill color of the expansion icon for an item.

        :returns: The fill color of the expansion icon for the first item with the supplied text as a string. Note that
            different browsers may return this string in different formats (RGB vs hex).

        :raises TimeoutException: If no expansion icon exists for the item, or if no item with the supplied text exists.
        """
        return self._get_expansion_icon(item_label=item_label).get_fill_color()

    def get_fill_color_of_icon_for_item(self, item_label: str) -> str:
        """
        Obtain the fill color of the icon for an item.

        :returns: The fill color of the icon for the first item with the supplied text as a string. Note that
            different browsers may return this string in different formats (RGB vs hex).

        :raises TimeoutException: If no icon exists for the item, or if no item with the supplied text exists.
        """
        return self._get_item_icon(item_label=item_label).get_fill_color()

    def get_path_of_expansion_icon_for_item(self, item_label: str) -> str:
        """
        Obtain the path of the expansion icon in use by an item.

        :returns: A slash-delimited string representing the path of the svg in use.

        :raises TimeoutException: If no expansion icon exists for the item, or if no item with the supplied text exists.
        """
        return self._get_expansion_icon(item_label=item_label).get_icon_name()

    def get_path_of_icon_for_item(self, item_label: str) -> str:
        """
        Obtain the path of the icon in use by an item.

        :returns: A slash-delimited string representing the path of the svg in use.

        :raises TimeoutException: If no icon exists for the item, or if no item with the supplied text exists.
        """
        return self._get_item_icon(item_label=item_label).get_icon_name()

    def get_text_of_top_level_items(self) -> List[str]:
        """
        Obtain the text of all items located at the top-most level.
        """
        try:
            return [_.text for _ in self._top_level_items.find_all()]
        except TimeoutException:
            return []

    def get_text_of_all_items_in_tree(self, wait_timeout: float = 5) -> List[str]:
        """
        Obtain a list which contains the text of all displayed items in the Tree.

        :param wait_timeout: How long to wait (in seconds) for any tree items to appear.
        """
        try:
            return [item.text for item in self._tree_items.find_all(wait_timeout=wait_timeout)]
        except TimeoutException:
            return []

    def multi_select_items(
            self, item_labels: List[str], inclusive_multi_selection: bool = True, wait_timeout: float = 5) -> None:
        """
        Select multiple items within the Tree. Note that any selections previous to this function could be lost.

        :param item_labels: A list of item labels to select.
        :param inclusive_multi_selection: Dictates whether we are holding Shift (True) or CMD/Ctrl (False) while making
            the selections.
        :param wait_timeout: The amount of time to wait for each item to become available before attempting selection.

        :raises TimeoutException: If no item exists with text matching any individual entry from the items_list.
        """
        actions = ActionChains(self.driver)
        if inclusive_multi_selection:
            mod_key = Keys.SHIFT
        else:
            mod_key = Keys.COMMAND if sys.platform.startswith('darwin') else Keys.CONTROL

        actions.key_down(mod_key)
        piece_list = [self._get_item_by_label(item_label=_, wait_timeout=wait_timeout) for _ in item_labels]
        for piece in piece_list:
            actions.click(on_element=piece.find()).pause(1)
        actions.key_up(mod_key)
        actions.perform()
        self.wait_on_binding(1)

    def item_label_exists_in_tree(self, item_label: str, wait_timeout: int = 5) -> bool:
        """
        Determine if an item exists based on its label text.

        :param item_label: The label text of the item whose existence you wish to verify.
        :param wait_timeout: The amount of time (in seconds) you are willing to wait for the item to appear.

        :returns: True, if any item matches the supplied text - False otherwise.
        """
        try:
            return self._get_item_by_label(item_label=item_label, wait_timeout=wait_timeout).find() is not None
        except TimeoutException:
            return False

    def item_is_expanded(self, item_label: str) -> bool:
        """
        Determine if an item is expanded.

        :param item_label: The label text of the item we will check the expanded status of.

        :raises TimeoutException: If the item we check does not have an expansion icon. This likely means that the
            specified item is a terminal node and may not be expanded.
        """
        try:
            return self._EXPANDED_ICON_CLASS in self._get_expansion_icon(
                item_label=item_label).find().get_attribute(name="class")
        except TimeoutException:
            return False

    def node_icon_is_present_for_item(self, item_label: str) -> bool:
        """
        Determine if an item is currently displaying an icon which would convey whether the item is a
        directory/folder or a terminal node.

        :param item_label: The text of the item we will check for a node icon.

        :returns: True, if an icon which would convey the type of the item is displayed for the first item with the
            supplied text. False, if an icon is not displayed, or if no item with the supplied text exists.
        """
        try:
            return ComponentPiece(
                locator=(By.CSS_SELECTOR, "g"),
                driver=self.driver,
                parent_locator_list=self._get_item_icon(item_label=item_label).locator_list,
                wait_timeout=1,
                poll_freq=self.poll_freq).find().is_displayed()
        except TimeoutException:
            return False

    def select_item_in_tree(self, item_label: str, wait_timeout: int = 5, binding_wait_time: int = 1) -> None:
        """
        Select a single item in the Tree.

        :param item_label: The label text of the item to click.
        :param wait_timeout: The amount of time (in seconds) to wait for the item to appear.
        :param binding_wait_time: The amount of time (in seconds) after clicking the item to wait before allowing code
            to continue.

        :raises TimeoutException: If no item with the supplied text exists.
        """
        self._get_item_by_label(
            item_label=item_label, wait_timeout=wait_timeout).click(binding_wait_time=binding_wait_time)

    def set_expansion_state_for_item(self, item_label: str, should_be_expanded: bool) -> None:
        """
        Set an item to be expanded or collapsed.

        :param item_label: The label text of the item to expand or collapse.
        :param should_be_expanded: A True value specifies the item should be expanded, while a False value specifies the
            item should be collapsed.

        :raises TimeoutException: If no item with the supplied text exists, or if the specified item has no expansion
            icon.
        """
        if self.item_is_expanded(item_label=item_label) != should_be_expanded:
            try:
                self._get_expansion_icon(item_label=item_label).click()
            except TimeoutException as toe:
                toe.msg = f"Node with label of '{item_label}' does not contain an expand/collapse icon."
                raise toe

    def _get_expansion_icon(self, item_label: str) -> CommonIcon:
        """Obtain the icon which conveys the expansion status of the item."""
        icon = self._expand_collapse_icons.get(item_label)
        if not icon:
            icon = CommonIcon(
                locator=(By.CSS_SELECTOR, "svg.expand-icon"),
                driver=self.driver,
                parent_locator_list=self._get_item_by_label(item_label=item_label).locator_list,
                poll_freq=self.poll_freq)
            self._expand_collapse_icons[item_label] = icon
        return icon

    def _get_item_icon(self, item_label: str) -> CommonIcon:
        """Obtain the icon which conveys whether the item is a directory/folder or a terminal node."""
        icon = self._item_icons.get(item_label)
        if not icon:
            icon = CommonIcon(
                locator=(By.CSS_SELECTOR, "svg.node-icon"),
                driver=self.driver,
                parent_locator_list=self._get_item_by_label(item_label=item_label).locator_list,
                poll_freq=self.poll_freq)
            self._item_icons[item_label] = icon
        return icon

    def _get_index_of_item_in_tree(self, item_label: str) -> int:
        """Get the zero-indexed position among all items for the label with the supplied text."""
        return [_.text for _ in self._tree_items.find_all()].index(item_label)

    def _get_item_by_label(self, item_label: str, wait_timeout: float = 5) -> ComponentPiece:
        """Obtain the first item with the supplied text."""
        item = self._items.get(item_label)
        if not item:
            item = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'{self._TREE_ITEM_LOCATOR[1]}[data-label="{item_label}"]'),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                wait_timeout=wait_timeout,
                poll_freq=self.poll_freq)
            self._items[item_label] = item
        return item

    @classmethod
    def _split_item_label_path(cls, slash_delimited_label_path: str) -> List[str]:
        """Obtain the pieces of a string after having split the string on a slas ('/')."""
        return slash_delimited_label_path.split('/')
