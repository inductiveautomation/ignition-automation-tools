from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece
from Helpers.CSSEnumerations import CSS
from Helpers.IAAssert import IAAssert


class PopupHelper:
    """
    This helper is intended to help with Popups in a generalized capacity. It does not work for interacting with
    or determining the state of specific Popups.
    """
    _CLOSE_ICON_LOCATOR = (By.CSS_SELECTOR, "svg.close-icon")
    _GENERIC_POPUP_LOCATOR = (By.CSS_SELECTOR, "div.popup")
    _MODAL_LOCATOR = (By.CSS_SELECTOR, "div.modal")

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self._generic_popup = ComponentPiece(
            locator=self._GENERIC_POPUP_LOCATOR,
            driver=driver,
            description="A generic definition of a Popup.",
            wait_timeout=0)  # no parent
        self._modal = ComponentPiece(
            locator=self._MODAL_LOCATOR, driver=driver, parent_locator_list=None, wait_timeout=0)

    def close_all_popups(self) -> None:
        """
        Make an attempt to close all open Popups. This approach requires that each open Popup be configured to display
        a close icon.

        :raises NoSuchElementException: If any of the open Popups does not have a close icon.
        """
        # find all popups
        try:
            list_of_popups = self._generic_popup.find_all(wait_timeout=1)
            # now sort them so the "highest" is first.
            popups_sorted_by_z_index = sorted(
                list_of_popups, key=lambda e: e.value_of_css_property(CSS.Z_INDEX.value), reverse=True)
            # click the close icon for each popup
            [popup.find_element(*self._CLOSE_ICON_LOCATOR).click() for popup in popups_sorted_by_z_index]
        except NoSuchElementException as nsee:
            raise NoSuchElementException(msg="Unable to close a Popup because it had no close icon present.") from nsee
        except TimeoutException:
            pass
        IAAssert.is_equal_to(
            actual_value=self.get_count_of_all_open_popups(),
            expected_value=0,
            failure_msg="We failed to close all open Popups.")

    def get_count_of_all_open_popups(self) -> int:
        """
        Obtain a count of how many Popups are currently displayed.

        :returns: A count of how many Popups are currently displayed.
        """
        try:
            return len(self._generic_popup.find_all(wait_timeout=0))
        except TimeoutException:
            return 0

    def overlay_is_present(self) -> bool:
        """
        Determine if an overlay is present.

        :returns: True, if any Popup is displaying as a modal - False otherwise.
        """
        try:
            return self._modal.find(wait_timeout=0) is not None
        except TimeoutException:
            return False
