from enum import Enum
from typing import List, Optional, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Helpers.CSSEnumerations import CSS


class Appearance(Enum):
    AUTO = "auto"
    PNID = "p&id"
    MIMIC = "mimic"
    SIMPLE = "simple"


class Directional(Enum):
    RIGHT = "right"
    LEFT = "left"
    TOP = "top"
    BOTTOM = "bottom"


class Orientation(Enum):
    """If testing a Vessel, note that the Vessel has its own Orientation options."""
    RIGHT = "right"
    LEFT = "left"
    TOP = "top"
    BOTTOM = "bottom"


class State(Enum):
    DEFAULT = "default"
    RUNNING = "running"
    FAULTED = "faulted"
    STOPPED = "stopped"


class TextLabelLocation(Enum):
    RIGHT = "right"
    LEFT = "left"
    TOP = "top"
    BOTTOM = "bottom"
    HIDDEN = "hidden"


class ValueLabelLocation(Enum):
    RIGHT = "right"
    LEFT = "left"
    TOP = "top"
    BOTTOM = "bottom"
    HIDDEN = "hidden"


class SensorTextLabelLocation(Enum):
    RIGHT = "right"
    LEFT = "left"
    TOP = "top"
    BOTTOM = "bottom"
    HIDDEN = "hidden"
    INSIDE = "inside"


class SensorValueLabelLocation(Enum):
    RIGHT = "right"
    LEFT = "left"
    TOP = "top"
    BOTTOM = "bottom"
    HIDDEN = "hidden"
    INSIDE = "inside"


