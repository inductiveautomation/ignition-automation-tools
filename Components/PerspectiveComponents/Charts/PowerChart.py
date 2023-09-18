from enum import Enum
from typing import Union, List, Tuple, Optional

from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from Components.BasicComponent import ComponentPiece, BasicPerspectiveComponent
from Components.Common.Button import CommonButton
from Components.PerspectiveComponents.Common.Checkbox import CommonCheckbox
from Components.PerspectiveComponents.Common.DateRangeSelector import \
    CommonDateRangeSelector, DateRangeSelectorTab, DateRangeSelectorTimeUnit, HistoricalRange, PerspectiveDate
from Components.PerspectiveComponents.Common.Table import Table as CommonTable
from Components.PerspectiveComponents.Common.TagBrowseTree import CommonTagBrowseTree
from Components.PerspectiveComponents.Inputs.TextField import TextField
from Helpers.CSSEnumerations import CSS, CSSPropertyValue
from Helpers.IAAssert import IAAssert
from Helpers.IAExpectedConditions import IAExpectedConditions as IAec
from Helpers.IAExpectedConditions.IAExpectedConditions import TextCondition
from Helpers.IASelenium import IASelenium


class OptionBarButton(Enum):
    """An enumeration of the available Option Bar buttons."""
    PAN_AND_ZOOM = 'panAndZoom'
    X_TRACE = 'xTrace'
    RANGE_BRUSH = 'rangeBrush'
    ANNOTATION = 'annotation'
    FULL_SCREEN = 'fullscreen'
    SETTINGS = 'settings'
    MORE = "more"


class PenControlColumn(Enum):
    """An enumeration of the available Pen Control columns."""
    AVERAGE = "average"
    AXIS = "axis"
    CURRENT_VALUE = "currentValue"
    MAXIMUM = "maximum"
    MINIMUM = "minimum"
    PLOT = "plot"
    X_TRACE = "xTrace"


class RangeBrushColumn(Enum):
    """An enumeration of the available Range Brush columns."""
    AVERAGE = "average"
    DELTA = "delta"
    FIRST = "first"
    LAST = "last"
    LCL = "lcl"
    MAXIMUM = "maximum"
    MINIMUM = "minimum"
    MEDIAN = "median"
    STANDARD_DEVIATION = "standardDeviation"
    SUM = "sum"
    UCL = "ucl"


class Tab(Enum):
    """An enumeration of the available Tabs within the settings panel."""
    AXES = "Axes"
    COLUMNS = "Columns"
    PENS = "Pens"
    PLOTS = "Plots"


