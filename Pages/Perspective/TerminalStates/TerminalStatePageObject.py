from typing import Union

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec

from Components.BasicComponent import BasicComponent, ComponentPiece
from Helpers.CSSEnumerations import CSS, CSSPropertyValue
from Pages.PagePiece import PagePiece


class TerminalStatePageObject(PagePiece):
    """
    The over-arching ancestor of all Terminal State Pages.
    """
    _HEADER_LOCATOR = (By.CSS_SELECTOR, 'h1.terminal-state-header')
    _MESSAGE_LOCATOR = (By.CSS_SELECTOR, 'section.terminal-state-section p')
    _LAUNCH_GATEWAY_ANCHOR_LOCATOR = (By.CSS_SELECTOR, 'a.terminal-state-link')

    def __init__(
            self,
            driver: WebDriver,
            expected_page_header_text: str):
        PagePiece.__init__(
            self,
            driver=driver,
            primary_locator=self._HEADER_LOCATOR)
        self._expected_page_header_text = expected_page_header_text
        self._main_body = ComponentPiece(
            locator=(By.CSS_SELECTOR, "div.terminal-state-page"),
            driver=driver)
        self._launch_gateway_button = BasicComponent(
            locator=self._LAUNCH_GATEWAY_ANCHOR_LOCATOR,
            driver=driver)

    def click_launch_gateway(self) -> None:
        """
        Click the Launch Gateway button.
        """
        self._launch_gateway_button.click()

    def get_background(self) -> str:
        """
        Obtain the background in use for this Terminal State Page.

        :return: While using Branding Customization, this returns a hex color (as a string) - otherwise a path to the
            gradient image.
        """
        return self._main_body.get_css_property(property_name=CSS.BACKGROUND_COLOR)

    def get_launch_gateway_css_property(self, property_name: Union[CSSPropertyValue, str]) -> str:
        """
        Obtain some CSS property of the Launch Gateway button.

        :param property_name: The name of the CSS property you would like the value of.

        :return: The value of the specified CSS property as applied to the Launch Gateway button.
        """
        return self._launch_gateway_button.get_css_property(property_name=property_name)

    def get_message(self) -> str:
        """
        Obtain the message displayed for this Terminal State Page.

        :return: The message displayed by this Terminal State Page.
        """
        return self.wait.until(
            method=ec.presence_of_element_located(self._MESSAGE_LOCATOR),
            message="No message found on Terminal State page.").text

    def get_header_text(self) -> str:
        """
        Obtain the header text displayed for this Terminal State Page.

        :return: The header text displayed by this Terminal State Page.
        """
        return self.wait.until(
            method=ec.presence_of_element_located(self._HEADER_LOCATOR),
            message="No header found on Terminal State page.").text.strip()

    def get_launch_gateway_button_text(self) -> str:
        """
        Obtain the text of the Launch Gateway button.

        :return: The text of the Launch Gateway button.
        """
        return self._launch_gateway_button.find().text.strip()

    def get_text_color(self) -> str:
        """
        Obtain the color in use for the text of the body of this Terminal State Page.

        :return: The color in use for the text of the body of this Terminal State Page.
        """
        return self._main_body.get_css_property(property_name=CSS.COLOR)

    def launch_gateway_button_is_present(self) -> bool:
        """
        Determine if this page contains a Launch Gateway button.

        :return: True, if the Launch Gateway button is present - False otherwise.
        """
        try:
            return self.driver.find_element(*self._LAUNCH_GATEWAY_ANCHOR_LOCATOR) is not None
        except NoSuchElementException:
            return False

    def wait_for_terminal_state_page(self) -> None:
        """
        Wait for the Terminal State Page to load, but allow code to continue in the event the page does not load.
        """
        try:
            self.wait.until(
                method=ec.presence_of_element_located(
                    self._HEADER_LOCATOR),
                message="The header was not found on the Terminal State page - the page may not have loaded")
        except TimeoutException:
            pass

    def is_current_page(self) -> bool:
        """
        Determine if this Terminal State Page is the currently displayed page.

        :return: True, if the header text of this page is what we would expect to find - False otherwise.
        """
        try:
            return self.driver.find_element(*self.primary_locator).text == self._expected_page_header_text
        except NoSuchElementException:
            return False