class CommonSymbol(BasicPerspectiveComponent):
    """
    When examining classes, you'll often see an odd pattern: "symbol_symbol_descriptor". This is a result of the Pump
    having multiple variants. A motor, for example, will ALWAYS be "motor_motor_descriptor", but a Pump could be
    "pump_centrifugal_descriptor" or "pump_vacuum_descriptor"
    """
    GENERIC_IA_SYMBOL_CLASS = "ia_symbolComponent"
    WRAPPER_LOCATOR = (By.CSS_SELECTOR, "div.ia_symbolComponent__wrapper")
    MAIN_SVG_LOCATOR = (By.CSS_SELECTOR, f"{WRAPPER_LOCATOR[1]} > svg")
    _LABEL_TEXT_LOCATOR = (By.CSS_SELECTOR, 'div[data-display-type="label"]')
    _VALUE_TEXT_LOCATOR = (By.CSS_SELECTOR, 'div[data-display-type="value"]')

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]],
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            description=description,
            poll_freq=poll_freq)
        self._main_svg = ComponentPiece(
            locator=self.MAIN_SVG_LOCATOR, driver=driver, parent_locator_list=self.locator_list, poll_freq=poll_freq)
        self._label_text = ComponentPiece(
            locator=self._LABEL_TEXT_LOCATOR, driver=driver, parent_locator_list=self.locator_list, poll_freq=poll_freq)
        self._value_text = ComponentPiece(
            locator=self._VALUE_TEXT_LOCATOR, driver=driver, parent_locator_list=self.locator_list, poll_freq=poll_freq)

    def get_label_text(self) -> str:
        """Get the text of the label of the Symbol. Distinct from the actual value of the Symbol."""
        return self._label_text.get_text()

    def get_value_text(self) -> str:
        """Get the value of the Symbol (including units). Distinct from label text of the Symbol."""
        return self._value_text.get_text()

    def symbol_has_appearance(self, appearance: Appearance) -> bool:
        """
        Determines whether the Symbol is currently using the supplied Appearance.

        returns: True, if the supplied Appearance is currently in use, False otherwise. Supplying an Appearance of
            `Auto` will always result in False.
        """
        return f"{self.GENERIC_IA_SYMBOL_CLASS}--{appearance.value}" in self.get_wrapper_classes()

    def symbol_has_orientation(self, orientation: Orientation) -> bool:
        """
        Determine if the supplied orientation is currently in use by the Symbol.

        returns: True, if the orientation is currently in use by the Symbol - False otherwise.
        """
        for html_class in self.get_wrapper_classes():
            if "orientation" in html_class:
                return orientation.value in html_class
        return False  # orientation not found

    def symbol_has_state(self, state: State) -> bool:
        """
        Determine if the supplied state is currently in use by the Symbol.

        returns: True, if the state is currently in use by the Symbol - False otherwise.
        """
        return f"{self.GENERIC_IA_SYMBOL_CLASS}--{state.value}" in self.get_wrapper_classes()

    def text_label_has_location(self, location: TextLabelLocation) -> bool:
        """
        Determine if the text label of the Symbol currently has the supplied location.

        returns: True, if the text label of the component has the supplied location, False otherwise.
        """
        _main_symbol_width = int(float(self._main_svg.get_computed_width(include_units=False)))
        _main_symbol_height = int(float(self._main_svg.get_computed_height(include_units=False)))
        _main_symbol_origin = self._main_svg.get_origin()
        _main_symbol_x = int(float(_main_symbol_origin.X))
        _main_symbol_y = int(float(_main_symbol_origin.Y))
        try:
            _text_label_width = int(float(self._label_text.get_computed_width(include_units=False)))
            _text_label_height = int(float(self._label_text.get_computed_height(include_units=False)))
            _text_label_origin = self._label_text.get_origin()
            _text_label_x = int(float(_text_label_origin.X))
            _text_label_y = int(float(_text_label_origin.Y))
            if location == TextLabelLocation.TOP:
                return _text_label_y + _text_label_height <= _main_symbol_y
            elif location == TextLabelLocation.BOTTOM:
                return _text_label_y >= _main_symbol_y + _main_symbol_height
            elif location == TextLabelLocation.LEFT:
                return _text_label_x + _text_label_width <= _main_symbol_x
            elif location == TextLabelLocation.RIGHT:
                return _text_label_x >= _main_symbol_x + _main_symbol_width
            else:
                raise ValueError(f"Invalid location: {location}")
        except TimeoutException:
            """
            The label was correctly "hidden", and therefore not found, and therefore we want to return True.
            Truth-wise our response is equivalent to returning whether the supplied location was HIDDEN.
            """
            return location == TextLabelLocation.HIDDEN

    def value_label_has_location(self, location: ValueLabelLocation) -> bool:
        """
        Determine if the value label of the Symbol currently has the supplied location.

        returns: True, if the value label of the component has the supplied location, False otherwise.
        """
        _main_symbol_width = int(float(self._main_svg.get_computed_width(include_units=False)))
        _main_symbol_height = int(float(self._main_svg.get_computed_height(include_units=False)))
        _main_symbol_origin = self._main_svg.get_origin()
        _main_symbol_x = int(float(_main_symbol_origin.X))
        _main_symbol_y = int(float(_main_symbol_origin.Y))
        try:
            _text_value_width = int(float(self._value_text.get_computed_width(include_units=False)))
            _text_value_height = int(float(self._value_text.get_computed_height(include_units=False)))
            _text_value_origin = self._value_text.get_origin()
            _text_value_x = int(float(_text_value_origin.X))
            _text_value_y = int(float(_text_value_origin.Y))
            if location == ValueLabelLocation.TOP:
                return _text_value_y + _text_value_height <= _main_symbol_y
            elif location == ValueLabelLocation.BOTTOM:
                return _text_value_y >= _main_symbol_y + _main_symbol_height
            elif location == ValueLabelLocation.LEFT:
                return _text_value_x + _text_value_width <= _main_symbol_x
            elif location == ValueLabelLocation.RIGHT:
                return _text_value_x >= _main_symbol_x + _main_symbol_width
            else:
                raise ValueError(f"Invalid location: {location}")
        except TimeoutException:
            """
            The label was correctly "hidden", and therefore not found, and therefore we want to return True.
            Truth-wise our response is equivalent to returning whether the supplied location was HIDDEN.
            """
            return location == ValueLabelLocation.HIDDEN

    def get_wrapper_classes(self) -> List[str]:
        """
        Obtain a list of every HTML class currently applied to the main Symbol. Used internally for determining
        which Appearance and/or State a Symbol has.
        """
        return self._main_svg.find().get_attribute(name="class").split(" ")


class _SymbolWithFeet(CommonSymbol):
    """
    Some Symbols contain feet as part of their appearance.
    """

    class Feet(Enum):
        """
        Feet are not available to all Symbols.
        """
        RIGHT = "right"
        LEFT = "left"
        TOP = "top"
        BOTTOM = "bottom"
        NONE = "none"

    def feet_have_display_state(self, feet_display_state: Feet) -> bool:
        """
        Determine the display state of the feet of a Motor Symbol.

        returns: True, if the feet currently have the supplied display state, False otherwise.
        """
        html_classes = self.get_wrapper_classes()
        feet_have_expected_html_class = False
        for html_class in html_classes:
            if "feet" in html_class:
                feet_have_expected_html_class = feet_display_state.value == html_class.split("-")[-1]
        return feet_have_expected_html_class or feet_display_state == Motor.Feet.NONE


