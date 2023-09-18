from typing import Optional, Tuple, List

from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece
from Components.PerspectiveComponents.Common.Icon import CommonIcon
from Helpers.IAAssert import IAAssert
from Helpers.IAExpectedConditions import IAExpectedConditions as IAec


class CommonCheckbox(ComponentPiece):
    """A Common Checkbox, as might be used within a larger component."""
    _DISABLED_CLASS = "ia_checkbox--disabled"
    _CLICK_TARGET_LOCATOR = (By.CSS_SELECTOR, "label.ia_checkbox")
    _LABEL_TEXT_LOCATOR = (By.CSS_SELECTOR, "label.checkbox-input-label")
    _ICON_LOCATOR = (By.TAG_NAME, "svg")
    _INPUT_LOCATOR = (By.TAG_NAME, "input")

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
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
        self._click_target = ComponentPiece(
            locator=self._CLICK_TARGET_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq,
            description="The actual visible checkbox a user would click.")
        self._text_label = ComponentPiece(
            locator=self._LABEL_TEXT_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq,
            description="The actual text a user should see for the Checkbox.")
        self._icon = CommonIcon(
            locator=self._ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq,
            description="The actual text a user should see for the Checkbox.")
        self._input = ComponentPiece(
            locator=self._INPUT_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)

    def click(self, wait_timeout: Optional[float] = None, binding_wait_time: float = 0) -> None:
        """
        Click the Checkbox.

        If attempting to set the checkbox to a known state, :func:`set_state` is preferred.

        :param wait_timeout: The amount of time you are willing to wait for the checkbox to appear before attempting
            to perform the click. Overrides the component's original wait.
        :param binding_wait_time: The amount of time after the click occurs before allowing code to continue.
        """
        self._click_target.click(wait_timeout=wait_timeout, binding_wait_time=binding_wait_time)

    def get_checkbox_state(self) -> Optional[bool]:
        """
        Obtain the state of the checkbox.

        :returns: True, if checked. False, if un-checked. None, if indeterminate (tri-state).
        """
        return None if self._is_indeterminate() else self.is_checked()

    def get_direction_of_label_text(self) -> str:
        """
        Obtain the direction of the text as a string. This value describes the location of the text relative to the
        Checkbox.
        """
        return self._text_label.find().get_attribute("class").split("--")[-1]

    def get_label_text(self) -> str:
        """Obtain the text of the label of the checkbox."""
        return self._text_label.find().text

    def get_path_of_icon(self) -> str:
        """
        Obtain a slash-delimited path of the icon currently in use for the checkbox.
        """
        return self._icon.get_icon_name()

    def is_checked(self) -> bool:
        """
        Determine if the checkbox is currently 'checked'. Preferred function is :func:`get_checkbox_state` as it handles
        tri-state checkboxes as well.

        :returns: True, if the checkbox is checked - False if the checkbox is un-checked or indeterminate.
        """
        try:
            return self._icon.find().get_attribute("data-state") == "checked"
        except StaleElementReferenceException:
            # check again
            return self.is_checked()

    def is_enabled(self) -> bool:
        """
        Determine if the Checkbox is currently enabled.

        :returns: True, if the Checkbox is enabled - False otherwise.
        """
        try:
            return self.wait.until(IAec.function_returns_true(
                custom_function=self._is_enabled, function_args={}))
        except TimeoutException:
            return False

    def set_state(self, should_be_checked: Optional[bool], binding_wait_time: float = 0) -> None:
        """
        Set the checkbox to a specified state.
        :param binding_wait_time: How long to wait before allowing the code to continue.
        :param should_be_checked: True if the Checkbox should be selected, False if it should not be selected, or None
            if the checkbox is a tri-state checkbox and should be 'indeterminate'.
        """
        self._set_state(should_be_checked=should_be_checked, binding_wait_time=binding_wait_time)

    def _is_enabled(self) -> bool:
        """Determine if the checkbox is enabled."""
        return self._input.find().is_enabled() and (
                self._DISABLED_CLASS not in self._click_target.find().get_attribute("class"))

    def _is_indeterminate(self) -> bool:
        """
        Determine if the Checkbox is currently displaying as 'indeterminate' (tri-state).

        :returns: True, if the Checkbox is currently displaying as indeterminate. False, if the checkbox is checked or
            unchecked.
        """
        return self._icon.find().get_attribute("data-state") == "indeterminate"

    def _set_state(
            self,
            should_be_checked: Optional[bool],
            already_clicked_once: bool = False,
            binding_wait_time: float = 0) -> None:
        """
        Set the checkbox to a specified state.
        :param should_be_checked: True if the Checkbox should be selected, False if it should not be selected, or None
            if the checkbox is a tri-state checkbox and should be 'indeterminate'.
        :param already_clicked_once: Used to prevent possible recursion by preventing additional calls. In theory, we
            should only ever need to call this function twice in a row, in order to swap between the three states.
        """
        if self.get_checkbox_state() != should_be_checked:
            self.click(binding_wait_time=binding_wait_time)
            # could potentially need to click again (checked/unchecked/indeterminate)
            if not already_clicked_once:
                # prevent possible recursion issues
                self._set_state(should_be_checked=should_be_checked, already_clicked_once=True)
        IAAssert.is_equal_to(
            actual_value=self.get_checkbox_state(),
            expected_value=should_be_checked,
            failure_msg="Failed to set the state of a checkbox.")
