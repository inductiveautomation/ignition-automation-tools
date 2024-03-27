from typing import Optional, Union, Tuple, List

from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece
from Helpers.IAAssert import IAAssert
from Helpers.IAExpectedConditions.IAExpectedConditions import TextCondition


class CommonTextInput(ComponentPiece):
    """A common-use input field."""
    _INTERNAL_INPUT_LOCATOR = (By.TAG_NAME, "input")

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
        # The internal input piece is important for when our component has a quality overlay because any reference
        # made using something like an id would now refer to the <div> level instead.
        self._internal_input = ComponentPiece(
            locator=self._INTERNAL_INPUT_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            description="The internal <input> element, used primarily for Text Fields, or when the component contains "
                        "a quality overlay.",
            poll_freq=poll_freq)

    def get_placeholder_text(self) -> str:
        """
        Obtain the text in use as a placeholder for this component.

        :returns: The text a user sees within this component when no value has been supplied.
        """
        return self.find().get_attribute("placeholder")

    def get_text(self) -> str:
        """
        Obtain the text contained within this component.

        :returns: The text contents of the component via the `value` attribute.
        """
        input_component = self._internal_input if self._needs_to_get_input_element() else self
        return input_component.find().get_attribute("value")

    def placeholder_text_exists(self) -> bool:
        """
        Determine if a component is currently displaying placeholder text.

        :returns: True, if a component is currently displaying placeholder text - False otherwise.
        """
        return (self.find().get_attribute("placeholder") is not None) and (self.find().get_attribute("value") is None)

    def set_text(
            self,
            text: Union[float, str],
            release_focus: bool = True,
            binding_wait_time: float = 0) -> None:
        """
        Set the value of this component.

        :param text: The text to type into the field.
        :param release_focus: Dictates whether a blur() event is invoked for the component after typing the supplied
            text.
        :param binding_wait_time: The amount of time (in seconds) to wait after typing the supplied text before allowing
            code to continue.
        """
        text = str(text)
        # strip special characters (ESC, ENTER) while leaving spaces and punctuation
        expected_text = text.encode("ascii", "ignore").decode()
        if text is None or text == '':
            text = ' ' + Keys.BACKSPACE
        self.wait_on_text_condition(text_to_compare="", condition=TextCondition.DOES_NOT_EQUAL, wait_timeout=0.5)
        current_text = self.get_text()  # Do NOT wait on matching text to be in place
        keys_to_send = ''.join([Keys.ARROW_RIGHT for _ in current_text] +
                               [Keys.BACKSPACE for _ in current_text] +
                               [text])
        self.scroll_to_element()
        input_object = self
        if self._needs_to_get_input_element():
            input_object = self._internal_input
        try:
            input_object.click()
        except ElementClickInterceptedException:
            # quality overlay interference
            ActionChains(driver=self.driver) \
                .move_to_element_with_offset(to_element=input_object.find(), xoffset=5, yoffset=5) \
                .click() \
                .perform()
        input_object.find().send_keys(keys_to_send)
        if release_focus:
            self.release_focus()
        IAAssert.is_equal_to(
            actual_value=self.wait_on_text_condition(
                text_to_compare=expected_text, condition=TextCondition.EQUALS, wait_timeout=binding_wait_time + 0.5),
            expected_value=expected_text,
            failure_msg="Failed to set the value of the input.")
        self.wait_on_binding(time_to_wait=binding_wait_time)

    def _needs_to_get_input_element(self) -> bool:
        """
        Determine if the Component IS the <input>, or if we should instead query for the internal <input>.

        :returns: True, if the current component definition would fail to operate as an <input> - False otherwise.
        """
        return self.find().tag_name not in ['input', 'textarea']
