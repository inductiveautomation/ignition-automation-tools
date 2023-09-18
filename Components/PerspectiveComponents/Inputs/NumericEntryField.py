from typing import Optional, Union, List, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Components.Common.Button import CommonButton
from Components.Common.TextInput import CommonTextInput
from Components.PerspectiveComponents.Common.ComponentModal import ComponentModal
from Helpers.IAAssert import IAAssert
from Helpers.IAExpectedConditions.IAExpectedConditions import TextCondition
from Helpers.IASelenium import IASelenium
from Helpers.Point import Point


def _remove_commas(value: Union[float, str]) -> str:
    """
    Without any formatting modifications to a default Numeric Entry Field, Numeric Entry Fields display commas as part
    of their text. This of course wreaks havoc when doing comparisons against expected values, so remove any commas from
    all values. This requires that we convert/cast the value to a string.

    :param value: The value which will have all commas removed.

    :return: The supplied value with all commas removed, as a string.
    """
    return str(value).replace(",", "")


def _zero_out(expected_value: Union[float, str]) -> Union[float, str]:
    """
    When users supply an empty string, Numeric Entry Fields fall back to 0

    :param expected_value: The original value expected to be displayed.

    :return: 0, if the supplied value for the Numeric Entry Field is an empty string - otherwise the current value.
    """
    return 0 if expected_value == "" else expected_value


