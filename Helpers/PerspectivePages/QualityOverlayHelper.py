from typing import List

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece
from Helpers.IAAssert import IAAssert
from Helpers.PerspectivePages.Quality import PerspectiveQuality


class QualityOverlayHelper:
    """
    An assistant for examining Quality Overlays and interacting with any popovers. As popover elements do not
    actually refer to their originating component, there is a chance that an open popover might not "belong" to a
    component under test, and so it is the responsibility of the test to verify no other popovers are open before
    opening a popover for a given component.

    Important terminology:

    overlay: The encompassing border of a Perspective component which denotes a non-good Quality.
    popover: The available informational window opened by clicking the icon within the overlay.
    """
    _QUALITY_FORCED_OVERLAY_PREFIX = 'cqfo'
    _MICRO_CONTAINER_LOCATOR = (By.CSS_SELECTOR, 'div.micro-icon-container')
    _BACK_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'div.popover-back-button')
    _NEXT_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'div.popover-next-button')
    _CARD_COUNT_LOCATOR = (By.CSS_SELECTOR, 'div.popover-card-count')
    _POPOVER_LOCATOR = (By.CSS_SELECTOR, 'div.component-popover')
    _POPOVER_ICON_LOCATOR = (By.CSS_SELECTOR, 'div.popover-icon')
    _BODY_SECTION_LOCATOR = (By.CSS_SELECTOR, 'div.popover-body-section')
    _BODY_DESCRIPTOR_LOCATOR = (By.CSS_SELECTOR, 'h6.body-descriptor')
    _BODY_CONTENT_LOCATOR = (By.CSS_SELECTOR, 'div.body-content')

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self._popover = ComponentPiece(
            locator=self._POPOVER_LOCATOR, driver=driver, parent_locator_list=None, wait_timeout=0)
        self._popover_icon = ComponentPiece(
            locator=self._POPOVER_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self._popover.locator_list,
            wait_timeout=0,
            description="The icon in the upper-right of the popover which allows for direct dismissal.")
        self._popover_back_button = ComponentPiece(
            locator=self._BACK_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self._popover.locator_list,
            wait_timeout=0,
            description="The '<' button/chevron in the bottom of the popover, available only when a component has "
                        "multiple faulted bindings.")
        self._popover_next_button = ComponentPiece(
            locator=self._NEXT_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self._popover.locator_list,
            wait_timeout=0,
            description="The '>' button/chevron in the bottom of the popover, available only when a component has "
                        "multiple faulted bindings.")
        self._card_count = ComponentPiece(
            locator=self._CARD_COUNT_LOCATOR,
            driver=driver,
            parent_locator_list=self._popover.locator_list,
            wait_timeout=0,
            description="The piece of popover UI which describes how many faulted bindings a component has.")
        self._body_section = ComponentPiece(
            locator=self._BODY_SECTION_LOCATOR,
            driver=driver,
            parent_locator_list=self._popover.locator_list,
            wait_timeout=0,
            description="The area between the header and footer of the popover.")
        self._body_descriptor = ComponentPiece(
            locator=self._BODY_DESCRIPTOR_LOCATOR,
            driver=driver,
            parent_locator_list=self._body_section.locator_list,
            wait_timeout=0,
            description="The label which SHOULD read as 'Subcode'.")
        self._body_content = ComponentPiece(
            locator=self._BODY_CONTENT_LOCATOR,
            driver=driver,
            parent_locator_list=self._body_section.locator_list,
            wait_timeout=0,
            description="The string designation of the subcode conveyed by a popover.")

    def any_popover_is_displayed(self) -> bool:
        """
        Determine if any popover is currently displayed.

        :returns: True, if any Quality popover is currently displayed - False otherwise.
        """
        try:
            return self._popover.find() is not None
        except TimeoutException:
            return False

    def click_back_in_popover_footer(self) -> None:
        """
        Click the '<' button/chevron in the footer of the Quality popover.
        """
        self.hover_over_icon_in_popover_header()
        self._popover_back_button.click()

    def click_next_in_popover_footer(self) -> None:
        """
        Click the '>' button/chevron in the footer of the Quality popover.
        """
        self.hover_over_icon_in_popover_header()
        self._popover_next_button.click()

    def close_all_popovers(self) -> None:
        """
        Close all Quality popovers currently open in the page.

        :raises AssertionError: If unsuccessful in closing all open Quality popovers.
        """
        elements = self.driver.find_elements(By.CSS_SELECTOR, 'svg.quality-icon')
        for element in reversed(elements):
            element.click()
        IAAssert.is_equal_to(
            actual_value=self.get_count_of_all_popovers(),
            expected_value=0,
            failure_msg="Failed to close all Quality Overlay popovers.")

    def get_count_of_all_popovers(self) -> int:
        """
        Obtain a count of all Quality popovers which are currently open in the page.

        :returns: A count of Quality popovers currently displayed to the user.
        """
        try:
            return len(self._popover.find_all())
        except TimeoutException:
            # might not be necessary
            return 0

    def get_count_of_overlays(self, quality: PerspectiveQuality) -> int:
        """
        Obtain a count of Quality overlays currently displayed to the user which convey the specified quality type.

        :returns: A count of Quality overlays currently displayed with the specified quality.
        """
        return len(self.driver.find_elements(
            By.CSS_SELECTOR, f'div.{self._QUALITY_FORCED_OVERLAY_PREFIX}-{quality.value}'))

    def get_count_of_all_overlays(self) -> int:
        """
        Obtain a count of all Quality overlays - regardless of quality.

        :returns: A count of all Quality overlays - regardless of their quality.
        """
        return self.get_count_of_overlays(quality=PerspectiveQuality.ERROR) \
            + self.get_count_of_overlays(quality=PerspectiveQuality.UNKNOWN) \
            + self.get_count_of_overlays(quality=PerspectiveQuality.PENDING)

    def get_count_of_quality_concerns_from_popover(self) -> int:
        """
        Obtain a count of Quality concerns from the first found Quality popover. Any value larger than 1 suggests
        that the component has multiple faulted bindings.

        :returns: A count of faulted bindings conveyed within the first Quality popover.
        """
        try:
            return int(self._card_count.get_text().split('/')[-1])
        except TimeoutException:
            try:
                return 1 if self._popover.find() is not None else 0
                # popover open, but no footer/count present
            except TimeoutException as toe:
                raise TimeoutException(
                    msg="Unable to discern a count of quality concerns from the popover as no popover "
                        "was displayed.") from toe

    def get_list_of_ids_with_overlays(self) -> List[str]:
        """
        Obtain a list of the HTML id attributes of any elements which have any overlay present. If the HTML element
        does not have an id, the element will not be represented in the list.

        :returns: A list of strings which are the HTML ids of any elements which have any type of overlay If those
            components have an id attribute.
        """
        id_list = []
        for el in self.driver.find_elements(By.CSS_SELECTOR, f"div.{self._QUALITY_FORCED_OVERLAY_PREFIX}"):
            potential_id = el.get_attribute('id')
            if (potential_id is not None) and (len(potential_id) > 0):
                id_list.append(potential_id)
        return id_list

    def hover_over_icon_in_popover_header(self) -> None:
        """
        Popovers do not declare what component they belong to, so if you are seeing information
        which seems incorrect, make sure only one popover is open and that it was triggered by
        the expected component.
        """
        self._popover_icon.hover()

    def get_sub_code_text_from_open_popover(self) -> str:
        """
        Obtain the subcode text from the first open popover. In the event a component has multiple faulted bindings,
        error subcodes take priority over uncertain (unknown) subcodes, which take priority over good subcodes.

        :returns: The string designation of the subcode which describes the quality of the most severe faulted binding.

        :raises AssertionError: If an unexpected popover structure is encountered.
        """
        IAAssert.is_equal_to(
            actual_value=self._body_descriptor.get_text(),
            expected_value='Subcode',
            failure_msg="The popover has an unexpected structure; we expected to find a subcode, but we found "
                        "something else")
        return self._body_content.get_text()
