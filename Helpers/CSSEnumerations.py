class CSSPropertyValue:
    """
    The CSSPropertyValue class serves two purposes:
    1. It allows for some areas of code to specify a type other than string, which would otherwise be confusing.
    2. It provides an avenue to reduce potential typos.

    Consider the following example:
    self._component.get_css_property_value('full') == ""

    Such a statement would always return True, because the minor typo prevents the 'fill' value from being queried. By
    providing and requiring an enumerated value we remove any chance of such a typo.
    """
    value = None

    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return self.value


class CSS:
    """
    An ever-expanding enumeration of sorts which contains common CSS properties. For properties which are themselves
    enumerations, we provide those enumerated values.
    """

    class AlignItems:
        CENTER = CSSPropertyValue("center")
        END = CSSPropertyValue("end")
        FLEX_END = CSSPropertyValue("flex-end")
        FLEX_START = CSSPropertyValue("flex-start")
        NORMAL = CSSPropertyValue("normal")
        START = CSSPropertyValue("start")
        STRETCH = CSSPropertyValue("stretch")

    BACKGROUND_COLOR = CSSPropertyValue("background-color")
    BORDER_TOP_COLOR = CSSPropertyValue("border-top-color")
    BORDER_TOP_LEFT_RADIUS = CSSPropertyValue("border-top-left-radius")
    BORDER_TOP_RIGHT_RADIUS = CSSPropertyValue("border-top-right-radius")
    BORDER_TOP_STYLE = CSSPropertyValue("border-top-style")
    BOTTOM = CSSPropertyValue("bottom")
    COLOR = CSSPropertyValue("color")

    class Cursor:
        GRAB = CSSPropertyValue("grab")
        NOT_ALLOWED = CSSPropertyValue("not-allowed")
        POINTER = CSSPropertyValue("pointer")
        WAIT = CSSPropertyValue("wait")

    class Display:
        """
        Display has loads of options and can take multiple arguments, but these are the basic/common options.
        """
        BLOCK = CSSPropertyValue("block")
        FLEX = CSSPropertyValue("flex")
        INLINE = CSSPropertyValue("inline")

    FILL = CSSPropertyValue("fill")
    FILL_OPACITY = CSSPropertyValue("fill-opacity")

    class FlexFlow:
        """
        This class currently only contains values supported by the Flex Container for direction.
        """
        COLUMN = CSSPropertyValue("column")
        COLUMN_REVERSE = CSSPropertyValue("column-reverse")
        ROW = CSSPropertyValue("row")
        ROW_REVERSE = CSSPropertyValue("row-reverse")

    FONT_SIZE = CSSPropertyValue("font-size")
    HEIGHT = CSSPropertyValue("height")
    JUSTIFY_CONTENT = CSSPropertyValue('justify-content')
    MARGIN_BOTTOM = CSSPropertyValue("margin-bottom")
    MARGIN_LEFT = CSSPropertyValue("margin-left")
    MARGIN_RIGHT = CSSPropertyValue("margin-right")
    MARGIN_TOP = CSSPropertyValue("margin-top")
    MAX_WIDTH = CSSPropertyValue("max-width")
    OBJECT_FIT = CSSPropertyValue("object-fit")
    OPACITY = CSSPropertyValue("opacity")
    OVERFLOW = CSSPropertyValue("overflow")
    POSITION = CSSPropertyValue("position")
    STROKE = CSSPropertyValue("stroke")
    STROKE_DASHARRAY = CSSPropertyValue("stroke-dasharray")
    STROKE_WIDTH = CSSPropertyValue("stroke-width")
    TEXT_ALIGN = CSSPropertyValue('text-align')
    TRANSITION = CSSPropertyValue("transition")
    TRANSITION_DURATION = CSSPropertyValue("transition-duration")
    TRANSITION_TIMING_FUNCTION = CSSPropertyValue("transition-timing-function")
    WIDTH = CSSPropertyValue("width")
    Z_INDEX = CSSPropertyValue("z-index")
    