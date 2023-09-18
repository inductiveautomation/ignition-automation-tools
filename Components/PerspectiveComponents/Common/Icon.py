from typing import Tuple, Optional, List

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece
from Helpers.CSSEnumerations import CSS


class CommonIcon(ComponentPiece):
    """An Icon which could be used anywhere within Perspective, including within other components."""
    # This list will grow over time, until Dev takes this on as a unit test for their Icon strip-and-zip
    _KNOWN_EXTRANEOUS_D_ATTRIBUTE_LIST = [
        'M24 24H0V0h24v24z',
        'M0,0h24v24H0V0z',
        'M0,0h24 M24,24H0'
    ]

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
        self._children = ComponentPiece(
            locator=(By.CSS_SELECTOR, "g > *"),
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._bad_borders = [
            ComponentPiece(
                locator=(By.CSS_SELECTOR, f'path[d="{bad_border}"]'),
                driver=driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq) for bad_border in self._KNOWN_EXTRANEOUS_D_ATTRIBUTE_LIST
        ]
        self._internal_g = ComponentPiece(
            locator=(By.CSS_SELECTOR, "g > g"),
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)

    def get_fill_color(self) -> str:
        """
        Obtain the fill in use by the Icon. In the event any children (internal <g> elements) of the Icon have a
        different fill, return that value instead.

        :returns: The fill color in use by the Icon. As a way to verify any potential children of the icon are
            displaying the same expected color, this function will return any mismatched child color instead.
        """
        local_fill = self.get_css_property(property_name=CSS.FILL)
        try:
            for child in self._children.find_all(wait_timeout=1):
                child_fill = child.value_of_css_property("fill")  # WebElement (WE), so have to use WE function
                if child_fill != local_fill and child_fill != 'none':  # ignore 'none' because we have 0 control over it
                    return child_fill
        except TimeoutException:
            pass
        return local_fill

    def get_icon_name(self) -> str:
        """
        Obtain the library and id of the Icon as a slash-delimited string.

        Example: material/perm_identity denotes the 'perm_identity' svg from the 'material' library.

        :returns: The library and id of the svg in use by the Icon Component as a slash-delimited string.

        raises: ValueError if the internal <g> element claims to be using a different id than the top-level
        component declares.
        """
        library_and_name = self.find().get_attribute("data-icon")
        name_in_use = self._internal_g.find().get_attribute("id")
        if name_in_use != library_and_name.split("/")[1]:
            raise ValueError(f"The icon declared a library:name combo of {library_and_name} but is actually "
                             f"using {name_in_use} within the <g> element.")
        return library_and_name

    def get_stroke_color(self) -> str:
        """
        Obtain the stroke in use by the Icon. In the event any children (internal <g> elements) of the Icon have a
        different stroke, return that value instead.

        :returns: The stroke color in use by the Icon. As a way to verify any potential children of the icon are
            displaying the same expected color, this function will return any mismatched child color instead.
        """
        local_stroke = self.get_css_property(property_name=CSS.STROKE)
        try:
            for child in self._children.find_all(wait_timeout=1):
                child_stroke = child.value_of_css_property("stroke")  # WebElement (WE), so have to use WE function
                if child_stroke != local_stroke:
                    return child_stroke
        except TimeoutException:
            pass
        return local_stroke

    def get_viewbox_as_dict(self) -> dict:
        """
        Get the viewbox of the Icon as a Python dictionary.

        returns: A dictionary with the following keys: 'x', 'y', 'width', and 'height'.
        """
        viewbox_pieces = self.driver.execute_script(
            'return arguments[0].getAttribute("viewBox")', self.find()).split(" ")
        viewbox_as_dict = dict()
        viewbox_as_dict['x'] = viewbox_pieces[0]
        viewbox_as_dict['y'] = viewbox_pieces[1]
        viewbox_as_dict['width'] = viewbox_pieces[2]
        viewbox_as_dict['height'] = viewbox_pieces[3]
        return viewbox_as_dict

    def has_extraneous_border(self) -> bool:
        """
        Determine if this Icon has any unexpected border. Used internally to verify packaged Icons have no
        borders which would interfere with styling.

        :returns: True, if any internal border is found for the Icon - False otherwise.
        """
        for bad_border in self._bad_borders:
            try:
                return bad_border.find(wait_timeout=0) is not None
            except TimeoutException:
                pass
        return False

    def is_rendered(self) -> bool:
        """
        Determine if this Icon is actually rendered/displayed.

        :returns: True, if rendered - False otherwise.
        """
        try:
            return self._internal_g.find(wait_timeout=0.5) is not None
        except TimeoutException:
            return False
