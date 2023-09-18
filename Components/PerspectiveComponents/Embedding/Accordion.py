from typing import Tuple, Optional, List

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Components.PerspectiveComponents.Common.Icon import CommonIcon


class Accordion(BasicPerspectiveComponent):
    """A Perspective Accordion Component."""
    _GENERIC_ITEM_HEADER_LOCATOR = (By.CSS_SELECTOR, 'div.ia_accordionComponent__header')
    _ITEM_HEADER_ICON_LOCATOR = (By.CSS_SELECTOR, 'svg.ia_accordionComponent__header__chevron')
    _ITEM_HEADER_TEXT_LOCATOR = (By.CSS_SELECTOR, 'div.ia_accordionComponent__header__text')
    _ITEM_HEADER_VIEW_LOCATOR = (By.CSS_SELECTOR, 'div.ia_accordionComponent__header__view')
    _BODY_CONTENT_MARGIN_IN_PIXELS = 16
    _BODY_BORDER = 1  # Body has border on bottom only

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
        self._headers = ComponentPiece(
            locator=self._GENERIC_ITEM_HEADER_LOCATOR,
            driver=self.driver,
            parent_locator_list=self.locator_list)
        self._body_collection = {}
        self._header_collection = {}
        self._header_icon_collection = {}
        self._header_text_collection = {}

    def click_body(self, index: int) -> None:
        """
        Click the body of an Accordion panel.

        :param index: The zero-based index of the panel for which you would like to click the body.

        :raises TimeoutException: If the supplied index is invalid.
        :raises ClickInterceptedException: If the targeted body is not already expanded.
        """
        self._get_body_by_index(index=index).click()

    def click_header(self, index: int) -> None:
        """
        Click the header of an Accordion panel.

        :param index: The zero-based index of the header you would like to click.

        :raises TimeoutException: If the supplied index is invalid.
        """
        self._get_header_by_index(index=index).click()

    def click_header_icon(self, index: int) -> None:
        """
        Click the icon located in the header of an Accordion panel.

        :param index: The zero-based index of the header for which you would like to click the icon.

        :raises TimeoutException: If the supplied index is invalid.
        """
        self._get_header_icon_by_index(index=index).click()

    def click_header_text(self, index: int) -> None:
        """
        Click the text of an Accordion header.

        :param index: The zero-based index of the header for which you would like to click the text.

        :raises TimeoutException: If the supplied index is invalid.
        """
        self._get_header_text_component_by_index(index=index).click()

    def get_available_body_height(self, index: int) -> float:
        """
        Obtain the available height (in pixels) for an Accordion panel's body.

        :param index: The zero-based index of the panel for which you would like to obtain the available height for the
            body.

        :returns: The height (in pixels) which a panel's body has available for display.

        :raises TimeoutException: If the supplied index is invalid.
        """
        # there is no top border on body, so only subtract bottom border
        return (float(self.get_body_height(index=index))
                - (self._BODY_CONTENT_MARGIN_IN_PIXELS * 2)) - Accordion._BODY_BORDER

    def get_available_body_width(self, index: int) -> float:
        """
        Obtain the available width (in pixels) for an Accordion panel's body.

        :param index: The zero-based index of the panel for which you would like to obtain the available width for the
            body.

        :returns: The width (in pixels) which a panel's body has available for display.

        :raises TimeoutException: If the supplied index is invalid.
        """
        # there is no left/right border on body
        return self.get_body_width(index=index) - (self._BODY_CONTENT_MARGIN_IN_PIXELS * 2)

    def get_body_height(self, index: int) -> float:
        """
        Obtain the height (in pixels) of a body panel. Note this may not be the height of a rendered View.

        :param index: The zero-based index of the panel for which you would like to obtain the height for the body
            panel.

        :returns: The height (in pixels) of a body panel.

        :raises TimeoutException: If the supplied index is invalid.
        """
        return float(self._get_body_by_index(index=index).get_computed_height())

    def get_body_width(self, index: int):
        """
        Obtain the width (in pixels) of a body panel. Note this may not be the width of a rendered View.

        :param index: The zero-based index of the panel for which you would like to obtain the width for the body panel.

        :returns: The width (in pixels) of a body panel.

        :raises TimeoutException: If the supplied index is invalid.
        """
        return float(self._get_body_by_index(index=index).get_computed_width())

    def get_count_of_headers(self) -> int:
        """
        Obtain a count of headers.
        """
        return len(self._headers.find_all())

    def get_header_height(self, index: int) -> float:
        """
        Obtain the height of a header.

        :param index: The zero-based index of the header for which you would like the height.

        :returns: The height (in pixels) of the header.

        :raises TimeoutException: If the supplied index is invalid.
        """
        return float(self._get_header_by_index(index=index).get_computed_height())

    def get_header_icon_fill_color(self, index: int) -> str:
        """
        Obtain the fill in use by the icon of a header.

        :param index: The zero-based index of the header from which you would like to obtain the fill color for the
            contained icon.

        :returns: The fill color of the icon as a string. Note that this color might report as RGB or hex based on
            the browser in use.

        :raises TimeoutException: If the supplied index is invalid.
        """
        return self._get_header_icon_by_index(index=index).get_fill_color()

    def get_header_icon_name(self, index: int) -> str:
        """
        Obtain a slash-delimited path for the icon in use for the header.

        :param index: The zero-based index of the header from which you would like to obtain the path for the
            contained icon.

        :returns: The slash-delimited path of the icon.

        :raises TimeoutException: If the supplied index is invalid.
        """
        return self._get_header_icon_by_index(index=index).get_icon_name()

    def get_header_icon_height(self, index: int) -> float:
        """
        Obtain the height of the icon in use by a header.

        :param index: The zero-based index of the header from which you would like to obtain the height of the
            contained icon.

        :raises TimeoutException: If the supplied index is invalid.
        """
        return float(self._get_header_icon_by_index(index=index).get_computed_height())

    def get_header_icon_width(self, index: int) -> float:
        """
        Obtain the width of the icon in use by a header.

        :param index: The zero-based index of the header from which you would like to obtain the width of the
            contained icon.

        :raises TimeoutException: If the supplied index is invalid.
        """
        return float(self._get_header_icon_by_index(index=index).get_computed_width())

    def get_header_text(self, index: int) -> str:
        """
        Obtain the text contained within the header.

        :param index: The zero-based index of the header from which you would like the text.

        :raises TimeoutException: If the supplied index is invalid.
        """
        return self._get_header_text_component_by_index(index=index).get_text()

    def get_header_width(self, index: int) -> float:
        """
        Obtain the width of a header.

        :param index: The zero-based index of the header for which you would like the width.

        :returns: The width (in pixels) of the header.

        :raises TimeoutException: If the supplied index is invalid.
        """
        return float(self._get_header_by_index(index=index).get_computed_width())

    def header_is_enabled(self, index: int) -> bool:
        """
        Determine if a header is enabled.

        :param index: The zero-bsed index of the header for which you would like to determine the enabled state.

        :returns: True, if the header is enabled - False otherwise.

        :raises TimeoutException: If the supplied index is invalid.
        """
        return '--disabled' not in self._get_header_by_index(index=index).find().get_attribute('class')

    def header_is_in_reverse_render_mode(self, index: int) -> bool:
        """
        Determine if the header is configured to display in reverse.

        :param index: The zero-based index of the header to check for reversal.

        :returns: True, if the icon of the header is displaying to the right of the header content.

        :raises TimeoutException: If the supplied index is invalid.
        """
        icon_x = float(self._get_header_icon_by_index(index=index).get_origin().X)
        content_x = float(self._get_header_content_div(index=index).get_origin().X)
        return icon_x > content_x

    def header_is_in_text_render_mode(self, index: int):
        """
        Determine if the header is displaying only text.

        :param index: The zero-based index of the header to check.

        :returns: True, if the header is displaying in text mode. False, if the header is rendering as a View.
        """
        try:
            return self._get_header_text_component_by_index(index=index).find() is not None
        except TimeoutException:
            return False

    def item_is_expanded(self, index: int) -> bool:
        """
        Determine if an item of the accordion is expanded.

        :param index: The zero-based index of the item to check for expansion.

        :returns: True, if the item is expanded - False otherwise.

        :raises TimeoutException: If the supplied index is invalid.
        """
        return '--collapsed' not in self._get_body_by_index(index=index).find().get_attribute('class')

    def _get_body_by_index(self, index: int) -> ComponentPiece:
        """Obtain the body of an item."""
        body = self._body_collection.get(index)
        if not body:
            body = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'div.ia_accordionComponent__body[data-index="{index}"]'),
                driver=self.driver,
                parent_locator_list=self.locator_list)
            self._body_collection[index] = body
        return body

    def _get_header_by_index(self, index: int) -> ComponentPiece:
        """Obtain the header of an item."""
        header = self._header_collection.get(index)
        if not header:
            header = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'{self._GENERIC_ITEM_HEADER_LOCATOR[1]}[data-index="{index}"]'),
                driver=self.driver,
                parent_locator_list=self.locator_list)
            self._header_collection[index] = header
        return header

    def _get_header_content_div(self, index: int) -> ComponentPiece:
        """
        Obtain the content div located inside a header.
        """
        if self.header_is_in_text_render_mode(index=index):
            locator = self._ITEM_HEADER_TEXT_LOCATOR
        else:
            locator = self._ITEM_HEADER_VIEW_LOCATOR
        return ComponentPiece(
            locator=locator,
            driver=self.driver,
            parent_locator_list=self._headers.locator_list,
            poll_freq=self.poll_freq)

    def _get_header_icon_by_index(self, index: int) -> CommonIcon:
        """
        Obtain an icon from inside a header.
        """
        icon = self._header_icon_collection.get(index)
        if not icon:
            icon = CommonIcon(
                locator=self._ITEM_HEADER_ICON_LOCATOR,
                driver=self.driver,
                parent_locator_list=self._get_header_by_index(index=index).locator_list)
            self._header_icon_collection[index] = icon
        return icon

    def _get_header_text_component_by_index(self, index: int) -> ComponentPiece:
        """Obtain the text component from within a header."""
        header_text = self._header_text_collection.get(index)
        if not header_text:
            header_text = ComponentPiece(
                locator=self._ITEM_HEADER_TEXT_LOCATOR,
                driver=self.driver,
                parent_locator_list=self._get_header_by_index(index=index).locator_list,
                wait_timeout=2)
            self._header_text_collection[index] = header_text
        return header_text