class ButtonNEF(BasicPerspectiveComponent, CommonTextInput):
    """A Button-variant Perspective Numeric Entry Field, as distinct from the Direct or Protected variants."""
    _APPLY_BUTTON_LOCATOR = (By.CSS_SELECTOR, "button.ia_button--primary")
    _CANCEL_BUTTON_LOCATOR = (By.CSS_SELECTOR, "button.ia_button--secondary")
    _MODAL_INPUT_LOCATOR = (By.TAG_NAME, "input")  # within modal

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 2,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        BasicPerspectiveComponent.__init__(
            self,
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        CommonTextInput.__init__(
            self,
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._edit_icon = ComponentPiece(
            locator=(By.TAG_NAME, "a"),
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._modal = ComponentModal(
            driver=driver,
            wait_timeout=1,
            poll_freq=poll_freq)  # no parent
        self._apply_button = CommonButton(
            locator=self._APPLY_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self._modal.locator_list,
            poll_freq=poll_freq)
        self._cancel_button = CommonButton(
            locator=self._CANCEL_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self._modal.locator_list,
            poll_freq=poll_freq)
        self._modal_input = CommonTextInput(
            locator=self._MODAL_INPUT_LOCATOR,
            driver=driver,
            parent_locator_list=self._modal.locator_list,
            poll_freq=poll_freq)

    def click_apply(self) -> None:
        """
        Click the Apply button in the entry modal.

        :raises TimeoutException: If the Apply Button (and/or entry modal) is not present.
        """
        self._apply_button.click()

    def click_cancel(self) -> None:
        """
        Click the Cancel button in the entry modal.

        :raises TimeoutException: If the Cancel Button (and/or entry modal) is not present.
        """
        self._cancel_button.click()

    def click_edit_icon(self) -> None:
        """Click the icon used to edit the value of the Numeric Entry Field."""
        return self._edit_icon.click()

    def get_modal_origin(self) -> Point:
        """
        Obtain the origin (top-left corner) of the entry modal.

        :returns: A Point which contains the x,y coordinates of the top-left of the entry modal.

        :raises TimeoutException: if the entry modal is not displayed.
        """
        return self._modal.get_origin()

    def modal_is_displayed(self) -> bool:
        """
        Determine if the entry modal is currently displayed.

        :returns: True, if the entry modal is displayed - False otherwise.
        """
        try:
            return self._modal.find() is not None
        except TimeoutException:
            return False

    def set_text(
            self,
            text: Union[float, str],
            apply_cancel_no_action: Optional[bool] = True,
            binding_wait_time: float = 0.5) -> None:
        """
        Convenience function to set the text of the Numeric Entry Field. Handles the opening of the entry modal and also
        applies, cancels, or takes no action as directed via arguments.

        :param text: The value which you would like to apply to the Numeric Entry Field.
        :param apply_cancel_no_action: If True, apply changes. If False, cancel changes after typing supplied text. If
            None, take no action - leaving the entry modal displayed without any changes committed.
        :param binding_wait_time: The amount of time to wait after applying or cancelling changes. Ignored if no action
            is to be taken after sending text.

        :raises AssertionError: If application or cancellation is specified, and the final displayed (and formatted)
            value of the Numeric Entry Field does not match the supplied text.
        """
        self.click_edit_icon()
        self._set_text(text=text)
        if apply_cancel_no_action is not None:
            self.click_apply() if apply_cancel_no_action else self.click_cancel()
            self._modal_input.wait_on_binding(time_to_wait=binding_wait_time)
            # assertion needs to go here as it does not make sense to assert if the value has not yet been committed.
            IAAssert.is_equal_to(
                actual_value=_remove_commas(
                    value=self.wait_on_text_condition(
                        text_to_compare=text, condition=TextCondition.EQUALS)),
                expected_value=_remove_commas(value=_zero_out(expected_value=text)),
                failure_msg="Failed to set the text of the Button-mode Numeric Entry Field.",
                as_type=str)

    def _set_text(self, text: Union[float, str]) -> None:
        """
        Set the text of the Numeric Entry Field by interacting with the already-opened entry modal.

        :param text: The text to apply to the input of the entry modal.
        """
        self._modal_input.click()
        self.driver.execute_script('arguments[0].value = ""', self._modal_input.find())
        self._modal_input.find().send_keys(text)


class DirectNEF(BasicPerspectiveComponent, CommonTextInput):
    """A Direct-variant Perspective Numeric Entry Field, as distinct from the Button or Protected variants."""

    def __init__(
            self,
            locator,
            driver: WebDriver,
            parent_locator_list: Optional[List] = None,
            wait_timeout: float = 5,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        BasicPerspectiveComponent.__init__(
            self,
            locator=locator, 
            driver=driver, 
            parent_locator_list=parent_locator_list, 
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        CommonTextInput.__init__(
            self,
            locator=locator, 
            driver=driver, 
            parent_locator_list=parent_locator_list, 
            wait_timeout=wait_timeout,
            poll_freq=poll_freq)

    def get_manual_entry_text(self) -> str:
        """
        Obtain the text of the Numeric Entry Field as a user sees it while typing. Distinct from get_text as this
        function will return an un-formatted value.

        Example: A user might type '14', but formatting for the component could display the committed value as '14.0'.
        This function will return the "typed" value of '14' instead of the formatted '14.0' value.

        :returns: The un-formatted value of the Numeric Entry Field.
        """
        if self.find().tag_name == "input":
            return self.find().get_attribute("value")
        else:
            self._internal_input.click()
            text = self._internal_input.find().get_attribute("value")
            self._internal_input.find().send_keys(Keys.ENTER)  # ENTER to avoid closing any popup
            return text

    def set_text(
            self,
            text: Union[float, int, str],
            release_focus: bool = True,
            binding_wait_time: float = 1) -> None:
        """
        Set the text of the Direct Numeric Entry Field.

        :param text: The value which you would like to apply to the Numeric Entry Field.
        :param release_focus: Specifies whether to commit the text after typing.
        :param binding_wait_time: The amount of time to wait after applying or cancelling changes. Ignored if no action
            is to be taken after sending text.

        :raises AssertionError: If the final displayed (and formatted) value of the Numeric Entry Field does not match
            the supplied text after releasing focus.
        """
        self._internal_input.click()
        if self._internal_input.find().get_attribute('readonly') is not None:
            self._internal_input.click()
        self._internal_input.find().send_keys(Keys.BACK_SPACE + str(text) + (Keys.ENTER if release_focus else ''))
        self.wait_on_binding(time_to_wait=binding_wait_time)
        if release_focus:
            IAAssert.is_equal_to(
                actual_value=_remove_commas(
                    value=self.wait_on_text_condition(
                        text_to_compare=text, condition=TextCondition.EQUALS)),
                expected_value=_remove_commas(value=_zero_out(expected_value=text)),
                failure_msg="Failed to apply the supplied text to the Direct-variant Numeric Entry Field.",
                as_type=str)


class ProtectedNEF(DirectNEF):
    """
    A Protected-variant Numeric Entry Field Component.

    Protected NEFs change their structure during interaction, so unique locators are very important. A Protected NEF
    without a unique ID is likely to fail the interaction process.
    """

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

    def set_text(
            self,
            text: Union[float, int, str],
            release_focus: bool = True,
            binding_wait_time: float = 1) -> None:
        """
        Pass-through function to set the text of the Protected Numeric Entry Field via double-click.

        :param text: The value which you would like to apply to the Numeric Entry Field.
        :param release_focus: Specifies whether to commit the text after typing.
        :param binding_wait_time: The amount of time to wait after applying or cancelling changes. Ignored if no action
            is to be taken after sending text.

        :raises AssertionError: If the final displayed (and formatted) value of the Numeric Entry Field does not match
             the supplied text.
        """
        self.set_text_via_double_click(
            text=text,
            release_focus=release_focus,
            binding_wait_time=binding_wait_time)

    def set_text_via_double_click(
            self,
            text: Union[float, int, str],
            release_focus: bool = True,
            binding_wait_time: float = 1) -> None:
        """
        Set the text of the Protected Numeric Entry Field via double-click.

        :param text: The value which you would like to apply to the Numeric Entry Field.
        :param release_focus: Specifies whether to commit the text after typing.
        :param binding_wait_time: The amount of time to wait after applying or cancelling changes. Ignored if no action
            is to be taken after sending text.

        :raises AssertionError: If the final displayed (and formatted) value of the Numeric Entry Field does not match
             the supplied text.
        """
        IASelenium(driver=self.driver).double_click(web_element=self.find())
        self._set_text(text=str(text), release_focus=release_focus)
        self.wait_on_binding(time_to_wait=binding_wait_time)
        if release_focus:
            IAAssert.is_equal_to(
                actual_value=_remove_commas(
                    value=self.wait_on_text_condition(
                        text_to_compare=text, condition=TextCondition.EQUALS)),
                expected_value=_remove_commas(value=_zero_out(expected_value=text)),
                failure_msg="Failed to apply the supplied text to the Protected-variant Numeric Entry Field.",
                as_type=str)

    def set_text_via_long_press(
            self,
            text: str,
            release_focus: bool = True,
            binding_wait_time: float = 1) -> None:
        """
        Set the text of the Protected Numeric Entry Field via a long-press.

        :param text: The value which you would like to apply to the Numeric Entry Field.
        :param release_focus: Specifies whether to commit the text after typing.
        :param binding_wait_time: The amount of time to wait after applying or cancelling changes. Ignored if no action
            is to be taken after sending text.

        :raises AssertionError: If the final displayed (and formatted) value of the Numeric Entry Field does not match
             the supplied text after releasing focus.
        """
        IASelenium(driver=self.driver).long_click(web_element=self.find())
        self._set_text(text=str(text), release_focus=release_focus)
        self.wait_on_binding(time_to_wait=binding_wait_time)
        if release_focus:
            IAAssert.is_equal_to(
                actual_value=_remove_commas(
                    value=self.wait_on_text_condition(
                        text_to_compare=text, condition=TextCondition.EQUALS)),
                expected_value=_remove_commas(value=_zero_out(expected_value=text)),
                failure_msg="Failed to apply the supplied text to the Protected-variant Numeric Entry Field while "
                            "activating the input via a long-press interaction.",
                as_type=str)

    def _set_text(self, text: str, release_focus: bool = False) -> None:
        """
        Set the text of the Protected Numeric Entry Field after interaction has been triggered via a long-press.

        :param text: The text to supply to the Numeric Entry Field
        :param release_focus: Specifies whether to commit the typed value.
        """
        self.driver.execute_script('arguments[0].value = ""', self.find())
        self._internal_input.find().send_keys(str(text) + (Keys.ENTER if release_focus else ''))
