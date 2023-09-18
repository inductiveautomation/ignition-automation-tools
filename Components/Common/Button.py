from typing import Tuple, List, Optional, Union

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece
from Components.PerspectiveComponents.Common.Icon import CommonIcon
from Helpers.CSSEnumerations import CSSPropertyValue
from Helpers.Point import Point


class CommonButton(ComponentPiece):
    """
    A common button, exposing common functions which EVERY button in Perspective can use. This includes buttons within
    other components, like the Acknowledge button found inside the Alarm Status Table component.
    """
    _INTERNAL_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button')
    _INTERNAL_ICON_LOCATOR = (By.TAG_NAME, "svg")
    _INTERNAL_TEXT_LOCATOR = (By.CSS_SELECTOR, "div.text")
    _INTERNAL_IMAGE_LOCATOR = (By.TAG_NAME, "img")
    PRIMARY_CLASS = 'ia_button--primary'
    SECONDARY_CLASS = 'ia_button--secondary'

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 10,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._internal_button = ComponentPiece(
            locator=self._INTERNAL_BUTTON_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            description="The internal HTML <button> element of the Button.",
            poll_freq=poll_freq)
        self._internal_icon = CommonIcon(
            locator=self._INTERNAL_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            description="The icon in use by the Button.",
            poll_freq=poll_freq)
        self._internal_text = ComponentPiece(
            locator=self._INTERNAL_TEXT_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            description="The container in which the text of the Button resides.",
            poll_freq=poll_freq)
        self._internal_image = ComponentPiece(
            locator=self._INTERNAL_IMAGE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            description="The image within the Button.",
            poll_freq=poll_freq)

    def click(self, wait_timeout=None, binding_wait_time: float = 0.5) -> None:
        """
        Click the button.
        """
        _button = self._get_html_button()
        if _button == self:
            super().click(wait_timeout=wait_timeout, binding_wait_time=binding_wait_time)
        else:
            _button.click(wait_timeout=wait_timeout, binding_wait_time=binding_wait_time)

    def get_css_property_of_icon(self, property_name: Union[CSSPropertyValue, str]) -> str:
        """
        Get some CSS property value of the icon within the button.
        """
        return self._internal_icon.get_css_property(property_name=property_name)

    def get_origin_of_icon(self) -> Optional[Point]:
        """
        Obtain the origin of the icon contained within this Button.

        :returns: A Point which marks the upper-left corner of the icon contained within this button, or None if no icon
            is present within the Button.
        """
        try:
            return self._internal_icon.get_origin()
        except TimeoutException:
            return None

    def get_origin_of_text(self) -> Optional[Point]:
        """
        Obtain the origin of the text of this Button.

        :returns: A Point which marks the upper-left corner of the text contained within this button, or None if no text
            is present within the Button.
        """
        try:
            return self._internal_text.get_origin()
        except TimeoutException:
            return None

    def icon_is_present_in_button(self) -> bool:
        """
        Determine if the Button contains an icon. This is not the same as :func:`icon_is_displayed_in_button`, which
        determines VISIBILITY of any such icon.

        :returns: True, if an image is currently present inside the button - False otherwise.
        """
        try:
            return self._internal_icon.find() is not None
        except TimeoutException:
            return False

    def icon_is_displayed_in_button(self) -> bool:
        """
        Determine if the Button is displaying an internal icon.

        :returns: True, if an icon is currently displayed inside the button - False otherwise.
        """
        try:
            return self._internal_icon.find().is_displayed()
        except TimeoutException:
            return False

    def image_is_displayed_in_button(self) -> bool:
        """
        Determine if the Button is displaying an internal image.

        :returns: True, if an image is currently displayed inside the button - False otherwise.
        """
        try:
            return self._internal_image.find().is_displayed()
        except TimeoutException:
            return False

    def is_enabled(self) -> bool:
        """
        Determine if this Button is enabled.

        :returns: True, if the Button is currently enabled - False otherwise.
        """
        return self._get_html_button().find().is_enabled()

    def is_primary(self) -> bool:
        """
        Determine if this button is currently displaying as a Primary Button.

        :returns: True, if this button is currently displaying as a Primary Button - False otherwise.
        """
        clazz = self.find().get_attribute("class")
        return (self.PRIMARY_CLASS in clazz) and (self.SECONDARY_CLASS not in clazz)

    def is_secondary(self) -> bool:
        """
        Determine if this button is currently displaying as a Secondary Button.

        :returns: True, if this button is currently displaying as a Secondary Button - False otherwise.
        """
        clazz = self.find().get_attribute("class")
        return (self.SECONDARY_CLASS in clazz) and (self.PRIMARY_CLASS not in clazz)

    def _get_html_button(self) -> ComponentPiece:
        """
        Obtain the true button of this component.

        :returns: A ComponentPiece which may be used as a <button>.
        """
        if self.find().tag_name != 'button':
            return self._internal_button
        else:
            return self