class Motor(_SymbolWithFeet):
    """A Perspective Motor Symbol."""
    def __init__(self, locator, driver: WebDriver, parent_locator_list: Optional[List] = None, poll_freq: float = 0.5):
        super().__init__(locator=locator, driver=driver, parent_locator_list=parent_locator_list, poll_freq=poll_freq)


class Pump(_SymbolWithFeet):
    """A Perspective Pump Symbol."""

    class Variant(Enum):
        """
        Pumps have variant appearances which must be accounted for.
        """
        CENTRIFUGAL = "centrifugal"
        VACUUM = "vacuum"

    def __init__(self, locator, driver: WebDriver, parent_locator_list: Optional[List] = None, poll_freq: float = 0.5):
        super().__init__(locator=locator, driver=driver, parent_locator_list=parent_locator_list, poll_freq=poll_freq)

    def pump_is_variant(self, variant: Variant) -> bool:
        """
        Determine if the Pump currently displays as the supplied variant.

        returns: True, if the Pump is currently the supplied variant - False otherwise.
        """
        return f"{self.GENERIC_IA_SYMBOL_CLASS}-pump-{variant.value}" in self.get_wrapper_classes()


class Sensor(CommonSymbol):
    """A Perspective Sensor Symbol."""
    _SENSOR_BODY_LOCATOR = (By.CSS_SELECTOR, "g.sensor_sensor_body")

    def __init__(self, locator, driver: WebDriver, parent_locator_list: Optional[List] = None, poll_freq: float = 0.5):
        super().__init__(locator=locator, driver=driver, parent_locator_list=parent_locator_list, poll_freq=poll_freq)
        self._body = ComponentPiece(
            locator=self._SENSOR_BODY_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)

    def text_label_has_location(self, location: SensorTextLabelLocation) -> bool:
        """
        Determine if the text label of the Symbol currently has the supplied location.

        returns: True, if the text label of the component has the supplied location, False otherwise.
        """
        sensor_body_origin = self._body.get_origin()
        sensor_body_x = int(float(sensor_body_origin.X))
        sensor_body_y = int(float(sensor_body_origin.Y))
        sensor_body_width = int(float(self._body.get_computed_width(include_units=False)))
        sensor_body_height = int(float(self._body.get_computed_height(include_units=False)))
        try:
            text_label_origin = self._label_text.get_origin()
            text_label_x = int(float(text_label_origin.X))
            text_label_y = int(float(text_label_origin.Y))
            text_label_height = int(float(self._label_text.get_computed_height(include_units=False)))
            text_label_width = int(float(self._label_text.get_computed_width(include_units=False)))
            if location == SensorTextLabelLocation.TOP:
                return text_label_y + text_label_height <= sensor_body_y
            elif location == SensorTextLabelLocation.BOTTOM:
                return text_label_y >= sensor_body_y + sensor_body_height
            elif location == SensorTextLabelLocation.LEFT:
                return text_label_x + text_label_width <= sensor_body_x
            elif location == SensorTextLabelLocation.RIGHT:
                return text_label_x >= sensor_body_x + sensor_body_width
            elif location == SensorTextLabelLocation.INSIDE:
                return (sensor_body_x < text_label_x < (sensor_body_x + sensor_body_width)) \
                       and (sensor_body_y < text_label_y < (sensor_body_y + sensor_body_height))
            else:
                raise ValueError(f"Invalid location: {location}")
        except TimeoutException:
            """
            The text label was correctly "hidden", and therefore not found, and therefore we want to return True.
            Truth-wise our response is equivalent to returning whether the supplied location was HIDDEN.
            """
            return location == TextLabelLocation.HIDDEN

    def value_label_has_location(self, location: SensorValueLabelLocation) -> bool:
        """
        Determine if the value label of the Sensor currently has the supplied location.

        returns: True, if the value label of the Sensor has the supplied location, False otherwise.
        """
        sensor_body_origin = self._body.get_origin()
        sensor_body_x = int(float(sensor_body_origin.X))
        sensor_body_y = int(float(sensor_body_origin.Y))
        sensor_body_width = int(float(self._body.get_computed_width(include_units=False)))
        sensor_body_height = int(float(self._body.get_computed_height(include_units=False)))
        try:
            value_label_origin = self._value_text.get_origin()
            value_label_x = int(float(value_label_origin.X))
            value_label_y = int(float(value_label_origin.Y))
            value_label_width = int(float(self._value_text.get_computed_width(include_units=False)))
            value_label_height = int(float(self._value_text.get_computed_height(include_units=False)))
            if location == SensorValueLabelLocation.TOP:
                return value_label_y + value_label_height <= sensor_body_y
            elif location == SensorValueLabelLocation.BOTTOM:
                return value_label_y >= sensor_body_y + sensor_body_height
            elif location == SensorValueLabelLocation.LEFT:
                return value_label_x + value_label_width <= sensor_body_x
            elif location == SensorValueLabelLocation.RIGHT:
                return value_label_x >= sensor_body_x + sensor_body_width
            elif location == SensorValueLabelLocation.INSIDE:
                return (sensor_body_x < value_label_x < (sensor_body_x + sensor_body_width)) \
                    and (sensor_body_y < value_label_y < (sensor_body_y + sensor_body_height))
            else:
                raise ValueError(f"Invalid location: {location}")
        except TimeoutException:
            """
            The value label was correctly "hidden", and therefore not found, and therefore we want to return True.
            Truth-wise our response is equivalent to returning whether the supplied location was HIDDEN.
            """
            return location == TextLabelLocation.HIDDEN


