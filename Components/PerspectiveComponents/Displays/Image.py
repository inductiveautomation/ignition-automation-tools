from typing import Optional, List, Tuple, Union

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Helpers.CSSEnumerations import CSS, CSSPropertyValue


class Image(BasicPerspectiveComponent):
    """A Perspective Image Component."""
    _INTERNAL_IMAGE_LOCATOR = (By.TAG_NAME, "img")

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 5,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._internal_img = ComponentPiece(
            locator=self._INTERNAL_IMAGE_LOCATOR,
            parent_locator_list=self.locator_list,
            driver=driver,
            poll_freq=poll_freq)

    def get_source(self) -> str:
        """
        Obtain the source (src) in use by the Image Component. This function works unless the component has no applied
        source. In that instance, Chrome and Firefox will return a blank String, whereas only Edge of all browsers will
        return the correct expected value, which is the url of the current page.

        :returns: The source (src) of the <img> element.
        """
        return self._internal_img.find().get_attribute('src')

    def get_alt_text(self) -> str:
        """
        Obtain the Alt Text (alt) in use by the Image Component. This function will return an empty string ("") if no
        alt text is configured to the Image component.

        :returns: The Alt Text (alt HTML attribute) of the <img> element.
        """
        return self._internal_img.find().get_attribute('alt')

    def get_css_property_value_of_internal_image(self, css_property: Union[CSSPropertyValue, str]) -> str:
        """
        Obtain the value of the specified CSS property for the internal image reference.

        :param css_property: Supply the name of the CSS property that will be obtained.

        :returns: The style property value of the <img> element.
        """
        return self._internal_img.get_css_property(property_name=css_property)

    def get_height_of_internal_image(self, include_units: bool = False) -> str:
        """
        Obtain the height value of the internal image (<img> element).

        :param include_units: If set to True, the units of the height value will be supplied to the value. Otherwise,
            only the numeric value will be given.

        :returns: The height value of the internal image (<img> element).
        """
        return self._internal_img.get_computed_height(include_units=include_units)

    def get_width_of_internal_image(self, include_units: bool = False) -> str:
        """
        Obtain the width value of the internal image (<img> element).

        :param include_units: If set to True, the units of the width value will be supplied to the value. Otherwise,
            only the numeric value will be given.

        :returns: The width value of the internal image (<img> element).
        """
        return self._internal_img.get_computed_width(include_units=include_units)

    def is_scroll_enabled(self) -> bool:
        """
        Obtain the value of the scroll property in the Image component. The Image component's overflow value
        determines if scroll is enabled or not. When overflow is set to auto, scrolling is enabled. Otherwise, the
        value of overflow is set to hidden.

        :returns: A value of True when overflow is set to "auto"; False otherwise.
        """
        return self.get_css_property(property_name=CSS.OVERFLOW) == 'auto'

