from typing import Optional, List, Tuple, Union
from Helpers.IAExpectedConditions import IAExpectedConditions as IAec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Components.PerspectiveComponents.Common.Icon import CommonIcon
from Helpers.CSSEnumerations import CSS, CSSPropertyValue


class Carousel(BasicPerspectiveComponent):
    """
    A Perspective Carousel Component.

    Note that many functions contained within this class are reliant on the presence of dots to determine the indices of
    active slides.
    """
    _ARROW_LOCATOR = (By.CSS_SELECTOR, "a.arrow")
    _DOT_LOCATOR = (By.CSS_SELECTOR, "a.dot")
    _ACTIVE_DOT_LOCATOR = (By.CSS_SELECTOR, f"{_DOT_LOCATOR[1]}.active")
    _VIEW_CONTAINER_LOCATOR = (By.CSS_SELECTOR, 'div.view-container:not(.leading-clone):not(.trailing-clone)')

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
        self._arrows = ComponentPiece(
            locator=self._ARROW_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._dot_coll = {}
        self._dot_icon_coll = {}
        self._dots = ComponentPiece(
            locator=self._DOT_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._active_dot = ComponentPiece(
            locator=self._ACTIVE_DOT_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)
        self._view_containers = ComponentPiece(
            locator=self._VIEW_CONTAINER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=poll_freq)

    def arrows_are_displayed(self) -> bool:
        """
        Determine if the Carousel is displaying arrows to the left and right of the slides.

        :returns: True, if arrows are displayed - False otherwise.
        """
        try:
            return self._arrows.find() is not None
        except TimeoutException:
            return False

    def click_dot_by_index(self, zero_based_index: int, wait_for_transition: bool = True) -> None:
        """
        Click a zero-indexed dot of the Carousel. The click is made regardless of active/inactive status.

        :param zero_based_index: The index of the dot to click.
        :param wait_for_transition: Dictates whether the code should wait for any animation to complete before
            continuing.

        :raises TimeoutException: If no dots are available to click or the supplied index is invalid.
        """
        current_index = self.get_current_index_from_dots()
        self._get_dot(
            zero_based_index=zero_based_index).click()
        if wait_for_transition:
            try:
                # We identify dots based on their active/inactive classes. By waiting for the inactive dot to disappear,
                # we are essentially waiting for the transition to have been completed and the active dot to have
                # appeared.
                self.wait.until(
                    ec.invisibility_of_element_located(
                        self._get_dot(
                            zero_based_index=current_index, must_be_active=False).get_full_css_locator()))
            except TimeoutException:
                pass

    def click_next_arrow(self, transition_speed: int = 1) -> None:
        """
        Click the 'next' arrow in order to transition to the next slide.

        :param transition_speed: The amount of time to wait while the Carousel goes through its transition. Synonymous
            with binding_wait_time.

        :raises TimeoutException: If no arrows are found.
        :raises IndexError: If only 1 arrow is found? Should never happen unless a user hides the next arrow through
            theming.
        """
        try:
            self.wait.until(IAec.function_returns_true(
                custom_function=self.next_arrow_is_enabled,
                function_args={}))
        except TimeoutException:
            pass
        # We have to perform a wait due to a FireFox issue not clicking the next arrow button.
        self.wait_on_binding(time_to_wait=0.25)
        self._arrows.find_all()[1].click()
        self._arrows.wait_on_binding(time_to_wait=transition_speed)

    def click_previous_arrow(self, transition_speed: int = 1) -> None:
        """
        Click the 'previous' arrow in order to transition to the previous slide.

        :param transition_speed: The amount of time to wait while the Carousel goes through its transition. Synonymous
            with binding_wait_time.

        :raises TimeoutException: If no arrows are found.
        :raises IndexError: If only 1 arrow is found? Should never happen unless a user hides the previous arrow through
            theming.
        """
        try:
            self.wait.until(IAec.function_returns_true(
                custom_function=self.previous_arrow_is_enabled,
                function_args={}))
        except TimeoutException:
            pass
        # We have to perform a wait due to a FireFox issue not clicking the previous arrow button.
        self.wait_on_binding(time_to_wait=0.25)
        self._arrows.find_all()[0].click()
        self._arrows.wait_on_binding(time_to_wait=transition_speed)

    def get_index_of_next_slide(self, current_index: Optional[int] = None) -> int:
        """
        Obtain the zero_based_index of the next slide. If current_index is supplied and is the last slide, or if
        current_index is not supplied and the Carousel is displaying the last slide, 0 will be returned.

        :param current_index: If None, we will return the next index based on the current display state of the Carousel.
            If not None, we will return the next index based on the provided index. This is most often used when
            dealing with what could potentially be the 'last' slide while attempting to determine if the 'next' slide
            would be the 'first' slide.

        :raises TimeoutException: If no dots are available from which to determine the indices.
        """
        if current_index is None:
            current_index = self.get_current_index_from_dots()
        current_index = int(current_index)
        slide_count = self.get_count_of_dots()
        if slide_count > 1:
            return (current_index + 1) % slide_count
        else:
            return current_index

    def determine_index_of_previous_slide(self, current_index: Optional[int] = None) -> int:
        """
        Obtain the zero_based_index of the previous slide. If current_index is supplied and is the first slide, or if
        current_index is not supplied and the Carousel is displaying the first slide, the index of the final slide will
        be returned.

        :param current_index: If None, we will return the previous index based on the current display state of the
            Carousel. If not None, we will return the previous index based on the provided index. This is most often
            used when dealing with what could potentially be the 'first' slide while attempting to determine if the
            'previous' slide would be the 'last' slide.

        :raises TimeoutException: If no dots are available from which to determine the indices.
        """
        if current_index is None:
            current_index = self.get_current_index_from_dots()
        current_index = int(current_index)
        slide_count = self.get_count_of_dots()
        if slide_count > 1:
            expected = current_index - 1
            return expected if expected >= 0 else slide_count - 1
        else:
            return current_index

    def dots_are_present(self) -> bool:
        """
        Determine if the Carousel is currently displaying the dots which convey which slide is active.

        :returns: True, if any dots are displayed - False otherwise.
        """
        try:
            return self._dots.find() is not None
        except TimeoutException:
            return False

    def fade_is_enabled(self) -> bool:
        """
        Determine if the Carousel is currently configured to fade during transitions.

        :returns: True, if the Carousel would fade in and out during slide transitions - False otherwise.
        """
        return 'opacity' == self.get_css_property(property_name=CSS.TRANSITION)

    def get_current_slide_display_area_height(self, include_units: bool = False) -> str:
        """
        Obtain the current height available for slides to display in.
        """
        return self._view_containers.get_computed_height(include_units=include_units)

    def get_current_slide_display_area_width(self, include_units: bool = False) -> str:
        """
        Obtain the current width available for slides to display in.
        """
        return self._view_containers.get_computed_width(include_units=include_units)

    def get_current_slide_css_property(self, property_name: Union[CSSPropertyValue, str]) -> str:
        """
        Obtain the value of some CSS property of the container of the current slide. Note that this is not a property
        of the rendered View.

        :param property_name: The name of the CSS property for which you would like the value.
        """
        return self._view_containers.get_css_property(property_name=property_name)

    def get_count_of_dots(self) -> int:
        """
        Obtain the count of rendered dots of the Carousel.
        """
        try:
            return len(self._dots.find_all(wait_timeout=0))
        except TimeoutException:
            return 0

    def get_count_of_slides(self) -> int:
        """
        Obtain the count of slides within the Carousel. This is not a count of how many slides are currently displayed.
        """
        return len(self._view_containers.find_all())

    def get_current_index_from_dots(self) -> int:
        """
        Obtain the index of the currently displayed slide from the dots of the Carousel.
        """
        return int(self._active_dot.find().get_attribute("data-index"))

    def get_dot_icon_css_property_by_name(
            self, zero_based_index: int, property_name: Union[CSSPropertyValue, str]) -> str:
        """
        Obtain a CSS property value from the icon of a Carousel dot.

        :param zero_based_index: The index of the dot from which you would like the CSS property value.
        :param property_name: The name of the CSS property of which you would like the value.

        :raises TimeoutException: If no dots are found, or if the provided index is not valid.
        """
        return self._get_dot_icon(
            zero_based_index=zero_based_index).get_css_property(property_name=property_name)

    def get_dot_icon_path(self, zero_based_index: int) -> str:
        """
        Obtain a slash-delimited path for the icon in use by a Carousel dot.

        :raises TimeoutException: If no dots are found, or if the provided index is not valid.
        """
        return self._get_dot_icon(
            zero_based_index=zero_based_index).get_icon_name()

    def next_arrow_is_enabled(self) -> bool:
        """
        Determine if the 'next' arrow is currently enabled.

        :returns: True, if the 'next' arrow is enabled - False otherwise.

        :raises TimeoutException: If no arrows are found.
        :raises IndexError: If only 1 arrow is found? Should never happen unless a user hides the next arrow through
            theming.
        """
        return "disabled" not in self._arrows.find_all()[1].get_attribute("class")

    def pause_by_hovering(self, binding_wait_time: float = 1) -> None:
        """
        Attempt to pause the Carousel by hovering the mouse over the Component. Note that this function only has any
        effect if the Carousel is configured to pause while a user hovers over it.

        :param binding_wait_time: How long (in seconds) to wait after hovering over the component before allowing code
            to continue.
        """
        self.hover()
        self.wait_on_binding(time_to_wait=binding_wait_time)

    def pause_by_hovering_on_dots(self, binding_wait_time: float = 1) -> None:
        """
        Attempt to pause the Carousel by hovering the mouse over the dots of the Carousel. Note that this function only
        has any effect if the Carousel is configured to pause while a user hovers over the dots of the Carousel.

        :param binding_wait_time: How long (in seconds) to wait after hovering over the component before allowing code
            to continue.
        """
        self._dots.hover()
        self._dots.wait_on_binding(time_to_wait=binding_wait_time)

    def previous_arrow_is_enabled(self) -> bool:
        """
        Determine if the 'previous' arrow of the Carousel is currently enabled.

        :returns: True, if the 'previous' arrow is currently enabled - False otherwise.

        :raises TimeoutException: If no arrows are found.
        :raises IndexError: If only 1 arrow is found? Should never happen unless a user hides the previous arrow through
            theming.
        """
        return "disabled" not in self._arrows.find_all()[0].get_attribute("class")

    def wait_for_next_slide(self, original_index: int, time_to_wait: float = 10) -> int:
        """
        Wait for the Carousel to transition to the next slide.

        :param original_index: The zero-based index you are waiting for the Carousel to transition away from.
        :param time_to_wait: The amount of time (in seconds) you are willing to wait for the Carousel to arrive at the
            next index after original_index.

        :returns: The index the Carousel is currently rendering after having waited for the transition from the
            original_index.

        :raises TimeoutException: If no dots are found.
        """
        try:
            self._get_dot(
                zero_based_index=self.get_index_of_next_slide(
                    current_index=original_index), must_be_active=True).find(wait_timeout=time_to_wait)
        except TimeoutException:
            pass
        return self.get_current_index_from_dots()

    def wait_for_previous_slide(self, original_index: int, time_to_wait: float = 10) -> int:
        """
        Wait for the Carousel to transition to the previous slide.

        :param original_index: The zero-based index you are waiting for the Carousel to transition away from.
        :param time_to_wait: The amount of time (in seconds) you are willing to wait for the Carousel to arrive at the
            previous index from original_index.

        :returns: The index the Carousel is currently rendering after having waited for the transition from the
            original_index.

        :raises TimeoutException: If no dots are found.
        """
        try:
            self._get_dot(
                zero_based_index=self.determine_index_of_previous_slide(
                    current_index=original_index), must_be_active=True).find(wait_timeout=time_to_wait)
        except TimeoutException:
            pass
        return self.get_current_index_from_dots()

    def _get_dot(self, zero_based_index: int, must_be_active: bool = False) -> ComponentPiece:
        """
        Obtain a ComponentPiece which describes a dot of the Carousel.

        :param zero_based_index: The index of the Carousel dot.
        :param must_be_active: Dictates whether the described dot is an active or inactive dot.
        """
        dot = self._dot_coll.get((zero_based_index, must_be_active))
        if not dot:
            locator = self._ACTIVE_DOT_LOCATOR[1] if must_be_active else self._DOT_LOCATOR[1]
            dot = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'{locator}[data-index="{zero_based_index}"]'),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                wait_timeout=1,
                poll_freq=self.poll_freq)
            self._dot_coll[(zero_based_index, must_be_active)] = dot
        return dot

    def _get_dot_icon(self, zero_based_index: int) -> CommonIcon:
        """
        Obtain a CommonIcon contained within a Carousel dot.

        :param zero_based_index: The index of the Carousel dot this icon lives in.
        """
        icon = self._dot_icon_coll.get(zero_based_index)
        if not icon:
            icon = CommonIcon(
                locator=(By.CSS_SELECTOR, "svg"),
                driver=self.driver,
                parent_locator_list=self._get_dot(
                    zero_based_index=zero_based_index).locator_list,
                wait_timeout=1,
                poll_freq=self.poll_freq)
            self._dot_icon_coll[zero_based_index] = icon
        return icon