class Valve(CommonSymbol):
    """A Perspective Valve Symbol."""
    _MAIN_VALVE_LOCATOR = (By.CSS_SELECTOR, "g.valve_2-way_main_valve")
    _LEFT_IN_OUT_LOCATOR = (By.CSS_SELECTOR, "g.valve_2-way_left")
    _RIGHT_IN_OUT_LOCATOR = (By.CSS_SELECTOR, "g.valve_2-way_right")

    class State(Enum):
        """
        Valve Symbols have different States available to it than other Perspective Symbols.
        """
        DEFAULT = "default"
        OPEN = "open"
        CLOSED = "closed"
        FAILED_TO_CLOSE = "failedToClose"
        FAILED_TO_OPEN = "failedToOpen"
        PARTIALLY_CLOSED = "partiallyClosed"

    def __init__(self, locator, driver: WebDriver, parent_locator_list: Optional[List] = None, poll_freq: float = 0.5):
        super().__init__(locator=locator, driver=driver, parent_locator_list=parent_locator_list, poll_freq=poll_freq)
        self._main_valve = ComponentPiece(
            locator=self._MAIN_VALVE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._left_in_out = ComponentPiece(
            locator=self._LEFT_IN_OUT_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._right_in_out = ComponentPiece(
            locator=self._RIGHT_IN_OUT_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)

    def flow_is_reversed(self) -> bool:
        """
        Determine if the flow of the Valve component is currently displaying as reversed. Flow is considered to be
        "reversed" if the "left" in/out is a different color than the main valve piece and the right in/out
        is the same color as the main valve piece.
        """
        main_fill = self._main_valve.get_css_property(property_name=CSS.FILL)
        right_fill = self._right_in_out.get_css_property(property_name=CSS.FILL)
        return (right_fill == main_fill) and self._left_and_right_have_different_fill()

    def symbol_has_state(self, state: State) -> bool:
        """
        Determine if the supplied state is currently in use by the Valve.

        returns: True, if the state is currently in use by the Valve - False otherwise.
        """
        valve_has_state = super().symbol_has_state(state=state)
        # We can actually check that the valve is displaying this state because of visual differences.
        if state == Valve.State.PARTIALLY_CLOSED:
            valve_has_state = valve_has_state and \
                              self._left_and_right_have_different_fill()
        return valve_has_state

    def _left_and_right_have_different_fill(self) -> bool:
        """
        Determine if the left and right in/out pieces of the Valve have different fill values.

        returns: True, if the fill property is different - False otherwise.
        """
        left_fill = self._left_in_out.get_css_property(property_name=CSS.FILL)
        right_fill = self._right_in_out.get_css_property(property_name=CSS.FILL)
        return left_fill != right_fill


class Vessel(CommonSymbol):
    """A Perspective Vessel Symbol."""
    _AGITATOR_AND_ROTOR_LOCATOR = (By.CSS_SELECTOR, "g[class^='vessel_cylindricalTank_agitator']")

    class Orientation(Enum):
        """The Vessel Symbol has only two orientations available for use."""
        VERTICAL = "vertical"
        HORIZONTAL = "horizontal"

    def __init__(self, locator, driver: WebDriver, parent_locator_list: Optional[List] = None, poll_freq: float = 0.5):
        super().__init__(locator=locator, driver=driver, parent_locator_list=parent_locator_list, poll_freq=poll_freq)
        self._agitator_and_rotor = ComponentPiece(
            locator=self._AGITATOR_AND_ROTOR_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)

    def agitator_and_rotor_are_displayed(self) -> bool:
        """
        Determine if the Vessel is currently displaying the agitator and rotor.

        returns: True, if both are displayed - False otherwise.
        """
        try:
            return len(self._agitator_and_rotor.find_all(wait_timeout=1)) == 2
        except TimeoutException:
            return False
