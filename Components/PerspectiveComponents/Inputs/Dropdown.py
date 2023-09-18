import json
from json import JSONDecodeError
from typing import List, Optional, Union, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece, BasicPerspectiveComponent
from Components.PerspectiveComponents.Common.Dropdown import CommonDropdown
from Helpers.CSSEnumerations import CSSPropertyValue
from Helpers.IAExpectedConditions import IAExpectedConditions as IAec
from Helpers.Point import Point


class Dropdown(CommonDropdown, BasicPerspectiveComponent):
    _ALL_ACTIVE_DROPDOWNS_LOCATOR = (By.CSS_SELECTOR, f"div.{CommonDropdown.ACTIVE_CLASS}")
    _PILL_CLASS = 'ia_dropdown__valuePill'
    _VALUE_PILL_LOCATOR = (By.CSS_SELECTOR, 'div.ia_dropdown__valuePill__value')
    _FOCUSED_OPTION_CLASS = 'ia_dropdown__option--focused'
    _PLACEHOLDER_LOCATOR = (By.CSS_SELECTOR, 'div.iaDropdownCommon_placeholder-container div')
    _CLEAR_ALL_OPTIONS_SVG_LOCATOR = (By.CSS_SELECTOR, 'a.iaDropdownCommon_clear_value')
    _VALUE_CONTAINER_LOCATOR = (By.CSS_SELECTOR, "div.iaDropdownCommon_value-container")
    _SEARCH_INPUT_LOCATOR = (By.CSS_SELECTOR, 'input.iaDropdownCommon_search')
    _SELECTED_OPTION_LOCATOR = (By.CSS_SELECTOR, '> div')
    _COMMON_CONTAINER_LOCATOR = (By.CSS_SELECTOR, 'div.iaDropdownCommon_container')
    _NO_RESULTS_MODAL_LOCATOR = (By.CSS_SELECTOR, 'a.iaDropdownCommon_option.ia_dropdown__option__noResults')

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 4,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        CommonDropdown.__init__(
            self,
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            poll_freq=poll_freq)
        BasicPerspectiveComponent.__init__(
            self,
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,  # only needs to be done once
            poll_freq=poll_freq
        )
        self._placeholder = ComponentPiece(
            locator=self._PLACEHOLDER_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._clear_all_options = ComponentPiece(
            locator=self._CLEAR_ALL_OPTIONS_SVG_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._displayed_selected_options = {}
        self._search_input = ComponentPiece(
            locator=self._SEARCH_INPUT_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._value_container = ComponentPiece(
            locator=self._VALUE_CONTAINER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._selected_options = ComponentPiece(
            locator=self._SELECTED_OPTION_LOCATOR,
            driver=driver,
            parent_locator_list=self._value_container.locator_list,
            poll_freq=poll_freq)
        self._all_active_dropdowns = ComponentPiece(
            locator=self._ALL_ACTIVE_DROPDOWNS_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            poll_freq=poll_freq)
        self._common_container = ComponentPiece(
            locator=self._COMMON_CONTAINER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._value_pill = ComponentPiece(
            locator=self._VALUE_PILL_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._no_results_modal = ComponentPiece(
            locator=self._NO_RESULTS_MODAL_LOCATOR,
            driver=driver,
            parent_locator_list=self._options_container.locator_list,
            poll_freq=poll_freq)

    def clear_all_selections(self) -> None:
        """
        Click the 'X' which would remove all selected options.

        :raises TimeoutException: If the clear all selected options 'X' is not present.
        """
        self._clear_all_options.click(wait_timeout=1)

    def clear_selected_option(self, option_text: str) -> None:
        """
        Clear an individual selected option. Available only for multi-select dropdowns.

        :raises TimeoutException: if not using a multi-select Dropdown component, or if no option with matching text
            is currently selected.
        """
        option_clear_link = self._displayed_selected_options.get(option_text)
        if not option_clear_link:
            option_clear_link = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'div[data-label="{option_text}"] a'),
                driver=self.driver,
                parent_locator_list=self._value_container.locator_list,
                poll_freq=self.poll_freq)
            self._displayed_selected_options[option_text] = option_clear_link
        option_clear_link.click()

    def collapse_if_expanded(self) -> None:
        """
        Collapse the Dropdown if it is currently active. Does NOT remove focus from the Dropdown.
        """
        if self.is_expanded():
            self.toggle_expansion()

    def get_common_container_css_property(self, property_name: Union[CSSPropertyValue, str]) -> str:
        """Obtain a CSS property value from the main container of the Dropdown."""
        return self._common_container.get_css_property(property_name=property_name)

    def get_count_of_active_dropdowns(self) -> int:
        """Obtain a count of how many Dropdowns are currently displaying options for selection."""
        try:
            return len(self._all_active_dropdowns.find_all(wait_timeout=1))
        except TimeoutException:
            return 0

    def get_count_of_displayed_options(self) -> int:
        """
        Obtain a count of how many options are currently displayed for selection.

        :returns: A count of options currently available for selection. This includes options which must be scrolled to.
        """
        try:
            return len(self._available_options.find_all())
        except TimeoutException:
            return 0

    def get_displayed_text(self) -> str:
        """
        Obtain the displayed text of the Dropdown.

        :returns: All text of the Dropdown - including all selected options - as a single string.
        """
        return self._value_container.get_text()

    def get_options_modal_css_property(self, property_name: Union[CSSPropertyValue, str]) -> str:
        """
        Obtain a CSS property value of the options modal.

        :returns: a specific CSS property value of the options modal, distinct from the main Dropdown container.
        """
        try:
            self.expand_if_collapsed()
            return self._available_options.get_css_property(property_name=property_name)
        finally:
            self.collapse_if_expanded()

    def get_no_results_modal_css_property(self, property_name: Union[CSSPropertyValue, str]) -> str:
        """
        Obtain a CSS property value of the 'No Results' modal.

        :returns: a specific CSS property value of the options modal, distinct from the main Dropdown container.

        :raises TimeoutException: If the 'No Results' modal is not displayed.
        """
        try:
            self.expand_if_collapsed()
            return self._no_results_modal.get_css_property(property_name=property_name)
        finally:
            self.collapse_if_expanded()

    def get_origin_of_search_input(self) -> Point:
        """
        Obtain the origin of the search input within the Dropdown.

        :raises TimeoutException: If the Dropdown does not allow for searching of options.
        """
        return self._search_input.get_origin()

    def get_origin_of_value_pills(self) -> List[Point]:
        """
        Obtain the origins of all option value pills currently displayed for the multi-select Dropdown.

        :raises TimeoutException: If no options are currently selected, or if using a single-select Dropdown.
        """
        return [Point(x=vp.rect["x"], y=vp.rect["y"]) for vp in self._value_pill.find_all()]

    def get_origins_of_selected_options(self) -> List[Point]:
        """
        Obtain the origins of all selected option wrapper <div> elements. Distinct from the value 'pills'. This function
        works for all Dropdowns.

        :raises TimeoutException: If no options are selected.
        """
        return [
            Point(x=option_elem.rect["x"], y=option_elem.rect["y"])
            for option_elem in self._selected_options.find_all()
        ]

    def get_placeholder_text(self) -> str:
        """
        Obtain the placeholder text currently displayed in the Dropdown.

        :raises TimeoutException: If no placeholder text is displayed.
        """
        return self._placeholder.get_text()

    def get_search_input_css_property(self, property_name: Union[CSSPropertyValue, str]) -> str:
        """
        Obtain a CSS property value of the search <input> element. This element is only present while the Dropdown is
        active.

        :returns: a specific CSS property value of the search input.

        :raises TimeoutException: If the search input is not present.
        """
        return self._search_input.get_css_property(property_name=property_name)

    def get_selected_options_as_list(self) -> List[str]:
        """
        Obtain all selected options as a list of strings.

        :returns: A list, where each item is the text of an option which is currently selected.
        """
        selected_labels = self.find().get_attribute("data-selected-labels")
        try:
            if selected_labels and "[" in selected_labels:
                selected_labels = json.loads(selected_labels)
            elif selected_labels == '""':
                selected_labels = []
            else:
                selected_labels = [json.loads(selected_labels)]
        except JSONDecodeError:
            return []
        return selected_labels

    def get_width_and_height_of_first_available_option(self) -> Tuple[str, str]:
        """
        Obtain the width and height of the first available option in the options modal as a Tuple where the first
        element is the width, and the second element is the height.

        :returns: A tuple, where the 0th element is the width of the first available option of the Dropdown, and the 1th
            element is the height.
        """
        try:
            self.expand_if_collapsed()
            return self._available_options.get_computed_width(include_units=False), \
                self._available_options.get_computed_height(include_units=False)
        finally:
            self.collapse_if_expanded()

    def insert_custom_option(self, custom_option_text: str) -> None:
        """
        Insert a custom option into the Dropdown.

        :param custom_option_text: The text of the option you would like to supply. This will also be used as the value
            of the option.

        :raises TimeoutException: If the Dropdown does not allow for custom options.
        """
        try:
            self.expand_if_collapsed()
            self._search_input.find().send_keys(custom_option_text)
            # The "create" option actually has a data-label attribute of "Create", regardless of the option text
            self._get_option(option_text=f"Create: {custom_option_text}").click()
        finally:
            self.collapse_if_expanded()

    def option_has_focus(self, option_text: str) -> bool:
        """
        Determine if the supplied option currently has focus.

        :param option_text: The text of the option to check.

        :returns: True, if the option has focus, False otherwise.
        """
        try:
            return self.wait.until(
                IAec.function_returns_true(
                    custom_function=self._option_has_focus,
                    function_args={"option_text": option_text}))
        except TimeoutException:
            return False

    def placeholder_text_is_displayed(self) -> bool:
        """Determine if placeholder text is currently displayed."""
        try:
            return len(self._placeholder.find(wait_timeout=1).text) > 0
        except TimeoutException:
            return False

    def select_option_by_text_if_not_selected(self, option_text: str, binding_wait_time: float = 0.5) -> None:
        """
        Select an option. If the option is already selected, no action is taken.

        Full Perspective Dropdowns often have many options and need assistance limiting the displayed list,
        so this function will attempt to filter the displayed options if the desired option is not readily seen.

        :param option_text: The text of the option you would like to select.
        :param binding_wait_time: The amount of time to wait after selecting an option before allowing the code to
            continue.

        :raises TimeoutException: If no option with the supplied text exists as an option.
        """
        if option_text not in self.get_selected_options_as_list():
            self.scroll_to_element()
            self.expand_if_collapsed()
            if not self.option_is_visible_within_option_modal(option_text=option_text):
                # Selenium occasionally has issues when scrolling the options modal, so attempt to filter the displayed
                # options first
                try:
                    self.set_search_text(search_text=option_text)
                except TimeoutException:
                    # filtering the displayed options didn't work, so our only option is to scroll and hope it works
                    self._get_option(option_text=option_text).scroll_to_element()
            try:
                self._get_option(option_text=option_text).click(wait_timeout=1, binding_wait_time=binding_wait_time)
            except TimeoutException as toe:
                toe.msg = f"Failed to locate element with text of \"{option_text}\"."
                raise toe
            finally:
                self.collapse_if_expanded()

    def selected_options_are_in_pills(self) -> bool:
        """
        Determine if the selected options are in 'pills'. This concept is unique to multi-select Dropdowns.

        :raises TimeoutException: If no options are currently selected.
        """
        # CommonDropdown does not allow for multi-selection, so no pills
        return self._PILL_CLASS in self._selected_options.find().get_attribute("class").split(" ")

    def set_search_text(self, search_text: str) -> None:
        """
        Set the search text of the Dropdown.

        :param search_text: The text to supply to the Dropdown in an attempt to filter the displayed options.

        :raises TimeoutException: If the Dropdown does not allow for searching.
        """
        # Searching not allowed in CommonDropdown
        self.click(binding_wait_time=0.5)
        self._search_input.find().send_keys(search_text)

    def _option_has_focus(self, option_text: str) -> bool:
        """
        Determine if an option in the options modal has focus.

        :param option_text: The text of the option to check.

        :raises TimeoutException: If no options are currently displayed, or no option with the supplied text exists.
        """
        return self._FOCUSED_OPTION_CLASS in self._get_option(
            option_text=option_text).find(wait_timeout=0).get_attribute("class")
