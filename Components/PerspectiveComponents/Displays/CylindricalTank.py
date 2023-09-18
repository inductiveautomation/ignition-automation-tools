from typing import Optional, List, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Helpers.CSSEnumerations import CSS, CSSPropertyValue


class CylindricalTank(BasicPerspectiveComponent):
    """A Perspective Cylindrical Tank Component."""
    _TANK_LOCATOR = (By.CSS_SELECTOR, 'path.ia_cylindricalTankComponent__tank')
    _LIQUID_LOCATOR = (By.CSS_SELECTOR, 'path.ia_cylindricalTankComponent__liquid')
    _VALUE_DISPLAY_LOCATOR = (By.CSS_SELECTOR, 'text.ia_cylindricalTankComponent__valueDisplay')
    _POTENTIAL_SYMBOLS_TO_OMIT_FROM_NUMERIC_VALUES = ["$", "%"]

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
        self._tank = ComponentPiece(locator=self._TANK_LOCATOR, driver=driver, wait_timeout=0, poll_freq=poll_freq)
        self._tank_liquid = ComponentPiece(
            locator=self._LIQUID_LOCATOR,
            driver=driver,
            wait_timeout=0,
            poll_freq=poll_freq)
        self._tank_value = ComponentPiece(
            locator=self._VALUE_DISPLAY_LOCATOR,
            driver=driver,
            wait_timeout=0,
            poll_freq=poll_freq)

    def get_liquid_property(self, property_name: CSSPropertyValue) -> str:
        """
        Obtain the value of some CSS property from the liquid within the Cylindrical Tank.

        :param property_name: The CSS property from which you would like the value.

        :returns: The value of the supplied CSS property as is in use by the liquid of the Cylindrical Tank.

        :raises TimeoutException: If the liquid of the Cylindrical Tank is not present.
        """
        try:
            return self._tank_liquid.get_css_property(property_name=property_name)
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate the liquid of the Cylindrical Tank") from toe

    def get_tank_color(self) -> str:
        """
        Obtain the color in use for the actual tank portion of the Cylindrical Tank.

        :returns: The color in use for the container portion of the Cylindrical Tank as a string. Note that different
            browsers may return this value in different formats (RGB vs hex).

        :raises TimeoutException: If the tank of the Cylindrical Tank is not present.
        """
        try:
            return self._tank.get_css_property(property_name=CSS.FILL)
        except TimeoutException as toe:
            raise TimeoutException(msg="Unable to locate the tank portion of the Cylindrical Tank") from toe

    def get_text(self) -> str:
        """
        Obtain the displayed text of the Cylindrical Tank, including any displayed units.

        :returns: The displayed value and units of the Cylindrical Tank, as a string.
        """
        return self._tank_value.get_text()

    def value_is_displayed(self) -> bool:
        """
        Determine if the Cylindrical Tank is displaying a value and/or units.

        :returns True, if the Cylindrical Tank is currently displaying a value and/or units - False otherwise.
        """
        try:
            return self._tank_value.find() is not None
        except TimeoutException:
            return False
