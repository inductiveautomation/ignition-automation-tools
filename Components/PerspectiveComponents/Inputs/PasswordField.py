from typing import Optional, Union, List, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent
from Components.Common.TextInput import CommonTextInput
from Components.PerspectiveComponents.Common.Icon import CommonIcon


class PasswordField(BasicPerspectiveComponent):
    """A Perspective Password Field Component."""
    _SHOW_PASSWORD_ICON_LOCATOR = (By.CSS_SELECTOR, 'a.ia_passwordFieldComponent__visibilityLink')

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
        self._internal_input = CommonTextInput(
            locator=(By.TAG_NAME, "input"),
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=2,
            poll_freq=poll_freq)
        self._icon = CommonIcon(
            locator=self._SHOW_PASSWORD_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)

    def display_password(self, should_be_displayed: bool) -> None:
        """
        Activate the visibility toggle for the field so that the text is displayed.

        :raises TimeoutException: If the ability to toggle visibility is not enabled for the component.
        """
        if self.password_is_displayed() != should_be_displayed:
            self._icon.click()

    def get_displayed_text(self) -> str:
        """
        Get the human-readable text from the Password Field. Note that due rules applied to the underlying HTML element
        this function should only ever return an empty string.

        :returns: An empty string if the component is working as expected, because the 'visible' text is not actually
            present in the DOM.
        """
        # We must NOT use TextField's get_text() method as it actually pulls the value - as opposed
        # to the visible text. That being said, even grabbing the WebElement's text should only ever
        # give us an empty String for the Password Field.
        return self._internal_input.find().text

    def get_placeholder_text(self) -> str:
        """
        Obtain the placeholder text of the component. Note that this value is returned even when the Password Field is
        not currently displaying the placeholder text.

        :returns: The text the Password Field would use as placeholder text, regardless of whether or not this text is
            currently being used.
        """
        return self._internal_input.find().get_attribute("placeholder")

    def password_is_displayed(self) -> bool:
        """
        Determine if the content supplied as a password is currently being displayed to the user.

        :returns: True, if the user may currently see the password content as text - False if the user is seeing the
            masked (asterisks) content.
        """
        return self._internal_input.find().get_attribute("type") == "text"

    def placeholder_text_exists(self) -> bool:
        """
        Determine if placeholder text is currently configured for the Password Field. Does not reflect current use.

        :returns: True, if placeholder text is configured, regardless of current use - False if not placeholder text is
            configured.
        """
        return self.get_placeholder_text() is not None

    def set_text(
            self,
            text: Union[int, float, str],
            release_focus: bool = True,
            binding_wait_time: float = 0) -> None:
        """
        Set the text content of the Password Field.

        :param text: The text content you would like to set the Password Field to contain.
        :param release_focus: Dictates whether the ENTER Key is supplied as a means to commit the value.
        :param binding_wait_time: The amount of time to wait after applying the supplied text before we allow code to
            continue.
        """
        self._internal_input.find().clear()
        text = text + Keys.ENTER if release_focus else text
        self._internal_input.find().send_keys(text)
        self.wait_on_binding(time_to_wait=binding_wait_time)

    def show_password_icon_is_visible(self) -> bool:
        """
        Determine if the Password Field is currently displaying the icon used to toggle content visibility.

        :returns: True, if the icon is visible - False otherwise.
        """
        return self._icon.is_rendered() and self._icon.find().is_displayed()
