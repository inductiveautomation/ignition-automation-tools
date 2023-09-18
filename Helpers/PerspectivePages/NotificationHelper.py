from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece
from Helpers.CSSEnumerations import CSS


class NotificationHelper:
    """
    A Helper class for interacting with Perspective browser notifications. Unfortunately, these notifications do not
    supply any sort of identifying attributes, so when more than one notification is present any sort of reference
    needs to be by index.
    """
    _NOTIFICATION_LOCATOR = (By.CSS_SELECTOR, 'div.notification')
    _CLOSE_ICON_LOCATOR = (By.CSS_SELECTOR, 'div.close-icon')
    _BODY_LOCATOR = (By.CSS_SELECTOR, 'div.notification-body')
    _ICON_LOCATOR = (By.CSS_SELECTOR, 'svg.notification-icon')
    _SUMMARY_LOCATOR = (By.CSS_SELECTOR, 'p.message-summary')
    _DETAILS_LOCATOR = (By.CSS_SELECTOR, 'p.message-detail')
    _ACTION_ITEM_LOCATOR = (By.CSS_SELECTOR, 'div.notification-action-item')

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self._notifications = ComponentPiece(
            locator=self._NOTIFICATION_LOCATOR,
            driver=driver,
            description="A generic notification, used primarily for determining presence.",
            wait_timeout=0)
        self._close_icon = ComponentPiece(
            locator=self._CLOSE_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self._notifications.locator_list,
            description="The 'X' icon in the upper-right of notifications which allow for dismissal.",
            wait_timeout=0)
        self._body = ComponentPiece(
            locator=self._BODY_LOCATOR,
            driver=driver,
            parent_locator_list=self._notifications.locator_list,
            description="The body of the Notification, where the details and summary reside.",
            wait_timeout=0)
        self._icon = ComponentPiece(
            locator=self._ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self._body.locator_list,
            description="The icon on the left-hand side of the Notification.",
            wait_timeout=0)
        self._summary = ComponentPiece(
            locator=self._SUMMARY_LOCATOR,
            driver=driver,
            parent_locator_list=self._body.locator_list,
            description="The summary (short description) of what the Notification is in regard to.",
            wait_timeout=0)
        self._details = ComponentPiece(
            locator=self._DETAILS_LOCATOR,
            driver=driver,
            parent_locator_list=self._body.locator_list,
            description="The in-depth details of the Notification.",
            wait_timeout=0)
        self._action_item = ComponentPiece(
            locator=self._ACTION_ITEM_LOCATOR,
            driver=driver,
            parent_locator_list=self._notifications.locator_list,
            description="The interactive piece of the Notification, used to reset or ignore the Notification.",
            wait_timeout=0
        )

    def any_notification_is_visible(self) -> bool:
        """
        Determine if any notification is currently visible.

        :returns: True, if any Notification is visible - False otherwise.
        """
        try:
            return self.get_count_of_current_notifications() > 0
        except TimeoutException:
            return False

    def close_any_notifications(self) -> None:
        """
        Close all displayed notifications.

        :raises TimeoutException: If any of the Notifications does not allow for dismissal.
        """
        while self.any_notification_is_visible():
            self._close_icon.click(binding_wait_time=1)  # glorified sleep

    def get_count_of_current_notifications(self) -> int:
        """
        Obtain a count of how many Notifications are currently displayed.

        :returns: A count of the number of displayed Notifications.
        """
        try:
            return len(self._notifications.find_all(wait_timeout=0))
        except TimeoutException:
            return 0

    def get_details(self, notification_index: int = 0) -> str:
        """
        Obtain the full details of the Notification.

        :param notification_index: The zero-based index of the Notification to target.

        :returns: The in-depth details portion of the Notification.

        :raises IndexError: If the supplied index is invalid based on the number of displayed notifications.
        """
        return self._details.find_all(wait_timeout=0)[notification_index].text

    def get_details_color(self, notification_index: int = 0) -> str:
        """
        Obtain the color in use for the details of the Notification. Note that some browsers may return the color in
        different formats (RGB vs hex).

        :param notification_index: The zero-based index of the Notification to target.

        :returns: The color of the details text, as a string.

        :raises IndexError: If the supplied index is invalid based on the number of displayed notifications.
        """
        return self._details.find_all(wait_timeout=0)[notification_index].value_of_css_property(CSS.COLOR.value)

    def get_icon_color(self, notification_index: int = 0) -> str:
        """
        Obtain the color in use for the fill of the icon of the Notification. Note that some browsers may return the
        color in different formats (RGB vs hex).

        :param notification_index: The zero-based index of the Notification to target.

        :returns: The color (fill) of the icon, as a string.

        :raises IndexError: If the supplied index is invalid based on the number of displayed notifications.
        """
        return self._icon.find_all(wait_timeout=0)[notification_index].value_of_css_property(CSS.FILL.value)

    def get_icon_id(self, notification_index: int = 0) -> str:
        """
        Obtain the id (name) of the icon in use for the Notification.

        :param notification_index: The zero-based index of the Notification to target.

        :returns: The id in use by the svg (icon) of the Notification.

        :raises IndexError: If the supplied index is invalid based on the number of displayed notifications.
        """
        return self._icon.find_all(
            wait_timeout=0)[notification_index].find_element(By.TAG_NAME, "symbol").get_attribute("id")

    def get_summary(self, notification_index: int = 0) -> str:
        """
        Obtain the summary of the Notification.

        :param notification_index: The zero-based index of the Notification to target.

        :returns: The summary (short description) of the Notification.

        :raises IndexError: If the supplied index is invalid based on the number of displayed notifications.
        """
        return self._summary.find_all(wait_timeout=0)[notification_index].text

    def get_summary_color(self, notification_index: int = 0) -> str:
        """
        Obtain the color in use for the summary of the Notification. Note that some browsers may return the color in
        different formats (RGB vs hex).

        :param notification_index: The zero-based index of the Notification to target.

        :returns: The color of the summary text, as a string.

        :raises IndexError: If the supplied index is invalid based on the number of displayed notifications.
        """
        return self._summary.find_all(wait_timeout=0)[notification_index].value_of_css_property(CSS.COLOR.value)

    def click_notification_action(self, notification_index: int = 0) -> None:
        """
        Click the action item of the Notification.

        :param notification_index: The zero-based index of the Notification to target.

        :raises IndexError: If the supplied index is invalid based on the number of displayed notifications.
        """
        self._notifications.find_all(
            wait_timeout=0)[notification_index].find_element(*self._ACTION_ITEM_LOCATOR).click()
