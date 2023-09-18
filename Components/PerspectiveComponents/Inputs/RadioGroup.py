from enum import Enum
from typing import Tuple, List, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Components.PerspectiveComponents.Common.Icon import CommonIcon


class RadioGroup(BasicPerspectiveComponent):
    """
    A Perspective Radio Group Component. A Radio Group component typically contains multiple buttons. Interaction
    preference is via the text of each button, though value may also be supplied.
    """
    _INTERNAL_RADIO_GROUP_LABEL_TEXT_LOCATOR = (By.CSS_SELECTOR, "label.ia_radioGroupComponent_text")
    _WRAPPER_CLASS = "ia_radioGroupComponent_radioWrapper"
    _RADIO_GROUP_BUTTON_VALUE_LOCATOR = (By.TAG_NAME, "input")
    _RADIO_GROUP_FORM_LOCATOR = (By.CSS_SELECTOR, "form")

    class Orientation(Enum):
        COLUMN = "column"
        ROW = "row"

    class TextPosition(Enum):
        BOTTOM = "bottom"
        LEFT = "left"
        RIGHT = "right"
        TOP = "top"

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
        self._radio_group_form = ComponentPiece(
            locator=self._RADIO_GROUP_FORM_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1)
        self._internal_radio_group_label_text = ComponentPiece(
            locator=self._INTERNAL_RADIO_GROUP_LABEL_TEXT_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1)
        self._radio_group_button_value = ComponentPiece(
            locator=self._RADIO_GROUP_BUTTON_VALUE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1)
        self._radio_wrapper_coll = {}
        self._input_coll = {}
        self._icon_coll = {}
        self._label_coll = {}

    def click_radio_button(
            self, button_text: str = None, button_value: str = None, binding_wait_time: float = 2) -> None:
        """
        Click a Radio Button by supplying either the text of the Radio button or the value of the Radio button. The
        actual click will occur on the label for the Radio button.

        :param button_text: The text of the Radio button you would like to click. If multiple radio buttons have the
            same exact text the first match will be clicked. Takes precedence over button_value.
        :param button_value: The value of the Radio button you would like to click.
        :param binding_wait_time: The amount of time after any click event before we allow code to continue.

        :raises TimeoutException: If no Radio button with the provided text or value is present.
        """
        self._get_label(button_text=button_text, button_value=button_value).click(binding_wait_time=binding_wait_time)

    def get_count_of_radio_buttons_in_group(self) -> int:
        """Get a count of buttons within the Radio Group."""
        return len(self._radio_group_button_value.find_all())

    def has_orientation(self, orientation: Orientation) -> bool:
        """
        Determine if the Radio Group currently has the supplied orientation.

        :param orientation: The orientation you hope to verify the Radio Group is currently using.
        """
        return f"radio-form-{orientation.value}" in self._radio_group_form.find().get_attribute('class')

    def has_text_position(self, expected_text_position: TextPosition) -> bool:
        """
        Determine if the labels of the Radio Group currently have the supplied relative positioning.

        :param expected_text_position: The position relative to the 'button' you hope to verify the text labels
            currently have.
        """
        return f"ia_radioGroupComponent_text--{expected_text_position.value}" in \
            self._internal_radio_group_label_text.find().get_attribute('class')

    def option_is_selected(self, button_text: str = None, button_value: str = None) -> bool:
        """
        Determine if the Radio button identified by the text or value is currently selected.

        :param button_text: The text of the Radio button for which you would like to check the selection state. If
            multiple radio buttons have the same exact text the first match will have its selection state checked.
            Takes precedence over button_value.
        :param button_value: The value of the Radio button for which you would like to check the selection state.

        :returns: True, if a Radio button with text matching the supplied button_text is currently selected, or - if
            button_text was not supplied - if a Radio button matching the supplied button_value is selected.
        """
        try:
            return self._get_input(button_text=button_text, button_value=button_value).find().is_selected()
        except TimeoutException:
            return False

    def _get_icon(self, button_text: str = None, button_value: str = None) -> CommonIcon:
        """
        Obtain the CommonIcon in use for the button of the Radio Group.

        :param button_text: The text of the Radio button from which you'd like the icon. If multiple radio buttons have
            the same exact text the first match will be selected. Takes precedence over button_value.
        :param button_value: The value of the Radio button from which you'd like the icon.

        :returns: CommonIcon
        """
        attr_text = button_text if button_text else button_value
        _icon = self._icon_coll.get(attr_text)
        if not _icon:
            _icon = CommonIcon(
                locator=(By.TAG_NAME, "svg"),
                driver=self.driver,
                parent_locator_list=self._get_radio_wrapper(
                    button_text=button_text,
                    button_value=button_value).locator_list)
            self._icon_coll[attr_text] = _icon
        return _icon

    def _get_input(self, button_text: str = None, button_value: str = None) -> ComponentPiece:
        """
        Obtain the HTML input in use for the button of the Radio Group as a ComponentPiece.

        :param button_text: The text of the Radio button from which you'd like the input. If multiple radio buttons have
            the same exact text the first match will be selected. Takes precedence over button_value.
        :param button_value: The value of the Radio button from which you'd like the input.

        :returns: ComponentPiece
        """
        attr_text = button_text if button_text else button_value
        _input = self._input_coll.get(attr_text)
        if not _input:
            _input = ComponentPiece(
                locator=(By.TAG_NAME, "input"),
                driver=self.driver,
                parent_locator_list=self._get_radio_wrapper(
                    button_text=button_text,
                    button_value=button_value).locator_list)
            self._input_coll[attr_text] = _input
        return _input

    def _get_label(self, button_text: str = None, button_value: str = None) -> ComponentPiece:
        """
        Obtain the label in use for the button of the Radio Group as a ComponentPiece.

        :param button_text: The text of the Radio button from which you'd like the label. If multiple radio buttons have
            the same exact text the first match will be selected. Takes precedence over button_value.
        :param button_value: The value of the Radio button from which you'd like the label.

        :returns: ComponentPiece
        """
        attr_text = button_text if button_text else button_value
        label = self._label_coll.get(attr_text)
        if not label:
            label = ComponentPiece(
                locator=(By.TAG_NAME, "label"),
                driver=self.driver,
                parent_locator_list=self._get_radio_wrapper(
                    button_text=button_text,
                    button_value=button_value).locator_list)
            self._label_coll[attr_text] = label
        return label

    def _get_radio_wrapper(self, button_text: str = None, button_value: str = None) -> ComponentPiece:
        """
        Obtain the wrapper in use for the button of the Radio Group as a ComponentPiece. This wrapper contains the
        input, icon, and label for the 'button'.

        :param button_text: The text of the Radio button from which you'd like the wrapper. If multiple radio buttons
            have the same exact text the first match will be selected. Takes precedence over button_value.
        :param button_value: The value of the Radio button from which you'd like the wrapper.

        :returns: ComponentPiece
        """
        assert button_text is not None or button_value is not None, \
            "You must supply either the text or value of the button"
        attr_text = button_text if button_text else button_value
        wrapper = self._radio_wrapper_coll.get(attr_text)
        if not wrapper:
            locator_piece = f'[data-{"label" if button_text else "value"}="{attr_text}"]'
            wrapper = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'div.{self._WRAPPER_CLASS}{locator_piece}'),
                driver=self.driver,
                parent_locator_list=self.locator_list)
            self._radio_wrapper_coll[attr_text] = wrapper
        return wrapper
