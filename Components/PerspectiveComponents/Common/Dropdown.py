import json
from json import JSONDecodeError
from typing import List, Optional, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece
from Components.PerspectiveComponents.Common.ComponentModal import ComponentModal
from Helpers.IAExpectedConditions import IAExpectedConditions as IAec
from Helpers.Point import Point


class CommonDropdown(ComponentPiece):
    """
    A common-use Dropdown, used by the Dropdown component a well as numerous larger components which provide the ability
    to select options form a list.
    """
    COMMON_CLASS = "iaDropdownCommon"
    ACTIVE_CLASS = "ia_dropdown--active"
    _FOCUSED_CLASS = "ia_dropdown--focused"
    _DISABLED_CLASS = 'ia_dropdown__option--disabled'
    _EXPAND_ICON_LOCATOR = (By.CSS_SELECTOR, 'svg.iaDropdownCommon_expandIcon')
    _OPTIONS_CONTAINER = (By.CSS_SELECTOR, 'div.iaDropdownCommon_options')
    _AVAILABLE_OPTION_LOCATOR = (By.CSS_SELECTOR, 'a.iaDropdownCommon_option:not(.ia_dropdown__option__noResults)')

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List] = None,
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
        self._expand_icon = ComponentPiece(
            locator=self._EXPAND_ICON_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._options_modal = ComponentModal(
            driver=self.driver,
            poll_freq=poll_freq)
        self._options_container = ComponentPiece(
            locator=self._OPTIONS_CONTAINER,
            driver=self.driver,
            parent_locator_list=self._options_modal.locator_list,
            poll_freq=poll_freq)
        self._available_options = ComponentPiece(
            locator=self._AVAILABLE_OPTION_LOCATOR,
            driver=driver,
            parent_locator_list=self._options_container.locator_list,
            poll_freq=poll_freq)
        self._option_elements = {}

    def collapse_if_expanded(self) -> None:
        """
        Collapse the dropdown if it is already expanded. No action is taken if the dropdown is currently collapsed.
        """
        if self.is_expanded():
            self.wait_on_binding(0.5)
            # counter-intuitive, but the expand and collapse icons share the same locator
            self.toggle_expansion()

    def get_width_and_height_of_first_available_option(self) -> Tuple[str, str]:
        """
        Obtain the width and height of the first available option within the Dropdown.

        :returns: A Tuple with two elements, where the 0th element is the width (in pixels) and the 1th element is the
        height (in pixels) as strings.

        :raises TimeoutException: If no options are currently displayed.
        """
        return self._available_options.get_computed_width(include_units=False), \
            self._available_options.get_computed_height(include_units=False)

    def expand_if_collapsed(self) -> None:
        """
        Expand the dropdown if it is collapsed. No action is taken if the dropdown is currently expanded.
        """
        if not self.is_expanded():
            self.toggle_expansion()

    def get_available_options(self) -> List[str]:
        """
        Expand the dropdown (if necessary), collect all displayed options, then collapse the dropdown before returning
        the displayed options as a list.

        :returns: A list where each item is an option displayed within the Dropdown when expanded.
        """
        needs_to_collapse = not self.is_expanded()
        self.expand_if_collapsed()
        try:
            options = [option.text for option in self._available_options.find_all(wait_timeout=0.5)]
        except TimeoutException:
            options = []
        if needs_to_collapse:
            self.collapse_if_expanded()
        return options

    def get_height_of_option_modal(self, include_units: bool = False) -> str:
        """
        Obtain the height of the modal which contains the options of the Dropdown. Requires that the Dropdown be
        expanded first.

        :param include_units: Dictates whether the returned value includes units of measurement.

        :returns: The height of the modal which contains the options of the Dropdown, as a string.

        :raises TimeoutException: If the modal is not present - most likely because the Dropdown was not expanded first.
        """
        return self._options_modal.get_computed_height(include_units=include_units)

    def get_origin_of_options_modal(self) -> Point:
        """
        Obtain the location of the upper-left corner of the modal which contains the options of the Dropdown. Requires
        that the Dropdown be expanded to display its options.

        :returns: A two-dimensional point which represents the location of the upper-left corner of the modal.

        :raises TimeoutException: If the modal is not present - most likely because the Dropdown was not expanded first.
        """
        return self._options_modal.get_origin()

    def get_selected_options_as_list(self) -> List[str]:
        """
        Obtain a list of all options which are displayed as currently selected by the Dropdown.

        :returns: A list, where each element of the list is an option currently selected within the Dropdown.
        """
        selected_labels = self.find().get_attribute("data-selected-labels")  # multi-select dropdowns
        if selected_labels is None:  # single-select handling
            return [self.find().get_attribute('data-label')]
        try:
            if selected_labels and "[" in selected_labels:
                selected_labels = json.loads(selected_labels)
            else:
                selected_labels = [json.loads(selected_labels)]
        except JSONDecodeError:
            return []
        return selected_labels

    def get_termination_of_options_modal(self) -> Point:
        """
        Obtain the location of the bottom-right corner of the modal which contains the options of the Dropdown. Requires
        that the Dropdown be expanded to display its options.

        :returns: A two-dimensional point which represents the location of the bottom-right corner of the modal.

        :raises TimeoutException: If the modal is not present - most likely because the Dropdown was not expanded first.
        """
        return self._options_modal.get_termination()

    def is_collapsed(self) -> bool:
        """
        Determine if the Dropdown is currently collapsed.

        :returns: True, if the Dropdown is currently collapsed.
        """
        try:
            return self.wait.until(IAec.function_returns_false(custom_function=self._is_expanded, function_args={}))
        except TimeoutException:
            return False

    def is_expanded(self) -> bool:
        """
        Determine if the Dropdown is currently expanded.

        :returns: True, if the Dropdown is currently expanded.
        """
        try:
            return self.wait.until(IAec.function_returns_true(custom_function=self._is_expanded, function_args={}))
        except TimeoutException:
            return False

    def option_is_disabled(self, option_text: str) -> bool:
        """
        Determine if an option of the Dropdown is currently disabled.

        :param option_text: The exact text of the option we will verify as being disabled.

        :returns: True, if the supplied option is currently disabled and therefore not available for selection.

        :raises TimeoutException: If the supplied option is not present.
        """
        self.expand_if_collapsed()
        option_disabled = self._DISABLED_CLASS in self._get_option(
            option_text=option_text).find().get_attribute("class")
        self.collapse_if_expanded()
        return option_disabled

    def option_is_visible_within_option_modal(self, option_text: str) -> bool:
        """
        Determine if an option is visible within the modal which displays options.

        :param option_text: The text of the option you wish to verify is contained within the modal.

        :returns: True, if the supplied option is present and is rendered within the boundaries of the modal - False if
            the option is not displayed at all, or if the option is rendering even partially outside the bounds of the
            modal - including options which must be scrolled to.
        """
        modal = ComponentModal(driver=self.driver)
        try:
            visible = self._get_option(option_text=option_text).find().is_displayed()
        except TimeoutException:  # option not even found
            return False
        if not visible:
            # don't bother checking anything else
            return False
        option_origin = self._get_option(option_text=option_text).get_origin()
        option_termination = self._get_option(option_text=option_text).get_termination()
        modal_origin = modal.get_origin()
        modal_termination = modal.get_termination()
        left_within_modal = option_origin.X >= modal_origin.X
        top_within_modal = option_origin.Y >= modal_origin.Y
        right_within_modal = option_termination.X <= modal_termination.X
        bottom_within_modal = option_termination.Y <= modal_termination.Y
        return visible and left_within_modal and top_within_modal and right_within_modal and bottom_within_modal

    def select_option_by_text_if_not_selected(self, option_text: str, binding_wait_time: float = 0.5) -> None:
        """
        Select an option from the Dropdown if it is not already selected. No action is taken if the supplied option is
        already selected.

        :param option_text: The exact text of the option to select.
        :param binding_wait_time: The amount of time (in seconds) to wait after selecting the option before allowing
            code to continue. Ignored if the option is already selected.

        :raises TimeoutException: If the specified option is not present.
        :raises AssertionError: If unsuccessful in selecting the specified option.
        """
        if option_text not in self.get_selected_options_as_list():
            self.scroll_to_element()
            self.expand_if_collapsed()
            try:
                self._get_option(option_text=option_text).click(wait_timeout=1, binding_wait_time=binding_wait_time)
            except TimeoutException as toe:
                raise TimeoutException(msg=f"Failed to locate element with text of \"{option_text}\".") from toe
        assert option_text in self.get_selected_options_as_list(), f"Failed to select option: '{option_text}'."

    def toggle_expansion(self) -> None:
        """
        Expands the Dropdown if it is collapsed, or collapses the dropdown if it is expanded.
        """
        self._expand_icon.click()

    def _is_expanded(self) -> bool:
        """
        Determine if the Dropdown is currently expanded (without waiting for the Dropdown to become expanded).

        :returns: True, if the Dropdown is currently expanded - False otherwise.
        """
        clazz = self.find().get_attribute("class")
        try:
            return (self.ACTIVE_CLASS in clazz) and (self._options_container.find(wait_timeout=0) is not None)
        except TimeoutException:
            return False

    def _get_option(self, option_text: str) -> ComponentPiece:
        """
        Obtain the ComponentPiece which defines an option within the modal.

        :param option_text: The exact text of the option.

        :returns: A ComponentPiece which defines the option of the Dropdown as it will be located within the modal
            during expansion.
        """
        option_element = self._option_elements.get(option_text)
        if not option_element:
            option_element = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'a[data-label="{option_text}"]'),
                driver=self.driver,
                parent_locator_list=self._options_container.locator_list,
                poll_freq=self.poll_freq)
            self._option_elements[option_text] = option_element
        return option_element
