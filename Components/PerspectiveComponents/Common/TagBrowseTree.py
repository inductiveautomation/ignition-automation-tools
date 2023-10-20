from typing import List, Optional, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Components.PerspectiveComponents.Common.Icon import CommonIcon
from Components.PerspectiveComponents.Common.Tree import CommonTree
from Components.Common.TextInput import CommonTextInput


class CommonTagBrowseTree(CommonTree, BasicPerspectiveComponent):
    _TAG_BROWSER_NO_RESULTS_FOUND_LOCATOR = (By.CSS_SELECTOR, 'span.ia_tagBrowser__noResultsDisplay__message')
    _TAG_BROWSER_RELOAD_ICON_LOCATOR = (By.CSS_SELECTOR, '.reload-icon svg')
    _TAG_BROWSER_FILTER_TEXT_FIELD_LOCATOR = (By.CSS_SELECTOR, '.filter-bar')

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 3,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        CommonTree.__init__(
            self, locator=locator, driver=driver, parent_locator_list=parent_locator_list, poll_freq=poll_freq)
        BasicPerspectiveComponent.__init__(
            self,
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._no_results = ComponentPiece(
            locator=self._TAG_BROWSER_NO_RESULTS_FOUND_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._reload_icon = CommonIcon(
            locator=self._TAG_BROWSER_RELOAD_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._filter_tf = CommonTextInput(
            locator=self._TAG_BROWSER_FILTER_TEXT_FIELD_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq
        )

    def click_refresh_icon(self, binding_wait_time=5) -> None:
        """
        Click the refresh icon of the Tag Browse Tree.

        :raises TimeoutException: If the refresh icon is not present.
        """
        self._reload_icon.click(binding_wait_time=binding_wait_time)

    def get_refresh_icon_path(self) -> str:
        """
        Get a slash-delimited path of the refresh icon.

        :returns: The path in use by the svg in a slash-delimited format.
        """
        return self._reload_icon.get_icon_name()

    def no_results_message_is_displayed(self, wait_timeout=5) -> bool:
        """
        Determine if the Tag Browse Tree is currently displaying a message conveying that no results are found for the
        configured provider.

        :param wait_timeout: The amount of time (in seconds) to wait for the message to appear.

        :returns: True, if the message is displayed - False otherwise.
        """
        try:
            return self._no_results.find(wait_timeout=wait_timeout).is_displayed()
        except TimeoutException:
            return False

    def refresh_icon_is_displayed(self, wait_timeout=5) -> bool:
        """
        Determine if the refresh icon is currently displayed.

        :param wait_timeout: The amount of time (in seconds) to wait for the icon to appear.

        :returns: True, if the icon is displayed - False otherwise.
        """
        try:
            return self._reload_icon.find(wait_timeout=wait_timeout).is_displayed()
        except TimeoutException:
            return False

    def set_filter_text(self, filter_text: str) -> None:
        """
        Set the text of Tag Tree Browser Filter text field.

        :param filter_text: The text we input to filter the tags.
        """
        self._filter_tf.set_text(text=filter_text, binding_wait_time=0.5)

    def filter_text_field_is_displayed(self) -> bool:
        """
        Determine if the Tag Browse Tree filter field is currently displayed.

        :returns: True, if the Filter text field is displayed - False otherwise.
        """
        try:
            return self._filter_tf.find(wait_timeout=0).is_displayed()
        except TimeoutException:
            return False