class PowerChart(BasicPerspectiveComponent):
    """A Perspective Power Chart Component."""

    class _PowerChartFooter(ComponentPiece):
        _FOOTER_LOCATOR = (By.CSS_SELECTOR, 'div.chart-footer')

        def __init__(
                self,
                parent_locator_list: List[Tuple[By, str]],
                driver: WebDriver,
                description: Optional[str] = None,
                poll_freq: float = 0.5):
            super().__init__(
                locator=self._FOOTER_LOCATOR,
                driver=driver,
                parent_locator_list=parent_locator_list,
                description=description,
                poll_freq=poll_freq)

        def is_in_responsive_mode(self) -> bool:
            """
            Determine if the Power Chart is in responsive mode.

            :returns: True, if the Power Chart is currently displaying in a responsive layout - False otherwise.
            """
            try:
                return "mobile" in self.find().get_attribute(name="class")
            except TimeoutException as toe:
                raise TimeoutException(msg="Unable to locate the Power Chart as defined by its locator") from toe

    class _PowerChartGraph(ComponentPiece):
        _LINE_CHART_CONTAINER_LOCATOR = (By.CSS_SELECTOR, "div.main-chart-container")
        _GRAPHED_LINE_LOCATOR = (By.CSS_SELECTOR, f"g.ia_lineChart > g > g")
        _LINE_PATH_LOCATOR = (By.CSS_SELECTOR, "> path")
        _GRAPH_CONTAINER_LOCATOR = (By.CSS_SELECTOR, "g.chart-row")
        _LABEL_LOCATOR = (By.CSS_SELECTOR, "text.ia_powerChartComponent__timeAxis__values")
        _Y_AXIS_GRID_LOCATOR = (By.CSS_SELECTOR, "line.ia_powerChartComponent__yAxis__grid")
        _X_AXIS_GRID_LOCATOR = (By.CSS_SELECTOR, "line.ia_powerChartComponent__timeAxis__grid")
        _X_AXIS_LOCATOR = (By.CSS_SELECTOR, "line.ia_powerChartComponent__timeAxis__axis")
        _Y_AXIS_LABEL_LOCATOR = (By.CSS_SELECTOR, "text.ia_powerChartComponent__yAxis__label")
        _Y_AXIS_LOCATOR = (By.CSS_SELECTOR, "line.ia_powerChartComponent__yAxis__axis")

        def __init__(
                self,
                parent_locator_list: List[Tuple[By, str]],
                driver: WebDriver,
                description: Optional[str] = None,
                poll_freq: float = 0.5):
            super().__init__(
                parent_locator_list=parent_locator_list,
                driver=driver,
                locator=self._LINE_CHART_CONTAINER_LOCATOR,
                description=description,
                poll_freq=poll_freq)
            self._row_container = ComponentPiece(
                locator=self._GRAPH_CONTAINER_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The container of all graphed lines in the chart.",
                poll_freq=poll_freq)
            self._graphed_line = ComponentPiece(
                locator=self._GRAPHED_LINE_LOCATOR,
                driver=driver,
                parent_locator_list=self._row_container.locator_list,
                description="The actual graphed line.",
                poll_freq=poll_freq)
            self._line_paths = ComponentPiece(
                parent_locator_list=self._graphed_line.locator_list,
                locator=self._LINE_PATH_LOCATOR,
                driver=driver,
                description="The <path> element within the line which describes the drawn path of the line.",
                poll_freq=poll_freq)
            self._time_axis_labels = ComponentPiece(
                locator=self._LABEL_LOCATOR,
                driver=driver,
                parent_locator_list=parent_locator_list,
                description="The labels of the time axis, usually found along the bottom of the graphed lines.",
                poll_freq=poll_freq)
            self._y_axis_grid_line = ComponentPiece(
                locator=self._Y_AXIS_GRID_LOCATOR,
                driver=driver,
                parent_locator_list=parent_locator_list,
                poll_freq=poll_freq)
            self._x_axis_grid_line = ComponentPiece(
                locator=self._X_AXIS_GRID_LOCATOR,
                driver=driver,
                parent_locator_list=parent_locator_list,
                poll_freq=poll_freq)
            self._x_axis = ComponentPiece(
                locator=self._X_AXIS_LOCATOR,
                driver=driver,
                parent_locator_list=parent_locator_list,
                description="The line which defines the bottom of the graphed area.",
                poll_freq=poll_freq)
            self._y_axis_label = ComponentPiece(
                locator=self._Y_AXIS_LABEL_LOCATOR,
                driver=driver,
                parent_locator_list=parent_locator_list,
                description="The labels of the Y axis, which can be found to either the left or right of the graphed "
                            "lines.",
                poll_freq=poll_freq)
            self._y_axis = ComponentPiece(
                locator=self._Y_AXIS_LOCATOR,
                driver=driver,
                parent_locator_list=parent_locator_list,
                description="The line which defines either the left or right border of the graph.",
                poll_freq=poll_freq)

        def get_count_of_graphed_pens(self) -> int:
            """
            Obtain a count of pens which are displayed in the chart.

            :returns: A count of pens currently rendered in the chart.
            """
            try:
                # each graphed pen has 2 <path> elements
                return int(len(self._line_paths.find_all(wait_timeout=1)) / 2)
            except TimeoutException:
                return 0

        def get_displayed_time_axis_labels(self) -> List[str]:
            """
            Obtain the labels displayed on the X (time) axis.

            :returns: A list which contains all currently displayed labels from the X (time) axis.

            :raises TimeoutException: If no labels are displayed on the X (time) axis.
            """
            try:
                return [_.text for _ in self._time_axis_labels.find_all()]
            except TimeoutException as toe:
                raise TimeoutException(msg="No labels displayed for the Power Chart") from toe

        def get_drawn_path(self, pen_checkbox_color_as_string: str) -> str:
            """
            Obtain the drawn path of a graphed pen. Useful for determining when a graphed pen has updated.

            :param pen_checkbox_color_as_string: The color used to graph the pen for which you would like the drawn
                path.

            :returns: A string which represents the actual graphed line of a pen.

            :raises IndexError: If no graphed pen has the supplied color.
            :raises TimeoutException: If no pens are graphed.
            """
            try:
                return list(
                    filter(
                        lambda e: e.value_of_css_property(CSS.STROKE.value) == pen_checkbox_color_as_string,
                        self._line_paths.find_all()))[0].get_attribute("d")
            except TimeoutException as toe:
                raise TimeoutException(msg="No pens are currently graphed.") from toe
            except IndexError as ie:
                raise IndexError(f"No pen graphed with a color of '{pen_checkbox_color_as_string}'.") from ie

        def get_x_axis_html_class(self) -> str:
            """
            Obtain the HTML class of the X axis.

            :returns: The class of the X axis as it exists in the DOM.

            :raises TimeoutException: If no X axis is present.
            """
            try:
                return self._x_axis.find().get_attribute(name="class")
            except TimeoutException as toe:
                raise TimeoutException(msg="No X axis present.") from toe

        def get_x_axis_css_property_value(self, property_name: Union[CSSPropertyValue, str]) -> str:
            """
            Obtain the value of a CSS property from the X axis.

            :param property_name: The name of the CSS property you would like the value of.

            :returns: The value of the requested CSS property.

            :raises TimeoutException: If no labels are present on the X (time) axis.
            """
            try:
                return self._time_axis_labels.get_css_property(property_name=property_name)
            except TimeoutException as toe:
                raise TimeoutException(msg="No labels are present for the X (time) axis.") from toe
        
        def get_y_axis_html_class(self) -> str:
            """
            Obtain the HTML class of the Y axis.

            :returns: The class of the Y axis as it exists in the DOM.

            :raises TimeoutException: If no Y axis is present.
            """
            try:
                return self._y_axis_label.find().get_attribute(name="class")
            except TimeoutException as toe:
                raise TimeoutException(msg="No labels present on the Y axis.") from toe

        def get_y_axis_vertical_bar_css_property(self, property_name: Union[CSSPropertyValue, str]) -> str:
            """
            Obtain a CSS property value from the Y axis.

            :param property_name: The name of the CSS property to retrieve the value of.

            :returns: The value of the requested CSS property from the Y axis.

            :raises TimeoutException: If no Y axis is present.
            """
            try:
                return self._y_axis.get_css_property(property_name=property_name)
            except TimeoutException as toe:
                raise TimeoutException(msg="No Y axis is present.") from toe

        def get_y_axis_label_css_property_value(self, property_name: Union[CSSPropertyValue, str]) -> str:
            """
            Obtain the value of a CSS property from the Y axis.

            :param property_name: The name of the CSS property you would like the value of.

            :returns: The value of the requested CSS property.

            :raises TimeoutException: If no labels are present on the Y axis.
            """
            try:
                return self._y_axis_label.get_css_property(property_name=property_name)
            except TimeoutException as toe:
                raise TimeoutException(msg="No labels present on the Y axis") from toe

        def click_and_drag_chart(self, x_offset: int = 0, y_offset: int = 0) -> None:
            """
            Blindly click within the Power Chart and then drag some number of pixels before releasing the click event.

            :param x_offset: The number of pixels to the right of the upper left corner to click.
            :param y_offset: The number of pixels down from the upper left corner to click.
            """
            ActionChains(driver=self.driver) \
                .click_and_hold(on_element=self.find()) \
                .move_by_offset(xoffset=x_offset, yoffset=y_offset) \
                .release() \
                .perform()
            self.wait_on_binding(time_to_wait=1)

        def get_count_of_x_axis_grid_lines(self, _already_attempted=False) -> int:
            """
            Obtain a count of lines displayed on the X axis.

            :param _already_attempted: Used internally to re-try in the event the Power Chart updates.

            :returns: A count of vertical lines currently displayed on the X axis of the Power Chart.
            """
            try:
                return len(self._x_axis_grid_line.find_all())
            except TimeoutException:
                return 0
            except StaleElementReferenceException as sere:
                if not _already_attempted:
                    return self.get_count_of_x_axis_grid_lines(
                        _already_attempted=True)
                else:
                    raise sere

        def get_count_of_y_axis_grid_lines(self, _already_attempted=False) -> int:
            """
            Obtain a count of lines displayed on the Y axis.

            :param _already_attempted: Used internally to re-try in the event the Power Chart updates.

            :returns: A count of horizontal lines currently displayed on the Y axis of the Power Chart.
            """
            try:
                return len(self._y_axis_grid_line.find_all())
            except TimeoutException:
                return 0
            except StaleElementReferenceException as sere:
                if not _already_attempted:
                    return self.get_count_of_y_axis_grid_lines(
                        _already_attempted=True)
                else:
                    raise sere

        def get_css_property_from_x_axis_grid(self, property_name: Union[CSSPropertyValue, str]) -> str:
            """
            Obtain the value of a CSS property from the grid of the X axis.

            :param property_name: The name of the property you want to value of.

            :returns: The value of the requested CSS property from the X axis grid.

            :raises TimeoutException: If no X axis grid is present.
            """
            try:
                return self._x_axis_grid_line.get_css_property(property_name=property_name)
            except StaleElementReferenceException:
                return self.get_css_property_from_x_axis_grid(property_name=property_name)
            except TimeoutException as toe:
                raise TimeoutException(
                    msg="No grid line was found for the X axis.") from toe

        def get_css_property_from_y_axis_grid(self, property_name: Union[CSSPropertyValue, str]) -> str:
            """
            Obtain the value of a CSS property from the grid of the Y axis.

            :param property_name: The name of the property you want to value of.

            :returns: The value of the requested CSS property from the Y axis grid.

            :raises TimeoutException: If no Y axis grid is present.
            """
            try:
                return self._y_axis_grid_line.get_css_property(property_name=property_name)
            except StaleElementReferenceException:
                return self.get_css_property_from_y_axis_grid(
                    property_name=property_name)
            except TimeoutException as toe:
                raise TimeoutException(
                    msg="No grid line was found for the Y axis.") from toe

        def line_is_displayed_by_color(self, pen_checkbox_color_as_str: str) -> bool:
            """
            Determine if a line is graphed.

            :param pen_checkbox_color_as_str: The color to look for in the graph. This value MUST be supplied in the
                same form as the browser in use would return a color value. It is recommended to avoid supplying
                hard-coded colors and instead supply values retrieved from the browser.

            :returns: True, if any graphed line uses the supplied color - False otherwise.
            """
            try:
                return len(
                    list(
                        filter(
                            lambda e: e.value_of_css_property(CSS.STROKE.value) == pen_checkbox_color_as_str,
                            self._line_paths.find_all()))) == 1
            except TimeoutException:
                return False

        def set_range_brush_basic(self) -> None:
            """
            Applies the range brush to the graph via a short drag event.
            """
            self.click_and_drag_chart(x_offset=100, y_offset=0)

    class _PowerChartHeader(ComponentPiece):
        """
        The header of the Power Chart, where the Option Bar Buttons live, as well as the range selector.
        """
        # TODO remove after IGN-5195
        _FULLSCREEN_BUTTON_ACTIVE_PATH = "M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"

        _GENERIC_ICON_STRING = "ia_powerChartComponent__icon__"
        _BUTTON_ACTIVE_CLASS = "ia_powerChartComponent__icon--active"
        _HEADER_LOCATOR = (By.CSS_SELECTOR, 'div.chart-header')
        _FULLSCREEN_BUTTON_ID_SUFFIX = "fullscreen"
        _TAG_BROWSER_BUTTON_LOCATOR = (By.CSS_SELECTOR, "div.tag-browser-icon-and-timerange span.show-tag-browser-icon")
        _TITLE_LOCATOR = (By.ID, "ia_powerChartComponent__title")

        def __init__(
                self,
                parent_locator_list: List[Tuple[By, str]],
                driver: WebDriver,
                poll_freq: float = 0.5):
            super().__init__(
                locator=self._HEADER_LOCATOR,
                driver=driver,
                parent_locator_list=parent_locator_list,
                poll_freq=poll_freq)
            self._tag_browser_button = ComponentPiece(
                locator=self._TAG_BROWSER_BUTTON_LOCATOR,
                driver=self.driver,
                parent_locator_list=self.locator_list,
                description="The button used to expand the Tag Browser Tree.",
                poll_freq=poll_freq)
            self._fullscreen_button_path = ComponentPiece(
                locator=(By.CSS_SELECTOR, f"#{self._GENERIC_ICON_STRING}{self._FULLSCREEN_BUTTON_ID_SUFFIX} path"),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                description="The <path> element of the fullscreen button.",
                poll_freq=poll_freq)
            self._date_range_selector = CommonDateRangeSelector(
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The Date Range Selector of the Power Chart. If enabled, this is found in the upper-left "
                            "of the Power Chart.",
                poll_freq=poll_freq)
            self._option_bar_buttons = {}
            self._title = ComponentPiece(
                locator=self._TITLE_LOCATOR,
                driver=driver,
                parent_locator_list=parent_locator_list,
                description="The title of the Power Chart. If configured, this will be found on the left side of the "
                            "Power Chart, between the toolbar area of the Power Chart and the graph itself.",
                poll_freq=poll_freq)

        def apply_changes(self) -> None:
            """
            Click the Apply button in the range selector.

            :raises TimeoutException: If the range selector is not present, or if the Apply button is not present.
            """
            self._date_range_selector.apply_changes()

        def button_is_active(self, option_bar_button: OptionBarButton) -> bool:
            """
            Determine if an Option Bar button is active (selected/in-use).

            :param option_bar_button: The Option Bar button to check the status of.

            :returns: True, if the supplied Option Bar button is active - False otherwise.
            """
            try:
                if option_bar_button == OptionBarButton.FULL_SCREEN:
                    # special handling for fullscreen button
                    return self._FULLSCREEN_BUTTON_ACTIVE_PATH \
                        == self._fullscreen_button_path.find().get_attribute(
                            name="d")
                else:
                    return self._BUTTON_ACTIVE_CLASS in self._get_option_bar_button(
                        option_bar_button=option_bar_button).find().get_attribute("class")
            except TimeoutException as toe:
                raise TimeoutException(
                    msg=f"No {option_bar_button.value} button found among the Option Bar buttons.") from toe

        def button_is_displayed(self, option_bar_button: OptionBarButton) -> bool:
            """
            Determine if an Option Bar button is displayed.

            :param option_bar_button: The Option Bar button we will check.

            :returns: True, if the supplied Option Bar button is displayed - False otherwise.
            """
            try:
                return self._get_option_bar_button(option_bar_button=option_bar_button).find().is_displayed()
            except TimeoutException:
                return False

        def click_option_bar_button(self, option_bar_button: OptionBarButton) -> None:
            """
            Click a button located within the Option Bar area.

            :param option_bar_button: The Option Bar button to click.

            :raises TimeoutException: if the supplied button is not present.
            """
            try:
                self._get_option_bar_button(option_bar_button=option_bar_button).click()
            except TimeoutException as toe:
                raise TimeoutException(
                    msg=f"No {option_bar_button.value} button found among the Option Bar buttons.") from toe

        def click_tag_browser_button(self) -> None:
            """
            Click the button which expands or collapses the Tag Browser panel.

            :raises TimeoutException: If the Tag Browse button is not present.
            """
            try:
                self._tag_browser_button.click()
            except TimeoutException as toe:
                raise TimeoutException(msg="The Tag browse button is not present.") from toe

        def date_range_selector_expansion_icon_is_displayed(self) -> bool:
            """
            Determine if the Date Range selector is displayed.

            :returns: True, if the date range selector is currently displayed - False otherwise.
            """
            return self._date_range_selector.date_range_selector_toggle_icon_is_present()

        def get_historical_range(self) -> HistoricalRange:
            """
            Obtain the applied historical range as an object. Expands the range selector if not already open, and then
            closes the range selector if it was not open to start with.

            :returns: The applied historical range as a HistoricalRange object.
            """
            return self._date_range_selector.get_historical_range()

        def get_date_range_message(self) -> str:
            """
            Obtain the range message associated with the Date Range Selector. This value describes the applied range.
            Example: 'Last 8 hours', or a breakdown of the date/times used for the Historical range.

            :returns: The range message associated with the Date Range Selector, if available.

            :raises TimeoutException: If the Power Chart has made the Date Range Selector invisible.
            """
            return self._date_range_selector.get_range_message()

        def get_title_html_class(self) -> str:
            """
            Obtain the html class attribute for the title of the header.

            :returns: The HTML class attribute for the title of the header of the Power Chart.

            :raises TimeoutException: If the title is not present.
            """
            try:
                return self._title.find().get_attribute(name="class")
            except TimeoutException as toe:
                raise TimeoutException(msg="No title is present in the header of the Power Chart.") from toe

        def get_css_property_value_from_title(self, property_name: Union[CSSPropertyValue, str]) -> str:
            """
            Obtain the value of a CSS property from the title of the header.

            :param property_name: The name of the property you want to value of.

            :returns: The value of the supplied CSS property of the title of the header of the Power Chart.

            :raises TimeoutException: If the title is not present.
            """
            try:
                return self._title.get_css_property(property_name=property_name)
            except TimeoutException as toe:
                raise TimeoutException(msg="No title is present in the header of the Power Chart.") from toe

        def hover_over_option_bar_button(self, option_bar_button: OptionBarButton) -> None:
            """
            Hover over a button of the Option Bar.

            :param option_bar_button: The Option Bar button to hover over.

            :raises TimeoutException: If the supplied Option Bar button is not present.
            """
            try:
                IASelenium(driver=self.driver).hover_over_web_element(
                    web_element=self._get_option_bar_button(option_bar_button=option_bar_button).find())
            except TimeoutException as toe:
                raise TimeoutException(msg=f"No {option_bar_button.value} Option Bar button found.") from toe

        def is_in_responsive_mode(self) -> bool:
            """
            Determine if the Power Chart is displaying in responsive mode.

            :returns: True, if the Power Chart is currently rendering in a responsive layout - False otherwise.
            """
            return "mobile" in self.find().get_attribute(name="class")

        def open_date_range_selector_if_not_displayed(self) -> None:
            """
            Open the date range selector if it is not already displayed. No action is taken if the date range selector
            is already displayed.
            """
            self._date_range_selector.open_date_range_popover_or_modal_if_not_already_displayed()

        def select_date_range_selector_tab(self, tab: DateRangeSelectorTab) -> None:
            """
            Select the supplied tab within the date range selector.

            :param tab: The date range selector tab to click/select.

            :raises TimeoutException: If the date range selector is not present.
            """
            self._date_range_selector.select_tab(tab=tab)

        def select_realtime_unit(self, time_unit: DateRangeSelectorTimeUnit) -> None:
            """
            Select a realtime unit from the date range selector.

            :param time_unit: The unit of time to select.

            :raises TimeoutSelection: If the date range selector is not present.
            """
            self._date_range_selector.select_realtime_unit(time_unit=time_unit)

        def set_historical_day(self, numeric_day: Union[int, str]) -> None:
            """
            Select/click a day within the historical range selector. This requires that the date range selector already
            be displayed and the historical tab is already selected.

            :param numeric_day: The numeric day to click within the historical range.

            :raises TimeoutException: If the historical range selector is not present, or if the supplied day is
                invalid.
            """
            self._date_range_selector.select_date(date=PerspectiveDate(day=numeric_day))

        def set_historical_month(self, month: str) -> None:
            """
            Select a month within the historical range selector. This requires that the date range selector already
            be displayed and the historical tab is already selected.

            :param month: The month to select (eg: "January", not 1).

            :raises TimeoutException: If the historical range selector is not present, or if the supplied month is not
                valid.
            """
            self._date_range_selector.select_date(date=PerspectiveDate(month=int(month)))

        def set_historical_year(self, year: Union[int, str]) -> None:
            """
            Select a year from the dropdown in the Historical Range selector.

            :param year: The year to select.

            :raises TimeoutException: If the Historical Range Selector is not present.
            """
            self._date_range_selector.select_date(date=PerspectiveDate(year=int(year)))

        def set_historical_range_and_apply(self, historical_range: HistoricalRange) -> None:
            """
            Open the date range selector, select values for a historical range, and then apply those changes.

            :param historical_range: The historical range settings to apply, within a HistoricalRange object.

            :raises AssertionError: If unsuccessful in applying the provided historical range.
            :raises TimeoutException: If the date range capabilities of the Power Chart are disabled.
            """
            self.open_date_range_selector_if_not_displayed()
            self.select_date_range_selector_tab(tab=DateRangeSelectorTab.HISTORICAL)
            self._date_range_selector.click_clear_in_historical_tab()
            self._date_range_selector.set_historical_range(historical_range=historical_range, apply=True)

        def set_realtime_numeric_value(self, time_value: int) -> None:
            """
            Set the numeric (scalar) value in use by the realtime range.

            :param time_value: The scalar value to use for the realtime range.

            :raises AssertionError: If unsuccessful in applying the supplied time value.
            """
            self._date_range_selector.set_realtime_range(time_value=time_value)

        def tag_browser_button_is_displayed(self) -> bool:
            """
            Determine if the Tag Browser button is displayed.

            :returns: True if the Tag Browser button is currently displayed - False otherwise.
            """
            try:
                return self._tag_browser_button.find().is_displayed()
            except TimeoutException:
                return False

        def _get_option_bar_button(self, option_bar_button: OptionBarButton) -> ComponentPiece:
            """
            Obtain one of the buttons available from the upper-right of the Power Chart.

            :param option_bar_button: The Option Bar button to obtain.
            """
            _button_comp_piece = self._option_bar_buttons.get(option_bar_button.value)
            if not _button_comp_piece:
                _button_comp_piece = ComponentPiece(
                    locator=(By.ID, f"{self._GENERIC_ICON_STRING}{option_bar_button.value}"),
                    driver=self.driver,
                    parent_locator_list=self.locator_list,
                    description=f"The {option_bar_button.value} button, found in the upper-right of the Power Chart.",
                    poll_freq=self.poll_freq)
                self._option_bar_buttons[option_bar_button.value] = _button_comp_piece
            return _button_comp_piece

    class _PowerChartSettingsPanel(ComponentPiece):
        """
        The settings panel is accessed by clicking the settings button (gear icon) of the Power Chart.
        """
        _SETTINGS_PANEL_LOCATOR = (By.CSS_SELECTOR, "section.ia_powerChartComponent__settings")
        _PEN_ROW_LOCATOR = (By.CSS_SELECTOR, "div.tr")
        _TAB_CONTAINER_LOCATOR = (By.CSS_SELECTOR, "div.tab-container")
        _TAB_ID_GENERIC_STRING = "ia_powerChartComponent__settings__tab__"
        _CHECKBOX_ACTIVE_PATH = "M19 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.11 0 2-.9 2-2V5c0-1.1-.89-2-2-2zm-9 " \
                                "14l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"
        _CLOSE_PANEL_ICON_LOCATOR = (By.ID, "ia_powerChartComponent__icon__closeSettings")
        _UPDATE_PEN_NAME_INPUT_FIELD_LOCATOR = (By.ID, "ia_powerChartComponent__settings__addEditPen__name")
        _UPDATE_PEN_PATH_INPUT_FIELD_LOCATOR = (By.ID, "ia_powerChartComponent__settings__addEditPen__dataSource")
        _DONE_BUTTON_LOCATOR = (
            By.CSS_SELECTOR, ".ia_powerChartComponent__settings__tab__content__buttonContainer .ia_button--primary")
        _DELETION_CANCELLATION_BUTTON_LOCATOR = (By.ID, "ia_powerChartComponent__settings__pensTab__deleteCancelButton")
        _DELETION_CONFIRMATION_BUTTON_LOCATOR = (
            By.ID, "ia_powerChartComponent__settings__pensTab__deleteConfirmButton")
        _VISIBILITY_CHECKBOX_LOCATOR = (By.ID, "ia_powerChartComponent__settings__addEditPen__visible")
        _ENABLED_CHECKBOX_LOCATOR = (By.ID, "ia_powerChartComponent__settings__addEditPen__enabled")
        _CHART_SETTINGS_LINK_LOCATOR = (By.LINK_TEXT, "Chart Settings")
        _NORMAL_STATE_STROKE_COLOR_DROPDOWN_LOCATOR = (
            By.ID, "ia_powerChartComponent__settings__addEditPen__displayStylesnormalStrokeColor")
        _SHARED_COLOR_PICKER_INPUT_LOCATOR = (By.CSS_SELECTOR, "div.ia_colorPickerCommon__modal input")
        _ADD_PEN_LINK_LOCATOR = (By.ID, "ia_powerChartComponent__settings__pensTab__addPenLink")
        # this can be updated once IGN-5498 is merged, new data attribute for the edit axis button will be included
        _DEFAULT_AXIS_EDIT_ICON_LOCATOR = (By.CSS_SELECTOR, 'div.tc.ia_table__cell[data-column-id="edit"] svg')
        _GRID_VISIBLE_CHECKBOX_LOCATOR = (By.ID, 'ia_powerChartComponent__settings__addEditAxis__gridVisible')
        _GRID_COLOR_PICKER_DROPDOWN_LOCATOR = (By.ID, 'ia_powerChartComponent__settings__addEditAxis__gridColor')
        _GRID_OPACITY_TF_LOCATOR = (By.ID, 'ia_powerChartComponent__settings__addEditAxis__gridOpacity')
        _GRID_DASH_ARRAY_TF_LOCATOR = (By.ID, 'ia_powerChartComponent__settings__addEditAxis__gridDashArray')

        def __init__(
                self,
                parent_locator_list: List[Tuple[By, str]],
                driver: WebDriver,
                poll_freq: float = 0.5):
            super().__init__(
                parent_locator_list=parent_locator_list,
                driver=driver,
                locator=self._SETTINGS_PANEL_LOCATOR,
                poll_freq=poll_freq)
            self._pen_rows = ComponentPiece(
                locator=self._PEN_ROW_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="Inside the Pens tab of the Settings Panel, the rows of Tag History Pen names.",
                poll_freq=poll_freq)
            self._tab_container = ComponentPiece(
                locator=self._TAB_CONTAINER_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="Inside the Settings Panel, the container which has tabs for various configuration areas.",
                poll_freq=poll_freq)
            self._close_icon = ComponentPiece(
                locator=self._CLOSE_PANEL_ICON_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The 'X' in the upper-right of the Settings Panel.",
                poll_freq=poll_freq)
            self._update_pen_name_input_field = ComponentPiece(
                locator=self._UPDATE_PEN_NAME_INPUT_FIELD_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The input used to modify the name of the pen currently being edited in the Settings "
                            "Panel.",
                poll_freq=poll_freq)
            self._update_pen_path_input_field = ComponentPiece(
                locator=self._UPDATE_PEN_PATH_INPUT_FIELD_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The input used to modify the path of the pen currently being edited in the Settings "
                            "Panel.",
                poll_freq=poll_freq)
            self._done_button = ComponentPiece(
                locator=self._DONE_BUTTON_LOCATOR,
                driver=driver,
                parent_locator_list=parent_locator_list,
                description="The 'Done' button, found in the bottom right of the Settings Panel while editing a pen",
                poll_freq=poll_freq)
            self._deletion_cancellation_button = ComponentPiece(
                locator=self._DELETION_CANCELLATION_BUTTON_LOCATOR,
                driver=driver,
                parent_locator_list=None,
                description="The 'Cancel' button, which is available after having clicked the trash can icon for a row "
                            "within the Settings Panel.",
                poll_freq=poll_freq)
            self._deletion_confirmation_button = ComponentPiece(
                locator=self._DELETION_CONFIRMATION_BUTTON_LOCATOR,
                driver=driver,
                parent_locator_list=None,
                description="The 'Delete' button, which is available after having clicked the trash can icon for a row "
                            "within the Settings Panel.",
                poll_freq=poll_freq)
            self._visible_checkbox = CommonCheckbox(
                locator=self._VISIBILITY_CHECKBOX_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The checkbox which dictates whether the pen is displayed in the chart.",
                poll_freq=poll_freq)
            self._enabled_checkbox = CommonCheckbox(
                locator=self._ENABLED_CHECKBOX_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The checkbox which dictates whether the pen is hidden from the chart and pen control "
                            "panel.",
                poll_freq=poll_freq)
            self._chart_settings_link = ComponentPiece(
                locator=self._CHART_SETTINGS_LINK_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The breadcrumb within the Settings Panel of the Power Chart, while editing a "
                            "configuration area.",
                poll_freq=poll_freq)
            self._normal_state_stroke_color_dropdown = ComponentPiece(
                locator=self._NORMAL_STATE_STROKE_COLOR_DROPDOWN_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The dropdown/Select used to allow modification for the 'Normal State' style within the "
                            "Settings Panel.",
                poll_freq=poll_freq)
            self._shared_color_modal_input = ComponentPiece(
                locator=self._SHARED_COLOR_PICKER_INPUT_LOCATOR,
                driver=driver,
                parent_locator_list=None,
                description="The color picker text input field shared by any of the color modification dropdowns.",
                poll_freq=poll_freq)
            self._color_picker = ComponentPiece(
                locator=(By.CSS_SELECTOR, "div.saturation-black"),
                driver=driver,
                parent_locator_list=None,
                description="The saturation picker panel itself.",
                poll_freq=poll_freq)
            self._add_pen_link = ComponentPiece(
                locator=self._ADD_PEN_LINK_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The '+ Add Pen' link found beneath the last row in the Pens tab of the Settings Panel.",
                poll_freq=poll_freq)
            self._tab = ComponentPiece(
                locator=(By.ID, f""),  # placeholder, to be replaced within usages.
                driver=driver,
                parent_locator_list=self._tab_container.locator_list,
                description="A specific tab within the Settings Panel - check the declared `id`.",
                poll_freq=poll_freq)
            self._pen_control_column_checkbox = ComponentPiece(
                locator=(By.ID, ""),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                description="The checkboxes within the Columns tab of the Settings Panel which are used to modify "
                            "which columns are displayed in the pen control table.",
                poll_freq=poll_freq)
            self._range_brush_column_checkboxes = {}
            self._pen_visibility_checkboxes = {}
            self._pen_row_visible_checkbox_path = ComponentPiece(
                locator=(By.CSS_SELECTOR, ""),
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The <path> element of the checkbox, which describes the drawn lines of the icon.",
                poll_freq=poll_freq)
            self._tabs = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'div[id^="{self._TAB_ID_GENERIC_STRING}"]'),
                driver=driver,
                parent_locator_list=self._tab_container.locator_list,
                description="Any of the tabs visible within the Settings Panel.",
                poll_freq=poll_freq)
            self._active_tab = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'div[id^="{self._TAB_ID_GENERIC_STRING}"].active'),
                driver=driver,
                parent_locator_list=self._tab_container.locator_list,
                description="The active tab visible within the Settings Panel.",
                poll_freq=poll_freq)
            self._edit_icons_dict = {}
            self._delete_icons_dict = {}
            self._grid_visible_checkbox = CommonCheckbox(
                locator=self._GRID_VISIBLE_CHECKBOX_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The checkbox which drives whether the grid is visible for the axis currently being "
                            "edited in the Settings Panel.",
                poll_freq=poll_freq)
            self._grid_color_picker_dropdown = ComponentPiece(
                locator=self._GRID_COLOR_PICKER_DROPDOWN_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The dropdown which opens up the color picker for the grid of the axis currently being "
                            "edited in the Settings Panel.",
                poll_freq=poll_freq)
            self._grid_opacity = TextField(
                locator=self._GRID_OPACITY_TF_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The text input for grid opacity of the axis currently being edited in the Settings Panel.",
                poll_freq=poll_freq)
            self._grid_dash_array = TextField(
                locator=self._GRID_DASH_ARRAY_TF_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The text input for grid dash array of the axis currently being edited in the Settings "
                            "Panel.",
                poll_freq=poll_freq)
            self._axis_edit_icon = {}

        def cancel_deletion(self) -> None:
            """
            Click the 'Cancel' button during the deletion process.

            :raises TimeoutException: If the 'Cancel' button is not present.
            """
            self._deletion_cancellation_button.click()

        def click_add_pen_link(self) -> None:
            """
            Click the '+ Add Pen' link. Requires that the Settings panel already be open.

            :raises TimeoutException: If the Settings panel is not already open, or if the Pens tab is not present.
            """
            self._add_pen_link.click()

        def click_chart_settings_breadcrumb_link(self) -> None:
            """
            Click the 'Chart Settings' link within the breadcrumb path at the top of the Settings panel.

            :raises TimeoutException: If the Settings panel is nt already open, or if the Chart Settings breadcrumb
                option is not present. This will occur anytime the Chart Settings tabbed area is already displayed.
            """
            self._chart_settings_link.click()

        def click_done(self) -> None:
            """
            Click the Done button.

            :raises TimeoutException: If the 'Done' button is not present.
            """
            self._done_button.click()

        def click_point_in_color_picker(self) -> None:
            """
            Click the color picker displayed while editing any of the color settings for a pen. Requires that the
            picker already be visible as a result of clicking any of the available color dropdown items. Note that
            Selenium does not properly handle offsets for the color picker modal, so this function has limited use.

            :raises TimeoutException: If the color picker is not present.
            """
            # TODO: Figure out why offsets don't work here
            ActionChains(driver=self.driver)\
                .move_to_element(
                    to_element=self._color_picker.find()
                )\
                .click()\
                .pause(1)\
                .perform()

        def click_normal_state_stroke_color_dropdown(self) -> None:
            """
            Click the dropdown for the stroke color in the 'Normal State' section of the pen.

            :raises TimeoutException: if not currently in the pen editing section of the Settings panel.
            """
            self._normal_state_stroke_color_dropdown.click()

        def click_tab(self, tab: Tab) -> None:
            """
            Click a tab of the Settings panel. Requires that the Settings panel already be open.

            :param tab: The tab to click.

            :raises TimeoutException: If the supplied tab is not present.
            """
            self._tab.set_locator(new_locator=(By.ID, f"{self._TAB_ID_GENERIC_STRING}{tab.value.lower()}"))
            self._tab.click()
            IAAssert.is_true(
                value=self.tab_is_active(tab=tab),
                failure_msg=f"Failed to select the {tab.value} tab.")

        def close_settings_panel(self) -> None:
            """
            Close the Settings panel.

            :raises AssertionError: If unsuccessful in closing the Settings panel.
            """
            if self.is_displayed():
                try:
                    self.click_chart_settings_breadcrumb_link()
                except TimeoutException:
                    pass
                try:
                    self._close_icon.click()
                except TimeoutException:
                    pass
            IAAssert.is_not_true(
                value=self.is_displayed(),
                failure_msg="Failed to close the Settings panel.")

        def confirm_deletion(self) -> None:
            """
            Click the 'Delete' button available during the process of deleting a pen.

            :raises TimeoutException: If the 'Delete' button is not present.
            """
            self._deletion_confirmation_button.click()

        def click_trash_can_icon_for_pen(self, pen_name: str) -> None:
            """
            Click the trash can icon for a specific pen. Note that this only begins the deletion process, and that there
            are further actions to take after this.

            :param pen_name: The name of the pen you would like to begin the deletion process for.

            :raises TimeoutException: If the trash can icon is not present. This might be due to no pen with the
                supplied name being present.
            """
            self._get_delete_icon_by_pen_name(pen_name=pen_name).click()

        def _get_delete_icon_by_pen_name(self, pen_name: str) -> ComponentPiece:
            """
            Obtain the trash can icon from the Tag History Pens tab for the supplied pen.

            :param pen_name: The name of the pen to target.
            """
            _icon = self._delete_icons_dict.get(pen_name)
            if not _icon:
                _icon = ComponentPiece(
                    locator=(
                        By.CSS_SELECTOR,
                        f'svg[id^="ia_powerChartComponent__settings__pensTab__deleteIcon"][data-pen-name="{pen_name}"'),
                    driver=self.driver,
                    parent_locator_list=self.locator_list,
                    description=f"The trash can icon for the '{pen_name}' pen in the Pens tab of the Settings Panel.",
                    poll_freq=self.poll_freq)
                self._delete_icons_dict[pen_name] = _icon
            return _icon

        def click_pencil_icon_for_pen(self, pen_name: str) -> None:
            """
            Click the pencil icon for a specific pen. Note that this only begins the editing process, and that there
            are further actions to take after this.

            :param pen_name: The name of the pen you would like to begin the editing process for.

            :raises TimeoutException: If the pencil icon is not present. This might be due to no pen with the
                supplied name being present.
            """
            self._get_edit_icon_by_pen_name(pen_name=pen_name).click()

        def _get_edit_icon_by_pen_name(self, pen_name: str) -> ComponentPiece:
            """
            Obtain the pencil icon from the Tag History Pens tab for the supplied pen.

            :param pen_name: The name of the pen to target.
            """
            _icon = self._edit_icons_dict.get(pen_name)
            if not _icon:
                _icon = ComponentPiece(
                    locator=(
                        By.CSS_SELECTOR,
                        f'svg[id^="ia_powerChartComponent__settings__pensTab__editIcon"][data-pen-name="{pen_name}"'),
                    driver=self.driver,
                    parent_locator_list=self.locator_list,
                    description=f"The pencil icon for the '{pen_name}' pen in the Pens tab of the Settings Panel.",
                    poll_freq=self.poll_freq)
                self._edit_icons_dict[pen_name] = _icon
            return _icon

        def get_current_color_from_picker(self) -> str:
            """
            Obtain the color in use for whichever setting is currently being modified, as a string. Note that as this
            value is coming from a prop it will always be hex.

            :returns: The color currently applied as a hex string.

            :raises TimeoutException: If the color picker and its accompanying inputs are not present.
            """
            return self._shared_color_modal_input.find().get_attribute("value")

        def get_count_of_displayed_pens(self) -> int:
            """
            Obtain a count of how many pens are currently listed in the Pens tab of the Settings panel. Requires that
            the Settings panel already be displayed and the Pens tab be selected.

            :returns: A numeric count of the pens listed in the Pens tab of the Settings Panel.
            """
            try:
                return len(self._pen_rows.find_all())
            except TimeoutException:
                return 0

        def get_displayed_pen_names(self) -> List[str]:
            """
            Obtain a list of all pen names displayed in the Pens tab of the Settings panel. Requires that the Settings
            panel already be displayed and the Pens tab be selected.

            :returns: A list which contains all pen names displayed in the Pens tab of the Settings panel.
            """
            try:
                return [_.text for _ in self._pen_rows.find_all()]
            except TimeoutException:
                return []

        def get_displayed_tab_names(self) -> List[str]:
            """
            Obtain the name sof all tabs listed in the Settings panel. Requires that the Settings panel already be
            displayed.

            :returns: A list which contains the names of all tabs displayed in the Settings panel.

            :raises TimeoutException: If the Settings panel is not already open, or if the Settings panel is not
                currently at the level which displays the tabbed layout.
            """
            return [_.text for _ in self._tabs.find_all()]

        def get_pen_name(self) -> str:
            """
            Obtain the name of the pen as displayed in the Settings panel.

            :returns: The text contents of the name field within the Settings panel.

            :raises TimeoutException: If the Settings panel is not present.
            """
            return self._update_pen_name_input_field.find().get_attribute("value")

        def is_displayed(self) -> bool:
            """
            Determine if the Settings panel is displayed.

            :returns: True, if the Settings panel is currently open/displayed/expanded - False otherwise.
            """
            try:
                return self.find(wait_timeout=1).is_displayed() and "expanded" in self.find().get_attribute("class")
            except TimeoutException:
                return False

        def pen_settings_are_displayed(self) -> bool:
            """
            Determine if the Pen settings panel is displayed.

            :returns: True, if the inputs used to edit a pen are currently displayed - False otherwise.
            """
            try:
                return self._update_pen_name_input_field.find(wait_timeout=1) is not None
            except TimeoutException:
                return False

        def set_pen_control_column_display_state_in_settings_panel(
                self,
                pen_control_column: PenControlColumn,
                should_be_displayed: bool) -> None:
            """
            Set the display state of a column within the pen control table. Requires the Settings panel already be
            displayed.

            :param pen_control_column: The column which will have its state set.
            :param should_be_displayed: If True, the column will be set to display - otherwise the column will be set to
                not be displayed.

            :raises TimeoutException: If the Settings panel is not already displayed.
            """
            self.click_tab(tab=Tab.COLUMNS)
            self._pen_control_column_checkbox.set_locator(
                new_locator=(
                    By.ID, f"ia_powerChartComponent__settings__columnsTab__penControl.{pen_control_column.value}"))
            self._special_checkbox_handling(
                checkbox_component_piece=self._pen_control_column_checkbox, should_be_checked=should_be_displayed)

        def set_range_brush_column_display_state_in_settings_panel(
                self,
                range_brush_column: RangeBrushColumn,
                should_be_displayed: bool) -> None:
            """
            Set the display state of a column within the range brush table. Requires the Settings panel already be
            displayed.

            :param range_brush_column: The column which will have its state set.
            :param should_be_displayed: If True, the column will be set to display - otherwise the column will be set to
                not be displayed.

            :raises TimeoutException: If the Settings panel is not already displayed.
            """
            self.click_tab(tab=Tab.COLUMNS)
            self._special_checkbox_handling(
                checkbox_component_piece=self._get_range_brush_checkbox(range_brush_column=range_brush_column),
                should_be_checked=should_be_displayed)

        def set_display_checkbox_state_by_pen_name(self, pen_name: str, should_be_checked: bool) -> None:
            """
            Set the display state of a pen listed in the Pens tab of the Settings panel. Requires the Settings panel
            already be displayed, and that the pen tab be displayed.

            :param pen_name: The name of the pen which will have its state set.
            :param should_be_checked: If True, the pen will be set to display - otherwise, the pen will be set to not
                display.

            :raises TimeoutException: If the Settings panel is not already displayed.
            """
            # requires special handling due to use of uncommon checkbox.
            if (self._get_pen_visibility_checkbox(
                    pen_name=pen_name).find().get_attribute('data-state') == "checked") != should_be_checked:
                self._get_pen_visibility_checkbox(pen_name=pen_name).click()

        def set_pen_display_state_in_settings_panel(self, should_be_checked: bool) -> None:
            """
            Set the display state of a pen while the pen is being edited. This function expects that a pen is already
            being edited.

            :param should_be_checked: If True, the pen will be set to display - otherwise, the pen will be set to not
                display.

            :raises TimeoutException: If the Settings panel is not already displayed, or if we are not already editing
                a pen.
            """
            self._special_checkbox_handling(
                checkbox_component_piece=self._visible_checkbox, should_be_checked=should_be_checked)

        def set_pen_enabled_state_in_settings_panel(self, should_be_enabled: bool) -> None:
            """
            Set the enabled state of a checkbox. The wording in the Power Chart is actually to "hide" the pen from the
            chart, so we reverse that logic inside this function. Requires that a pen already be in an "editing" state.

            :param should_be_enabled: If True, the pen will NOT be hidden - otherwise we will set the pen to be hidden.

            :raises TimeoutException: If the Settings panel is not already visible, or if a pen is not already being
                edited.
            """
            # This is counter-intuitive, but the checkbox is actually to "hide" the pen - so reverse the logic here.
            self._special_checkbox_handling(
                checkbox_component_piece=self._enabled_checkbox, should_be_checked=not should_be_enabled)

        @classmethod
        def _special_checkbox_handling(cls, checkbox_component_piece: ComponentPiece, should_be_checked: bool) -> None:
            """
            Perform one-off handling of checkboxes within the Power Chart.

            :param checkbox_component_piece: The ComponentPiece (not Checkbox) which defines the checkbox.
            :param should_be_checked: A True value dictates the checkbox should have an active (checked) state.

            :raises TimeoutException: If the checkbox can not be found.
            """
            svg = checkbox_component_piece.find().find_element(By.XPATH, '../*[name()="svg"]')
            if (svg.get_attribute("data-state") == "checked") != should_be_checked:
                svg.click()

        def set_pen_name_field(self, updated_pen_name: str) -> None:
            """
            Set the name of a pen during editing.

            :param updated_pen_name: The desired pen name.

            :raises AssertionError: If unsuccessful in editing the name of the pen.
            :raises TimeoutException: If the Settings panel is not already visible, or if a pen is not already being
                edited.
            """
            current_text = self._update_pen_name_input_field.find().get_attribute("value")
            self._update_pen_name_input_field.click()
            self._update_pen_name_input_field.find().send_keys(
                ''.join(
                    [Keys.ARROW_LEFT for _ in current_text] +
                    [updated_pen_name] +
                    [Keys.DELETE for _ in current_text]))
            IAAssert.is_equal_to(
                actual_value=self._update_pen_name_input_field.find().get_attribute("value"),
                expected_value=updated_pen_name,
                failure_msg="Failed to modify the name of the pen while editing in the Settings panel.")

        def set_pen_path_field(self, updated_pen_path: str) -> None:
            """
            Set the path of a pen during editing.

            :param updated_pen_path: The desired pen path to use.

            :raises AssertionError: If unsuccessful in editing the path of the pen.
            :raises TimeoutException: If the Settings panel is not already visible, or if a pen is not already being
                edited.
            """
            current_text = self._update_pen_path_input_field.find().get_attribute("value")
            self._update_pen_path_input_field.click()
            self._update_pen_path_input_field.find().send_keys(
                ''.join(
                    [Keys.ARROW_LEFT for _ in current_text] +
                    [updated_pen_path] +
                    [Keys.DELETE for _ in current_text]))
            IAAssert.is_equal_to(
                actual_value=self._update_pen_path_input_field.find().get_attribute("value"),
                expected_value=updated_pen_path,
                failure_msg="Failed to modify the path of the pen while editing in the Settings panel.")

        def set_pen_stroke_color(self, hex_desired_color: str) -> None:
            """
            Set the stroke color of a pen during editing.

            :param hex_desired_color: The color to use for the stroke of the pen, in hex format.

            :raises AssertionError: If unsuccessful in editing the stroke color of the pen.
            :raises TimeoutException: If the Settings panel is not already visible, or if a pen is not already being
                edited.
            """
            self._normal_state_stroke_color_dropdown.click()
            current_text = self._shared_color_modal_input.find().get_attribute("value")
            self._shared_color_modal_input.find().send_keys(
                ''.join(
                    [Keys.ARROW_LEFT for _ in current_text] +
                    [hex_desired_color] +
                    [Keys.DELETE for _ in current_text]))
            IAAssert.is_equal_to(
                actual_value=self._shared_color_modal_input.find().get_attribute("value"),
                expected_value=hex_desired_color,
                failure_msg="Failed to modify the stroke of the pen while editing in the Settings panel.")

        def tab_is_active(self, tab: Tab) -> bool:
            """
            Determine if a tab is actively in use.

            :param tab: The tab to check for.

            :returns: True, if the supplied tab is currently the active tab in use - False otherwise.

            raises TimeoutException: If the Settings panel is not already open, or if the Settings panel is not
                currently on the main tabbed layout section.
            """
            return self._active_tab.find().get_attribute(name="data-category") == tab.value.lower()

        def _get_range_brush_checkbox(self, range_brush_column: RangeBrushColumn) -> ComponentPiece:
            """
            Obtain a checkbox from the range brush section of the Columns tab.

            :param range_brush_column: The column for which you would like the checkbox.
            """
            _checkbox = self._range_brush_column_checkboxes.get(range_brush_column.value)
            if not _checkbox:
                _checkbox = ComponentPiece(
                    locator=(
                        By.ID,
                        f"ia_powerChartComponent__settings__columnsTab__rangeSelection.{range_brush_column.value}"),
                    driver=self.driver,
                    parent_locator_list=self.locator_list,
                    description=f"The {range_brush_column.value} checkbox within the Range Brush section of the "
                                f"Columns tab of the Settings Panel.",
                    poll_freq=self.poll_freq
                )
                self._range_brush_column_checkboxes[range_brush_column.value] = _checkbox
            return _checkbox

        def _get_pen_visibility_checkbox(self, pen_name: str) -> ComponentPiece:
            """
            Obtain the visibility checkbox for a row in the Pens tab of the Settings panel.

            :param pen_name: The name of the pen for which you would like the visibility checkbox.
            """
            _checkbox = self._pen_visibility_checkboxes.get(pen_name)
            if not _checkbox:
                _checkbox = ComponentPiece(
                    locator=(By.CSS_SELECTOR, f'svg[data-pen-name="{pen_name}"]'),
                    driver=self.driver,
                    parent_locator_list=self.locator_list,
                    description=f"The visibility checkbox to the left of the '{pen_name}' pen within the Pens tab of "
                                f"the Settings Panel,",
                    poll_freq=self.poll_freq)
                self._pen_visibility_checkboxes[pen_name] = _checkbox
            return _checkbox

        @classmethod
        def _click_checkbox_svg(cls, checkbox: ComponentPiece) -> bool:
            """
            Click the <svg> of a checkbox and report back on the success of the click.

            :param checkbox: The ComponentPiece which defines the checkbox.

            :returns: True, if the click event was successful - False otherwise.

            :raises TimeoutException: if the checkbox could not be found.
            """
            try:
                checkbox.find().find_element(By.XPATH, '../*[name()="svg"]').click()
                return True
            except StaleElementReferenceException:
                return False

        def click_pencil_icon_for_axis(self, axis_name: str) -> None:
            """
            Click the pencil (edit) icon for an axis.

            :param axis_name: The name of the axis to begin editing.

            :raises TimeoutException: If no row matching the supplied axis name is present.
            """
            _icon = self._axis_edit_icon.get(axis_name)
            if not _icon:
                _icon = ComponentPiece(
                    locator=(
                        By.CSS_SELECTOR,
                        f'[data-column-id="edit"] div [data-axis-name="{axis_name}"]'),
                    driver=self.driver,
                    parent_locator_list=self.locator_list,
                    description=f"The pencil icon for the '{axis_name}' axis row within the Axes tab of the Settings "
                                f"Panel.",
                    poll_freq=self.poll_freq)
                self._axis_edit_icon[axis_name] = _icon
            _icon.click()

        def set_grid_visible_checkbox_state(self, should_be_checked: bool) -> None:
            """
            Set the display state of the grid for the axis currently being edited.

            :param should_be_checked: If True, the checkbox will be set to active/checked - otherwise the checkbox will
                be set to inactive/un-checked.

            :raises TimeoutException: If the Settings panel is not already displayed, or an axis is not already being
                edited.
            """
            self._special_checkbox_handling(
                checkbox_component_piece=self._grid_visible_checkbox, should_be_checked=should_be_checked)

        def set_grid_y_axis_color(self, hex_desired_color: str) -> None:
            """
            Set the Y-axis color to be used by the grid for the axis currently being edited.

            :param hex_desired_color: The color (in hex format) to use for the Y-axis of the grid.

            :raises AssertionError: If unsuccessful in modifying the color in use by the Y-axis of the grid.
            :raises TimeoutException: If the Settings panel is not already displayed, or an axis is not already being
                edited.
            """
            self._grid_color_picker_dropdown.click()
            current_text = self._shared_color_modal_input.find().get_attribute("value")
            self._shared_color_modal_input.find().send_keys(
                ''.join(
                    [Keys.ARROW_LEFT for _ in current_text] +
                    [hex_desired_color] +
                    [Keys.DELETE for _ in current_text]))
            IAAssert.is_equal_to(
                actual_value=self._shared_color_modal_input.find().get_attribute("value"),
                expected_value=hex_desired_color,
                failure_msg="Failed to set the color of the Y-axis of the grid while editing an axis.")

        def set_grid_y_axis_opacity(self, value: Union[float, str]) -> None:
            """
            Set the Y-axis opacity to be used by the grid for the axis currently being edited.

            :param value: The desired value (0<=value<=1) to use for the opacity of the Y-axis of the grid.

            :raises AssertionError: If unsuccessful in modifying the opacity in use by the Y-axis of the grid.
            :raises TimeoutException: If the Settings panel is not already displayed, or an axis is not already being
                edited.
            """
            self._grid_opacity.set_text(text=value)
            IAAssert.is_equal_to(
                actual_value=self._grid_opacity.wait_on_text_condition(
                    text_to_compare=value, condition=TextCondition.EQUALS),
                expected_value=value,
                as_type=str,
                failure_msg="Failed to set the opacity of the Y-axis of the grid while editing an axis.")

        def set_grid_y_axis_dash_array(self, value: str) -> None:
            """
            Set the Y-axis dash-array to be used by the grid for the axis currently being edited.

            :param value: The desired value to use for the dash-array of the Y-axis of the grid.

            :raises AssertionError: If unsuccessful in modifying the dash-array in use by the Y-axis of the grid.
            :raises TimeoutException: If the Settings panel is not already displayed, or an axis is not already being
                edited.
            """
            self._grid_dash_array.set_text(text=value)
            IAAssert.is_equal_to(
                actual_value=self._grid_dash_array.wait_on_text_condition(
                    text_to_compare=value, condition=TextCondition.EQUALS),
                expected_value=value,
                as_type=str,
                failure_msg="Failed to set the dash-array of the Y-axis of the grid while editing an axis.")

    class _PowerChartTable(CommonTable):
        """
        The pen control table of the Power Chart.
        """
        _PEN_CHECKBOX_SVG_CHECKED = \
            'M19 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.11 0 2-.9 2-2V5c0-1.1-.89-2-2-2zm-9 ' \
            '14l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z'
        _EXPAND_COLLAPSE_ICON_LOCATOR_GENERIC_STRING = "ia_powerChartComponent__penDataDisplay__table__icon"
        _PEN_TABLE_COLLAPSE_ICON_LOCATOR = (
            By.CSS_SELECTOR, f'svg.{_EXPAND_COLLAPSE_ICON_LOCATOR_GENERIC_STRING}.collapse-icon')
        _PEN_TABLE_EXPAND_ICON_LOCATOR = (
            By.CSS_SELECTOR, f'svg.{_EXPAND_COLLAPSE_ICON_LOCATOR_GENERIC_STRING}.expand-icon')
        _DELETE_PEN_ICON_LOCATOR = (By.CSS_SELECTOR, "svg.delete-pen-icon")
        _EDIT_PEN_ICON_LOCATOR = (By.CSS_SELECTOR, "svg.edit-pen-icon")
        _PEN_TABLE_BODY_LOCATOR = (By.CSS_SELECTOR, "div.tb")
        _UNFORMATTED_PEN_VISIBILITY_CHECKBOX_SELECTOR_STRING = 'svg.pen-visibility-checkbox[data-pen-name="{0}"]'
        _TABLE_HEADER_LOCATOR = (By.CSS_SELECTOR, 'div.tr.header')
        _CONFIRM_DELETION_BUTTON_LOCATOR = (
            By.CSS_SELECTOR, "button#ia_powerChartComponent__settings__pensTab__deleteConfirmButton")

        def __init__(
                self,
                parent_locator_list: List[Tuple[By, str]],
                driver: WebDriver,
                poll_freq: float = 0.5):
            super().__init__(
                parent_locator_list=parent_locator_list,
                driver=driver,
                locator=(By.CSS_SELECTOR, 'div.pen-control-container'),
                description="The pen control table found at the bottom of the Power Chart.",
                poll_freq=poll_freq)
            self._collapse_icon = ComponentPiece(
                locator=self._PEN_TABLE_COLLAPSE_ICON_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The arrow pointing down - and located in the upper-left of the pen control table - which "
                            "allows for collapsing the pen control table. Present only while the pen control table is "
                            "expanded.",
                poll_freq=poll_freq)
            self._pen_table_body = ComponentPiece(
                locator=self._PEN_TABLE_BODY_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The body of the pen control table.",
                poll_freq=poll_freq)
            self._expand_icon = ComponentPiece(
                locator=self._PEN_TABLE_EXPAND_ICON_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The arrow pointing up - and located to the left of all displayed pen names - which "
                            "allows for expanding the pen control table. Present only while the pen control table is "
                            "collapsed.",
                poll_freq=poll_freq)
            self._delete_pen_icon = ComponentPiece(
                locator=self._DELETE_PEN_ICON_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The trash can icon visible only while hovering over a pen row in the pen control table.",
                poll_freq=poll_freq)
            self._edit_pen_icon = ComponentPiece(
                locator=self._EDIT_PEN_ICON_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The pencil icon visible only while hovering over a pen row in the pen control table.",
                poll_freq=poll_freq)
            self._confirm_deletion_button = ComponentPiece(
                locator=self._CONFIRM_DELETION_BUTTON_LOCATOR,
                driver=driver,
                parent_locator_list=None,
                description="The 'Delete' button visible after having clicked the trash can icon for a row in the "
                            "pen control table.",
                poll_freq=poll_freq)
            self._pen_checkbox = ComponentPiece(
                locator=(By.CSS_SELECTOR, f''),  # placeholder, to be overwritten with local pen name
                driver=self.driver,
                parent_locator_list=self._pen_table_body.locator_list,
                description="The checkbox which drives whether a given pen is displayed in the graph.",
                poll_freq=poll_freq)
            self._pen_control_columns = {}
            self._range_brush_columns = {}
            self._pen_table_expand_collapse_svg = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'svg[class*="{self._EXPAND_COLLAPSE_ICON_LOCATOR_GENERIC_STRING}"]'),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                description="The generic expand OR collapse svg definition; this could refer to either.",
                poll_freq=poll_freq)
            self._pen_labels = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'span.pen-name'),
                driver=self.driver,
                parent_locator_list=self._pen_table_body.locator_list,
                description="The labels which contain the names of pens within the pen control table.",
                poll_freq=poll_freq)
            self._pen_overlay = ComponentPiece(
                locator=(By.CSS_SELECTOR, '.overlay-shown'),
                driver=self.driver,
                parent_locator_list=self._pen_table_body.locator_list,
                description="The overlay displayed when a pen is faulted.",
                poll_freq=poll_freq)
            self._pen_control_table_cells_dict = {}

        def click_pen_checkbox_by_name(self, pen_name: str) -> None:
            """
            Click the checkbox for a pen listed in the pen control table.

            :param pen_name: The name of the pen for which you would like to click the accompanying checkbox.

            :raises TimeoutException: If no pen with the supplied name is present.
            """
            self._pen_checkbox.set_locator(
                new_locator=(
                    By.CSS_SELECTOR, self._UNFORMATTED_PEN_VISIBILITY_CHECKBOX_SELECTOR_STRING.format(pen_name)))
            self._pen_checkbox.click()

        def click_pencil_icon_for_pen(self, pen_name: str) -> None:
            """
            Click the pencil icon for a pen in the pen control table.

            :param pen_name: The name of the pen for which you would like to click the accompanying pencil icon.

            :raises IndexError: If no pen with the supplied name could be found.
            """
            pen_label_web_element = list(
                filter(
                    lambda e: e.text == pen_name,
                    self._pen_labels.find_all(
                        wait_timeout=1)))[0]
            IASelenium(
                driver=self.driver).hover_over_web_element(
                web_element=pen_label_web_element)
            self._edit_pen_icon.set_locator(
                new_locator=(By.CSS_SELECTOR, "div.tr.hovering svg.edit-pen-icon"))
            self._edit_pen_icon.click()

        def get_all_pen_names_from_pen_table(self) -> List[str]:
            """
            Obtain the names of all pens displayed in the pen control table.

            :returns: A list which contains the name of every pen displayed in the pen control table.

            :raises TimeoutException: If the pen control table is not present.
            """
            row_count = self.get_count_of_rows()
            pen_names = []
            for i in range(row_count):
                pen_names.append(self.get_row_data_by_row_index(zero_based_row_index=i)['penName'])
            return pen_names

        def get_count_of_pen_fault_overlays(self) -> int:
            """
            Obtain a count of how many pens are currently displaying fault overlays.

            :returns: A count of how many pens are currently displaying fault overlays.
            """
            try:
                return len(self._pen_overlay.find_all())
            except TimeoutException:
                return 0

        def get_column_headers_from_pen_table(self) -> List[str]:
            """
            Obtain the headers of the columns displayed in the pen control table. Ignores the selection column, as it
            contains no header text.

            :returns: A list which contains the header of every column currently displayed in the pen control table.

            :raises TimeoutException: If no pen control table is present.
            """
            return self.get_column_names_from_header()[1:]  # omit selection column

        def get_count_of_available_pens_from_pen_table(self) -> int:
            """
            Obtain a count of all pens listed in the pen control table.

            :returns: A count of every pen displayed in the pen control table.

            :raises TimeoutException: If the pen control table is not present.
            """
            return len(self.get_all_pen_names_from_pen_table())

        def get_pen_checkbox_color(self, pen_name: str) -> str:
            """
            Obtain the color in use for a given pen. This color will always be the same as the line which is graphed.

            :param pen_name: The name of the pen for which you would like the color of the accompanying checkbox.

            :returns: The color in use by the checkbox of a pen.

            :raises TimeoutException: If no pen with the supplied name is present in the pen control table, or if the
                pen control table is not present.
            """
            self._pen_checkbox.set_locator(
                new_locator=(
                    By.CSS_SELECTOR,
                    f'{self._UNFORMATTED_PEN_VISIBILITY_CHECKBOX_SELECTOR_STRING.format(pen_name)} > path'))
            return self._pen_checkbox.get_css_property(property_name=CSS.FILL)

        def pen_checkbox_is_active(self, pen_name: str) -> bool:
            """
            Determine if the checkbox of a pen is active (selected and/or checked are synonymous with active).

            :param pen_name: The name of the pen for which we will check the accompanying checkbox.

            :returns: True, if the checkbox for the specified pen is active/selected/checked.

            :raises TimeoutException: If no pen with the supplied name is present in the pen control table, or if the
                pen control table is not present.
            """
            self._pen_checkbox.set_locator(
                new_locator=(
                    By.CSS_SELECTOR,
                    f'{self._UNFORMATTED_PEN_VISIBILITY_CHECKBOX_SELECTOR_STRING.format(pen_name)} > path'))
            return self._pen_checkbox.find().get_attribute('d') == self._PEN_CHECKBOX_SVG_CHECKED

        def get_row_data_by_row_index(self, zero_based_row_index: int) -> dict:
            """
            Obtain the data of a specified row and return that data as a dictionary, where the keys of the dictionary
            are the column names.

            :param zero_based_row_index: The zero-based index of the row you are targeting.

            :returns: The row data as a dictionary, with the keys of the dictionary being the case-sensitive names of
                the columns.
            """
            row_data_as_dictionary = {}
            for cell in self._get_cell_components_by_row_index(zero_based_row_index=zero_based_row_index).find_all():
                row_data_as_dictionary[cell.get_attribute('data-column-id')] = cell.text
            row_data_as_dictionary.pop('toggle', None)
            return row_data_as_dictionary

        def _get_cell_components_by_row_index(self, zero_based_row_index: int) -> ComponentPiece:
            """
            Obtain a ComponentPiece which describes how to locate the cells of a row of the pen control table.

            :param zero_based_row_index: The zero-based index of the row these 'cells' would belong to.
            """
            cells = self._pen_control_table_cells_dict.get(zero_based_row_index)
            if not cells:
                cells = ComponentPiece(
                    locator=(By.CSS_SELECTOR, f'div.tr[data-row-index="{zero_based_row_index}"] div.tc'),
                    driver=self.driver,
                    parent_locator_list=self.locator_list,
                    description=f"The cells from the {zero_based_row_index}th row in the pen control table.",
                    poll_freq=self.poll_freq)
                self._pen_control_table_cells_dict[zero_based_row_index] = cells
            return cells

        def pen_control_column_is_displayed(
                self, pen_control_column: Union[PenControlColumn, RangeBrushColumn]) -> bool:
            """
            Determine if a pen control column is displayed.

            :param pen_control_column: The pen control column or range brush column to check for the presence of.

            :returns: True, if the supplied column is displayed - False otherwise.
            """
            try:
                return self._get_pen_control_table_column(pen_control_column=pen_control_column).find(1) is not None
            except TimeoutException:
                return False

        def _get_pen_control_table_column(
                self, pen_control_column: Union[PenControlColumn, RangeBrushColumn]):
            pen_control_column = pen_control_column.value
            _column = self._pen_control_columns.get(pen_control_column)
            if not _column:
                _column = ComponentPiece(
                    locator=(By.CSS_SELECTOR, f'div.thc[data-column-id="{pen_control_column}"]'),
                    driver=self.driver,
                    parent_locator_list=self.locator_list,
                    description=f"The '{pen_control_column}' column from the pen control table of the Power Chart.",
                    poll_freq=self.poll_freq)
                self._pen_control_columns[pen_control_column] = _column
            return _column

        def pen_table_is_expanded(self) -> bool:
            """
            Determine if the pen control table is expanded.

            :returns: True, if the pen control table is currently expanded - False otherwise.
            """
            try:
                return (self.find() is not None) \
                       and ("collapse-icon" in self._pen_table_expand_collapse_svg.find().get_attribute("class"))
            except TimeoutException:
                return False

        def range_brush_column_is_displayed(self, range_brush_column: RangeBrushColumn) -> bool:
            """
            Determine if a range brush column is displayed in the pen control table.

            :param range_brush_column: The range brush column for which we will check the display state.

            :returns: True, if the supplied range brush column is displayed - False otherwise.
            """
            return self.pen_control_column_is_displayed(pen_control_column=range_brush_column)

        def remove_pen_by_name(self, pen_name: str) -> None:
            """
            Remove a pen from the pen control table (and therefore the Power Chart) via the pen control table.

            :param pen_name: The name of the pen you would like to remove.

            :raises AssertionError: If unsuccessful in removing the supplied pen from the Power Chart.
            :raises TimeoutException: If the pen control table is not present.
            """
            try:
                pen_label_web_element = list(filter(
                    lambda e: e.text == pen_name, self._pen_labels.find_all(wait_timeout=1)))[0]
                IASelenium(driver=self.driver).hover_over_web_element(web_element=pen_label_web_element)
                self._delete_pen_icon.set_locator(new_locator=(By.CSS_SELECTOR, "div.tr.hovering svg.delete-pen-icon"))
                self._delete_pen_icon.click()
                self._confirm_deletion_button.click()
            except IndexError:
                # no pen with name in controls
                pass
            IAAssert.does_not_contain(
                iterable=self.get_all_pen_names_from_pen_table(),
                expected_value=pen_name,
                failure_msg=f"The '{pen_name}' pen was still present in the pen control table after we attempted to "
                            f"remove it.")

        def set_pen_visibility_on_pen_table(self, pen_name: str, should_be_visible: bool) -> None:
            """
            Set the display state (visibility) of a pen via the pen control table by interacting with the associated
            checkbox.

            :param pen_name: The name of the pen which you would like to set the display state of.
            :param should_be_visible: If True, the checkbox will be set to active/selected/checked - otherwise the
                checkbox will be set to inactive/unselected/un-checked.

            :raises AssertionError: If unsuccessful in setting the display state of the specified checkbox.
            :raises TimeoutException: if no pen with the supplied name is present, or if the pen control table is not
                present.
            """
            if self.pen_checkbox_is_active(pen_name=pen_name) != should_be_visible:
                self.click_pen_checkbox_by_name(pen_name=pen_name)
            IAAssert.is_equal_to(
                actual_value=self.pen_checkbox_is_active(pen_name=pen_name),
                expected_value=should_be_visible,
                failure_msg=f"Failed to set the display state (visibility) of the '{pen_name}' pen "
                            f"to {should_be_visible}.")

        def toggle_pen_table_display(self) -> None:
            """
            Toggle the pen control table expansion state.

            :raises TimeoutException: If the expand/collapse toggle icon is not present.
            """
            try:
                self._collapse_icon.click()
                self._expand_icon.find(wait_timeout=1)
            except TimeoutException:
                try:
                    self._expand_icon.click()
                    self._collapse_icon.find(wait_timeout=1)
                except TimeoutException as toe:
                    raise TimeoutException(
                        msg=f'Pen table collapse/expand icons could not be located for interaction.') from toe

    class _PowerChartTagBrowser(CommonTagBrowseTree):
        """
        The Tag Browse Tree built into the Power Chart.
        """
        _ADD_TAG_BUTTON_LOCATOR = (By.CSS_SELECTOR, '.ia_button--primary')
        _CLOSE_ICON_LOCATOR = (By.ID, 'ia_powerChartComponent__tagBrowserContainer__closeIcon')
        _TAG_BROWSER_LOCATOR = (By.CSS_SELECTOR, 'div.ia_powerChartComponent__tagBrowserContainer')
        _TAG_BROWSER_OPEN_ICON_LOCATOR = (By.CSS_SELECTOR, 'span.show-tag-browser-icon')
        _RELOAD_ICON_LOCATOR = (By.ID, 'ia_powerChartComponent__tagBrowserContainer__reloadIcon')

        def __init__(
                self,
                parent_locator_list: List[Tuple[By, str]],
                driver: WebDriver,
                poll_freq: float = 0.5):
            super().__init__(
                locator=self._TAG_BROWSER_LOCATOR,
                driver=driver,
                parent_locator_list=parent_locator_list,
                description="The Tag Browse Tree of the Power Chart.",
                poll_freq=poll_freq)
            self._add_tag_button = CommonButton(
                locator=self._ADD_TAG_BUTTON_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The 'Add Selected Tags' button at the bottom of the Tag Browse Tree.",
                poll_freq=poll_freq)
            self._close_icon = ComponentPiece(
                locator=self._CLOSE_ICON_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The arrow pointing left - and located in the upper-right of the Tag Browse Tree - which "
                            "collapses the Tag Browse Tree of the Power Chart.",
                poll_freq=poll_freq)
            self._reload_icon = ComponentPiece(
                locator=self._RELOAD_ICON_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                description="The reload/refresh icon located in the upper-right of the Tag Browse Tree of the Power "
                            "Chart.",
                poll_freq=poll_freq)

        def add_tags_to_chart(self, tag_paths: [str]) -> None:
            """
            Add tags to the Power Chart. Requires the Tag Browse Tree already be expanded. If all specified tags are
            already graphed, no action is taken, and the Tag Browse Tree will remain expanded.

            :param tag_paths: A list of tag paths which describe the tags to add to the Power Chart graph as pens.

            :raises TimeoutException: If any of the supplied paths does not map to a tag, or if the Tag Browse Tree is
                not present/expanded.
            """
            for tag_path in tag_paths:
                tag_name = self._split_item_label_path(tag_path)[-1]
                self._expand_tag_browser_tree_by_path(path=tag_path)
                try:
                    WebDriverWait(driver=self.driver, timeout=5).until(
                        IAec.function_returns_true(
                            custom_function=self._select_tag_to_be_added_later,
                            function_args={"tag_name": tag_name}))
                except TimeoutException as toe:
                    raise TimeoutException(msg=f"No tag found with a name of '{tag_name}'.") from toe
                # wait for Apply button to become enabled
                WebDriverWait(driver=self.driver, timeout=1).until(IAec.function_returns_true(
                    custom_function=self._add_tag_button.is_enabled, function_args={}))
                if self._add_tag_button.is_enabled():
                    # tag might already be displayed in the chart, so we might not need to add it
                    self._add_tag_button.click(binding_wait_time=1)

        def click_reload_icon(self) -> None:
            """
            Click the reload icon of the Tag Browse Tree.

            :raises TimeoutException: If the Tag Browse Tree is not expanded in the Power Chart.
            """
            self._reload_icon.click(binding_wait_time=1)

        def collapse_if_expanded(self) -> None:
            """
            Collapse the Tag Browse Tree if it is currently expanded. If the Tag Browse Tree is already collapsed, then
            no action is taken.
            """
            if self.tag_browser_is_expanded():
                self._close_icon.click()

        def is_displayed(self) -> bool:
            """
            Determine if the Tag Browse Tree is displayed.

            :returns: True, if the Tag Browse Tree is currently displayed - False otherwise.
            """
            return self.tag_browser_is_expanded()

        def is_in_responsive_mode(self) -> bool:
            """
            Determine if the Tag Browse Tree is in responsive mode.

            :returns: True, if the Tag Browse Tree is currently rendering in responsive mode.
            """
            return "mobile" in self.find().get_attribute(name="class")

        def tag_browser_is_expanded(self) -> bool:
            """
            Determine if the Tag Browse Tree is expanded.

            :returns: True, if the tag Browse Tree is currently expanded - False otherwise.
            """
            try:
                return 'expanded' in self.find(wait_timeout=1).get_attribute('class')
            except TimeoutException:
                return False

        def _expand_tag_browser_tree_by_path(self, path: str) -> None:
            """
            Expand the Tag Browse Tree structure based on a supplied tag path.

            :param path: The path of a Tag as a slash-delimited string.
            """
            path_nodes = self._split_item_label_path(path)
            for i in path_nodes:
                try:
                    if self.item_label_exists_in_tree(item_label=i) and \
                            not self.item_is_expanded(item_label=i) \
                            and (path_nodes.index(i) != len(path_nodes)-1):
                        folder_index = self._get_index_of_item_in_tree(item_label=i)
                        self._folder_icons.find_all()[folder_index].click()
                        self.wait_on_binding(time_to_wait=1)
                        WebDriverWait(driver=self.driver, timeout=3, poll_frequency=self.poll_freq).until(
                            IAec.function_returns_true(
                                custom_function=self.item_is_expanded,
                                function_args={'item_label': i}))
                except TimeoutException as toe:
                    raise TimeoutException(
                        msg=f"Tag browser tree might not have expanded as expected.\nCheck that the provided "
                            f"path \'{path}\' is correct.") from toe

        def _select_tag_to_be_added_later(self, tag_name: str) -> bool:
            """
            Select a singular tag for later addition to the Power Chart.

            :param tag_name: The name of the tag to select now, for later addition to the Power Chart graph.

            :returns: True, if the supplied tag name was selected successfully - False otherwise.
            """
            try:
                self.click_item_label(item_label=tag_name)
                return True
            except TimeoutException:
                return False

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 10,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        self._footer = self._PowerChartFooter(
            parent_locator_list=self.locator_list, driver=driver, poll_freq=poll_freq)
        self._graph = self._PowerChartGraph(
            parent_locator_list=self.locator_list, driver=driver, poll_freq=poll_freq)
        self._header = self._PowerChartHeader(
            parent_locator_list=self.locator_list, driver=driver, poll_freq=poll_freq)
        self._pen_control_table = self._PowerChartTable(
            parent_locator_list=self.locator_list, driver=driver, poll_freq=poll_freq)
        self._settings_panel = self._PowerChartSettingsPanel(
            parent_locator_list=self.locator_list, driver=driver, poll_freq=poll_freq)
        self._tag_browser = self._PowerChartTagBrowser(
            parent_locator_list=self.locator_list, driver=driver, poll_freq=poll_freq)

    def add_tags_to_chart(self, tag_paths: [str]) -> None:
        """
        Add tags to the chart to be graphed as pens. This function will expand the Tag Browser if it is not already
        expanded, and will leave the Tag Browser expansion state as it was before this function was invoked.

        :param tag_paths: A list containing the full tag paths of each tag to add.

        :raises TimeoutException: If the Tag Browser button is not present, or if any supplied tag path does not
            identify a Tag to be added.
        """
        _original_state = self._tag_browser.tag_browser_is_expanded()
        if not _original_state:
            self._header.click_tag_browser_button()
        self._tag_browser.add_tags_to_chart(tag_paths=tag_paths)
        self.wait_on_binding(time_to_wait=2)  # wait for tags to be graphed
        if not _original_state:
            self._tag_browser.collapse_if_expanded()

    def button_is_active(self, option_bar_button: OptionBarButton) -> bool:
        """
        Determine if an Option Bar button is active (selected/in-use).

        :param option_bar_button: The Option Bar button to check the status of.

        :returns: True, if the supplied Option Bar button is active - False otherwise.
        """
        return self._header.button_is_active(option_bar_button=option_bar_button)

    def button_is_displayed(self, option_bar_button: OptionBarButton) -> bool:
        """
        Determine if an Option Bar button is displayed.

        :param option_bar_button: The Option Bar button we will check.

        :returns: True, if the supplied Option Bar button is displayed - False otherwise.
        """
        return self._header.button_is_displayed(option_bar_button=option_bar_button)

    def click_add_pen_link_in_settings_panel(self) -> None:
        """
        Click the '+ Add Pen' link. Requires that the Settings panel already be open.

        :raises TimeoutException: If the Settings panel is not already open, or if the Pens tab is not present.
        """
        self._settings_panel.click_add_pen_link()

    def click_and_drag_chart(self, x_offset: int = 0, y_offset: int = 0) -> None:
        """
        Blindly click within the Power Chart and then drag some number of pixels before releasing the click event.

        :param x_offset: The number of pixels to the right of the upper left corner to click.
        :param y_offset: The number of pixels down from the upper left corner to click.
        """
        self._graph.click_and_drag_chart(x_offset=x_offset, y_offset=y_offset)

    def click_cancel_button_during_deletion(self) -> None:
        """
        Click the 'Cancel' button during the deletion process.

        :raises TimeoutException: If the 'Cancel' button is not present.
        """
        self._settings_panel.cancel_deletion()

    def click_chart_settings_link_in_settings_panel(self) -> None:
        """
        Click the 'Chart Settings' link within the breadcrumb path at the top of the Settings panel.

        :raises TimeoutException: If the Settings panel is nt already open, or if the Chart Settings breadcrumb
            option is not present. This will occur anytime the Chart Settings tabbed area is already displayed.
        """
        self._settings_panel.click_chart_settings_breadcrumb_link()

    def click_confirm_button_during_deletion(self) -> None:
        """
        Click the 'Delete' button available during the process of deleting a pen.

        :raises TimeoutException: If the 'Delete' button is not present.
        """
        self._settings_panel.confirm_deletion()

    def click_done_button_in_settings_panel(self) -> None:
        """
        Click the Done button located in the bottom right of the Settings panel.

        :raises TimeoutException: If the 'Done' button is not present.
        """
        self._settings_panel.click_done()

    def click_normal_state_stroke_color_dropdown(self) -> None:
        """
        Click the 'Normal State' stroke color dropdown for the pen which is currently being edited.

        :raises TimeoutException: if not currently in the pen editing section of the Settings panel.
        """
        self._settings_panel.click_normal_state_stroke_color_dropdown()

    def click_option_bar_button(self, option_bar_button: OptionBarButton) -> None:
        """
        Click a button located within the Option Bar area.

        :param option_bar_button: The Option Bar button to click.

        :raises TimeoutException: if the supplied button is not present.
        """
        self._header.click_option_bar_button(option_bar_button=option_bar_button)

    def click_reload_icon_in_tag_browser(self) -> None:
        """
        Click the reload icon of the Tag Browse Tree.

        :raises TimeoutException: If the Tag Browse Tree is not expanded in the Power Chart.
        """
        self._tag_browser.click_reload_icon()

    def click_pencil_icon_for_axis(self, axis_name) -> None:
        """
        Click the pencil (edit) icon for an axis. Requires that the Settings panel already be displayed.

        :param axis_name: The name of the axis to begin editing.

        :raises TimeoutException: If no row matching the supplied axis name is present, or if the Settings panel is not
            displayed.
        """
        self._settings_panel.click_pencil_icon_for_axis(axis_name=axis_name)

    def click_point_in_color_picker(self) -> None:
        """
        Click the color picker displayed while editing any of the color settings for a pen. Requires that the
        picker already be visible as a result of clicking any of the available color dropdown items. Note that
        Selenium does not properly handle offsets for the color picker modal, so this function has limited use.

        :raises TimeoutException: If the color picker is not present.
        """
        self._settings_panel.click_point_in_color_picker()

    def click_tab_of_settings_panel(self, tab: Tab) -> None:
        """
        Click a tab of the Settings panel. Requires that the Settings panel already be open.

        :param tab: The tab to click.

        :raises TimeoutException: If the supplied tab is not present.
        """
        self._settings_panel.click_tab(tab=tab)

    def click_tag_browser_button(self) -> None:
        """
        Click the button which expands or collapses the Tag Browser panel.

        :raises TimeoutException: If the Tag Browse button is not present.
        """
        self._header.click_tag_browser_button()

    def close_settings_panel(self) -> None:
        """
        Close the Settings panel. Takes no action if the Settings panel is already closed.

        :raises AssertionError: If unsuccessful in closing the Settings panel.
        """
        self._settings_panel.close_settings_panel()

    def collapse_tag_browser_if_expanded(self) -> None:
        """
        Collapse the Tag Browse Tree if it is currently expanded. If the Tag Browse Tree is already collapsed, then
        no action is taken.
        """
        self._tag_browser.collapse_if_expanded()

    def date_range_selector_is_displayed(self) -> bool:
        """
        Determine if the Date Range selector is displayed.

        :returns: True, if the date range selector is currently displayed - False otherwise.
        """
        return self._header.date_range_selector_expansion_icon_is_displayed()

    def click_trash_can_icon_for_pen_in_settings_panel(self, pen_name: str) -> None:
        """
        Click the trash can icon for a specific pen. Note that this only begins the deletion process, and that there
        are further actions to take after this.

        :param pen_name: The name of the pen you would like to begin the deletion process for.

        :raises TimeoutException: If the trash can icon is not present. This might be due to no pen with the
            supplied name being present.
        """
        self._settings_panel.click_trash_can_icon_for_pen(pen_name=pen_name)

    def click_pencil_icon_for_pen_in_pen_control_table(self, pen_name: str) -> None:
        """
        Click the pencil icon for a pen in the pen control table.

        :param pen_name: The name of the pen for which you would like to click the accompanying pencil icon.

        :raises IndexError: If no pen with the supplied name could be found.
        """
        self._pen_control_table.click_pencil_icon_for_pen(pen_name=pen_name)

    def click_pencil_icon_for_pen_in_settings_panel(self, pen_name: str) -> None:
        """
        Click the pencil icon for a specific pen. Note that this only begins the editing process, and that there
        are further actions to take after this.

        :param pen_name: The name of the pen you would like to begin the editing process for.

        :raises TimeoutException: If the pencil icon is not present. This might be due to no pen with the
            supplied name being present.
        """
        self._settings_panel.click_pencil_icon_for_pen(pen_name=pen_name)

    def get_all_pen_names_from_pen_control_table(self) -> List[str]:
        """
        Obtain the names of all pens displayed in the pen control table.

        :returns: A list which contains the name of every pen displayed in the pen control table.

        :raises TimeoutException: If the pen control table is not present.
        """
        return self._pen_control_table.get_all_pen_names_from_pen_table()

    def get_column_headers_from_pen_control_table(self) -> List[str]:
        """
        Obtain the headers of the columns displayed in the pen control table. Ignores the selection column, as it
        contains no header text.

        :returns: A list which contains the header of every column currently displayed in the pen control table.

        :raises TimeoutException: If no pen control table is present.
        """
        return self._pen_control_table.get_column_headers_from_pen_table()

    def get_count_of_pen_fault_overlays(self) -> int:
        """
        Obtain a count of how many pens are currently displaying fault overlays.

        :returns: A count of how many pens are currently displaying fault overlays.
        """
        return self._pen_control_table.get_count_of_pen_fault_overlays()

    def get_count_of_pens_from_pen_control_table(self) -> int:
        """
        Obtain a count of all pens listed in the pen control table.

        :returns: A count of every pen displayed in the pen control table.

        :raises TimeoutException: If the pen control table is not present.
        """
        return self._pen_control_table.get_count_of_available_pens_from_pen_table()

    def get_count_of_visible_line_charts(self) -> int:
        """
        Obtain a count of pens which are displayed in the chart.

        :returns: A count of pens currently rendered in the chart.
        """
        return self._graph.get_count_of_graphed_pens()

    def get_css_property_value_from_title_in_header(self, property_name: Union[CSSPropertyValue, str]) -> str:
        """
        Obtain the value of a CSS property from the title of the header.

        :param property_name: The name of the CSS property you would like the value of.

        :returns: The value of the supplied CSS property of the title of the header of the Power Chart.

        :raises TimeoutException: If the title is not present.
        """
        return self._header.get_css_property_value_from_title(property_name=property_name)

    def get_css_property_value_from_x_axis_grid(self, property_name: Union[CSSPropertyValue, str]) -> str:
        """
        Obtain the value of a CSS property from the grid of the X axis.

        :param property_name: The name of the property you want to value of.

        :returns: The value of the requested CSS property from the X axis grid.

        :raises TimeoutException: If no X axis grid is present.
        """
        return self._graph.get_css_property_from_x_axis_grid(property_name=property_name)

    def get_css_property_value_from_y_axis_grid(self, property_name: Union[CSSPropertyValue, str]) -> str:
        """
        Obtain the value of a CSS property from the grid of the Y axis.

        :param property_name: The name of the property you want to value of.

        :returns: The value of the requested CSS property from the Y axis grid.

        :raises TimeoutException: If no Y axis grid is present.
        """
        return self._graph.get_css_property_from_y_axis_grid(property_name=property_name)

    def get_css_property_value_from_y_axis(self, property_name: Union[CSSPropertyValue, str]) -> str:
        """
        Obtain a CSS property value from the Y axis.

        :param property_name: The name of the CSS property to retrieve the value of.

        :returns: The value of the requested CSS property from the Y axis.

        :raises TimeoutException: If no Y axis is present.
        """
        return self._graph.get_y_axis_vertical_bar_css_property(property_name=property_name)

    def get_currently_selected_color_from_color_picker(self) -> str:
        """
        Obtain the color in use for whichever setting is currently being modified, as a string. Note that as this
        value is coming from a prop it will always be hex. Requires that the Settings panel be displayed, and that a pen
        already be in an editing state, and that a color dropdown has already been clicked/activated.

        :returns: The color currently applied as a hex string.

        :raises TimeoutException: If the color picker and its accompanying inputs are not present.
        """
        return self._settings_panel.get_current_color_from_picker()

    def get_displayed_tab_names_from_settings_panel(self) -> List[str]:
        """
        Obtain the name sof all tabs listed in the Settings panel. Requires that the Settings panel already be
        displayed.

        :returns: A list which contains the names of all tabs displayed in the Settings panel, or na empty list if the
            Settings panel is not displayed.
        """
        return self._settings_panel.get_displayed_tab_names() if self.settings_panel_is_displayed() else []

    def get_graph_path(self, pen_name: str) -> str:
        """
        Obtain the drawn path of a graphed pen. Useful for determining when a graphed pen has updated.

        :param pen_name: The name of the pen for which you would like the path of the graphed line.

        :returns: A string which represents the actual graphed line of a pen.

        :raises IndexError: If unable to link the supplied pen name to a graphed line by the color of the pen's
            checkbox.
        :raises TimeoutException: If no pen with the supplied name is present in the pen control table, or if no pens
            are graphed at all.
        """
        return self._graph.get_drawn_path(pen_checkbox_color_as_string=self.get_pen_checkbox_color(pen_name=pen_name))

    def get_historical_range(self) -> HistoricalRange:
        """
        Obtain the applied historical range as an object. Expands the range selector if not already open, and then
        closes the range selector if it was not open to start with. Returns a HistoricalRange object, even if the Power
        Chart is using a realtime range.

        :returns: The historical range as a HistoricalRange object - even if the Power Chart is using a realtime range.
        """
        return self._header.get_historical_range()

    def get_html_class_from_title_in_header(self) -> str:
        """
        Obtain the html class attribute for the title of the header.

        :returns: The HTML class attribute for the title of the header of the Power Chart.

        :raises TimeoutException: If the title is not present.
        """
        return self._header.get_title_html_class()

    def get_html_class_from_x_axis(self) -> str:
        """
        Obtain the HTML class of the X axis.

        :returns: The class of the X axis as it exists in the DOM.

        :raises TimeoutException: If no X axis is present.
        """
        return self._graph.get_x_axis_html_class()

    def get_html_class_from_y_axis(self) -> str:
        """
        Obtain the HTML class of the Y axis.

        :returns: The class of the Y axis as it exists in the DOM.

        :raises TimeoutException: If no Y axis is present.
        """
        return self._graph.get_y_axis_html_class()

    def get_pen_checkbox_color(self, pen_name: str) -> str:
        """
        Obtain the color in use for a given pen. This color will always be the same as the line which is graphed.

        :param pen_name: The name of the checkbox for which you would like the color of the accompanying checkbox.

        :returns: The color in use by the checkbox of a pen.

        :raises TimeoutException: If no pen with the supplied name is present in the pen control table, or if the
            pen control table is not present.
        """
        return self._pen_control_table.get_pen_checkbox_color(pen_name=pen_name)

    def get_pen_name_from_settings_panel(self) -> str:
        """
        Obtain the name of the pen as displayed in the Settings panel.

        :returns: The text contents of the name field within the Settings panel.

        :raises TimeoutException: If the Settings panel is not present.
        """
        return self._settings_panel.get_pen_name()

    def get_realtime_range_time_units(self) -> str:
        """
        Obtain the unit of time in use by the realtime range. Only works if the Power Cart is currently using
        a realtime range.

        :returns: The unit of time in use by the realtime range.

        :raises TimeoutException: If the Power Chart has configured the range selector piece to be invisible.
        """
        return self._header.get_date_range_message().split(" ")[-1]

    def get_realtime_range_scalar_time_value(self) -> int:
        """
        Obtain the scalar amount of time in use by the realtime range. Only works if the Power Cart is currently using
        a realtime range.

        :returns: The scalar time value in use by the realtime range.

        :raises TimeoutException: If the Power Chart has configured the range selector piece to be invisible.
        """
        return int(self._header.get_date_range_message().split(" ")[1])

    def get_text_of_top_level_nodes(self) -> List[str]:
        """
        Obtain the text of all items located at the top-most level of the Tag Browser.
        """
        return self._tag_browser.get_text_of_top_level_items()

    def get_time_axis_labels(self) -> List[str]:
        """
        Obtain the labels displayed on the X (time) axis.

        :returns: A list which contains all currently displayed labels from the X (time) axis.

        :raises TimeoutException: If no labels are displayed on the X (time) axis.
        """
        return self._graph.get_displayed_time_axis_labels()

    def get_time_range_selector_message(self) -> str:
        """
        Obtain the range message associated with the Date Range Selector. This value describes the applied range.
        Example: 'Last 8 hours', or a breakdown of the date/times used for the Historical range.

        :returns: The range message associated with the Date Range Selector, if available.

        :raises TimeoutException: If the Power Chart has made the Date Range Selector invisible.
        """
        return self._header.get_date_range_message()

    def get_x_axis_style_class_property_value(self, property_name: Union[CSSPropertyValue, str]) -> str:
        """
        Obtain the value of a CSS property from the X axis.

        :param property_name: The name of the CSS property you would like the value of.

        :returns: The value of the requested CSS property.

        :raises TimeoutException: If no labels are present on the X (time) axis.
        """
        return self._graph.get_x_axis_css_property_value(property_name=property_name)

    def get_y_axis_label_style_class_property_value(self, property_name: Union[CSSPropertyValue, str]) -> str:
        """
        Obtain the value of a CSS property from the Y axis.

        :param property_name: The name of the CSS property you would like the value of.

        :returns: The value of the requested CSS property.

        :raises TimeoutException: If no labels are present on the Y axis.
        """
        return self._graph.get_y_axis_label_css_property_value(property_name=property_name)

    def hover_over_option_bar_button(self, option_bar_button: OptionBarButton) -> None:
        """
        Hover over a button of the Option Bar.

        :param option_bar_button: The Option Bar button to hover over.

        :raises TimeoutException: If the supplied Option Bar button is not present.
        """
        self._header.hover_over_option_bar_button(option_bar_button=option_bar_button)

    def is_displaying_in_full_screen(self) -> bool:
        """
        Determine if the Power Chart is rendering in a full-screen layout.

        :returns: True, if the Power Chart is currently rendering in a manner which covers the entire viewport - False
            otherwise.

        :raises TimeoutException: If the full-screen button is not present.
        """
        return self._header.button_is_active(
            option_bar_button=OptionBarButton.FULL_SCREEN)

    def is_in_responsive_mode(self) -> bool:
        """
        Determine if the Power Chart is rendering in a mobile-friendly layout.

        :returns: True, if the Tag Browser, Header, and Footer are all reporting as rendering in a mobile-friendly
            layout - False if any of those pieces is reporting otherwise.

        :raises TimeoutException: If the Tag Browser, Header, or Footer are not present.
        """
        return self._tag_browser.is_in_responsive_mode() \
            and self._header.is_in_responsive_mode() \
            and self._footer.is_in_responsive_mode()

    def line_is_displayed_by_color(self, pen_checkbox_color_as_str: str) -> bool:
        """
        Determine if a line is graphed.

        :param pen_checkbox_color_as_str: The color to look for in the graph. This value MUST be supplied in the
            same form as the browser in use would return a color value. It is recommended to avoid supplying
            hard-coded colors and instead supply values retrieved from the browser. Look into use
            of :func:`get_pen_checkbox_color` in order to obtain a color.

        :returns: True, if any graphed line uses the supplied color - False otherwise.
        """
        return self._graph.line_is_displayed_by_color(pen_checkbox_color_as_str=pen_checkbox_color_as_str)

    def line_is_displayed_by_name(self, pen_name: str) -> bool:
        """
        Determine if a line is graphed.

        :param pen_name: The name of the pen to look for in the graph.

        :returns: True, if the supplied pen name has a graphed line - False otherwise.
        """
        try:
            return self._graph.line_is_displayed_by_color(
                pen_checkbox_color_as_str=self._pen_control_table.get_pen_checkbox_color(pen_name=pen_name))
        except TimeoutException:
            return False

    def pen_checkbox_is_active(self, pen_name: str) -> bool:
        """
        Determine if the checkbox of a pen is active (selected and/or checked are synonymous with active).

        :returns: True, if the checkbox for the specified pen is active/selected/checked.

        :raises TimeoutException: If no pen with the supplied name is present in the pen control table, or if the
            pen control table is not present.
        """
        return self._pen_control_table.pen_checkbox_is_active(pen_name=pen_name)

    def pen_control_column_is_displayed(self, pen_control_column: PenControlColumn) -> bool:
        """
        Determine if a pen control column is displayed.

        :param pen_control_column: The pen control column or range brush column to check for the presence of.

        :returns: True, if the supplied column is displayed - False otherwise.
        """
        return self._pen_control_table.pen_control_column_is_displayed(pen_control_column=pen_control_column)

    def pen_settings_are_displayed_in_settings_panel(self) -> bool:
        """
        Determine if the Pen settings panel is displayed.

        :returns: True, if the inputs used to edit a pen are currently displayed - False otherwise.
        """
        return self._settings_panel.pen_settings_are_displayed()

    def pen_table_is_visible(self) -> bool:
        """
        Determine if the pen control table is expanded.

        :returns: True, if the pen control table is currently expanded - False otherwise.
        """
        return self._pen_control_table.pen_table_is_expanded()

    def range_brush_column_is_displayed(self, range_brush_column: RangeBrushColumn) -> bool:
        """
        Determine if a range brush column is displayed in the pen control table.

        :param range_brush_column: The range brush column for which we will check the display state.

        :returns: True, if the supplied range brush column is displayed - False otherwise.
        """
        return self._pen_control_table.range_brush_column_is_displayed(range_brush_column=range_brush_column)

    def remove_pen_by_name(self, pen_name: str) -> None:
        """
        Remove a pen from the pen control table (and therefore the Power Chart) via the pen control table.

        :param pen_name: The name of the pen you would like to remove.

        :raises AssertionError: If unsuccessful in removing the supplied pen from the Power Chart.
        :raises TimeoutException: If the pen control table is not present.
        """
        self._pen_control_table.remove_pen_by_name(pen_name=pen_name)

    def select_historical_range(self, historical_range: HistoricalRange) -> None:
        """
        Apply the values of a HistoricalRange object to the Power Chart. This convenience function handles expansion,
        application, and confirmation of the supplied values.

        :param historical_range: A HistoricalRange object which contains all of the information about the range to be
            selected.

        :raises AssertionError: If unsuccessful in applying the provided range.
        """
        self._header.open_date_range_selector_if_not_displayed()
        self._header.select_date_range_selector_tab(tab=DateRangeSelectorTab.HISTORICAL)
        self._header.set_historical_month(month=historical_range.beginning_month)
        self._header.set_historical_year(year=historical_range.beginning_year)
        self._header.set_historical_day(numeric_day=historical_range.beginning_day)
        self._header.set_historical_month(month=historical_range.ending_month)
        self._header.set_historical_year(year=historical_range.ending_year)
        self._header.set_historical_day(numeric_day=historical_range.ending_day)
        self._header.apply_changes()

    def select_realtime_range(self, time_value: int, time_unit: DateRangeSelectorTimeUnit) -> None:
        """
        Select the scalar value of time and the time unit to use for the realtime range of the Power Chart.

        :param time_value: The scalar amount of time to apply.
        :param time_unit: The unit of time to apply.

        :raises TimeoutException: If the range selector is not present.
        """
        self._header.open_date_range_selector_if_not_displayed()
        self._header.select_date_range_selector_tab(tab=DateRangeSelectorTab.REALTIME)
        self._header.set_realtime_numeric_value(time_value=time_value)
        self._header.select_realtime_unit(time_unit=time_unit)
        self._header.apply_changes()

    def set_display_state_for_pen_in_settings_panel(self, pen_name: str, should_be_displayed: bool) -> None:
        """
        Set the display state of a pen listed in the Pens tab of the Settings panel. Requires the Settings panel
        already be displayed, and that the pen tab be displayed.

        :param pen_name: The name of the pen which will have its state set.
        :param should_be_displayed: If True, the pen will be set to display - otherwise, the pen will be set to not
            display.

        :raises TimeoutException: If the Settings panel is not already displayed.
        """
        self._settings_panel.set_display_checkbox_state_by_pen_name(
            pen_name=pen_name, should_be_checked=should_be_displayed)

    def set_grid_visible_checkbox_state_in_axis_settings(self, should_be_checked: bool) -> None:
        """
        Set the display state of the grid for the axis currently being edited.

        :param should_be_checked: If True, the checkbox will be set to active/checked - otherwise the checkbox will
            be set to inactive/un-checked.

        :raises TimeoutException: If the Settings panel is not already displayed, or an axis is not already being
            edited.
        """
        self._settings_panel.set_grid_visible_checkbox_state(should_be_checked=should_be_checked)

    def set_grid_y_axis_color_in_axis_settings(self, hex_desired_color: str) -> None:
        """
        Set the Y-axis color to be used by the grid for the axis currently being edited.

        :param hex_desired_color: The color (in hex format) to use for the Y-axis of the grid.

        :raises AssertionError: If unsuccessful in modifying the color in use by the Y-axis of the grid.
        :raises TimeoutException: If the Settings panel is not already displayed, or an axis is not already being
            edited.
        """
        self._settings_panel.set_grid_y_axis_color(hex_desired_color=hex_desired_color)

    def set_grid_y_axis_opacity_in_axis_settings(self, value: Union[float, str]) -> None:
        """
        Set the Y-axis opacity to be used by the grid for the axis currently being edited.

        :param value: The desired value (0<=value<=1) to use for the opacity of the Y-axis of the grid.

        :raises AssertionError: If unsuccessful in modifying the opacity in use by the Y-axis of the grid.
        :raises TimeoutException: If the Settings panel is not already displayed, or an axis is not already being
            edited.
        """
        self._settings_panel.set_grid_y_axis_opacity(value=value)

    def set_grid_y_axis_dasharray_in_axis_settings(self, value: str) -> None:
        """
        Set the Y-axis dash-array to be used by the grid for the axis currently being edited.

        :param value: The desired value to use for the dash-array of the Y-axis of the grid.

        :raises AssertionError: If unsuccessful in modifying the dash-array in use by the Y-axis of the grid.
        :raises TimeoutException: If the Settings panel is not already displayed, or an axis is not already being
            edited.
        """
        self._settings_panel.set_grid_y_axis_dash_array(value=value)

    def set_historical_range_and_apply(self, historical_range: HistoricalRange) -> None:
        """
        Open the date range selector, select values for a historical range, and then apply those changes.

        :param historical_range: The historical range settings to apply, within a HistoricalRange object.

        :raises AssertionError: If unsuccessful in applying the provided historical range.
        :raises TimeoutException: If the date range capabilities of the Power Chart are disabled.
        """
        self._header.set_historical_range_and_apply(historical_range=historical_range)

    def set_pen_control_column_display_state_in_settings_panel(
            self, pen_control_column: PenControlColumn, should_be_displayed: bool) -> None:
        """
        Set the display state of a column within the pen control table. Requires the Settings panel already be
        displayed.

        :param pen_control_column: The column which will have its state set.
        :param should_be_displayed: If True, the column will be set to display - otherwise the column will be set to
            not be displayed.

        :raises TimeoutException: If the Settings panel is not already displayed.
        """
        self._settings_panel.set_pen_control_column_display_state_in_settings_panel(
            pen_control_column=pen_control_column, should_be_displayed=should_be_displayed)

    def set_pen_enabled_state_in_settings_panel(self, should_be_enabled: bool) -> None:
        """
        Set the enabled state of a checkbox. The wording in the Power Chart is actually to "hide" the pen from the
        chart, so we reverse that logic inside this function. Requires that a pen already be in an "editing" state.

        :param should_be_enabled: If True, the pen will NOT be hidden - otherwise we will set the pen to be hidden.

        :raises TimeoutException: If the Settings panel is not already visible, or if a pen is not already being
            edited.
        """
        self._settings_panel.set_pen_enabled_state_in_settings_panel(should_be_enabled=should_be_enabled)

    def set_pen_name_while_editing(self, updated_pen_name: str) -> None:
        """
        Set the name of a pen during editing. Requires the Settings panel be displayed and a pen already be in editing
        mode.

        :param updated_pen_name: The desired pen name.

        :raises AssertionError: If unsuccessful in editing the name of the pen.
        :raises TimeoutException: If the Settings panel is not already visible, or if a pen is not already being
            edited.
        """
        self._settings_panel.set_pen_name_field(updated_pen_name=updated_pen_name)

    def set_pen_path_while_editing(self, updated_pen_path: str) -> None:
        """
        Set the path of a pen during editing.

        :param updated_pen_path: The desired pen path to use.

        :raises AssertionError: If unsuccessful in editing the path of the pen.
        :raises TimeoutException: If the Settings panel is not already visible, or if a pen is not already being
            edited.
        """
        self._settings_panel.set_pen_path_field(updated_pen_path=updated_pen_path)

    def set_pen_visibility_in_settings_panel(self, should_be_displayed: bool) -> None:
        """
        Set the display state of a pen while the pen is being edited. This function expects that a pen is already
        being edited in the Settings panel.

        :param should_be_displayed: If True, the pen will be set to display - otherwise, the pen will be set to not
            display.

        :raises TimeoutException: If the Settings panel is not already displayed, or if we are not already editing
            a pen.
        """
        self._settings_panel.set_pen_display_state_in_settings_panel(should_be_checked=should_be_displayed)

    def set_pen_visibility_on_pen_table(self, pen_name: str, should_be_visible: bool) -> None:
        """
        Set the display state (visibility) of a pen via the pen control table by interacting with the associated
        checkbox.

        :param pen_name: The name of the pen which you would like to set the display state of.
        :param should_be_visible: If True, the checkbox will be set to active/selected/checked - otherwise the
            checkbox will be set to inactive/unselected/un-checked.

        :raises AssertionError: If unsuccessful in setting the display state of the specified checkbox.
        :raises TimeoutException: if no pen with the supplied name is present, or if the pen control table is not
            present.
        """
        self._pen_control_table.set_pen_visibility_on_pen_table(pen_name=pen_name, should_be_visible=should_be_visible)

    def set_range_brush_basic(self) -> None:
        """
        Applies the range brush to the graph via a short drag event.
        """
        self._graph.set_range_brush_basic()

    def set_range_brush_column_display_state(
            self, range_brush_column: RangeBrushColumn, should_be_displayed: bool) -> None:
        """
        Set the display state of a column within the range brush table. Requires the Settings panel already be
        displayed.

        :param range_brush_column: The column which will have its state set.
        :param should_be_displayed: If True, the column will be set to display - otherwise the column will be set to
            not be displayed.

        :raises TimeoutException: If the Settings panel is not already displayed.
        """
        self._settings_panel.set_range_brush_column_display_state_in_settings_panel(
            range_brush_column=range_brush_column, should_be_displayed=should_be_displayed)

    def settings_panel_is_displayed(self) -> bool:
        """
        Determine if the Settings panel is displayed.

        :returns: True, if the Settings panel is currently open/displayed/expanded - False otherwise.
        """
        return self._settings_panel.is_displayed()

    def tag_browser_button_is_displayed(self) -> bool:
        """
        Determine if the Tag Browser button is displayed.

        :returns: True if the Tag Browser button is currently displayed - False otherwise.
        """
        return self._header.tag_browser_button_is_displayed()

    def tag_browser_panel_is_displayed(self) -> bool:
        """
        Determine if the Tag Browse Tree is displayed.

        :returns: True, if the Tag Browse Tree is currently displayed - False otherwise.
        """
        return self._tag_browser.is_displayed()

    def toggle_pen_table_display(self) -> None:
        """
        Toggle the pen control table expansion state.

        :raises TimeoutException: If the expand/collapse toggle icon is not present.
        """
        self._pen_control_table.toggle_pen_table_display()

    def x_axis_grid_is_displayed(self) -> bool:
        """
        Determine if grid lines are displayed for the X axis.

        :returns: True, if grid lines are found for the X axis - False otherwise.
        """
        return self._graph.get_count_of_x_axis_grid_lines() > 0

    def y_axis_grid_is_displayed(self) -> bool:
        """
        Determine if grid lines are displayed for the Y axis.

        :returns: True, if grid lines are found for the Y axis - False otherwise.
        """
        return self._graph.get_count_of_y_axis_grid_lines() > 0
