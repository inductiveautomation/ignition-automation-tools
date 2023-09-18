from enum import Enum
from typing import Optional, Union, Tuple, List

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Helpers.IASelenium import IASelenium


class RenderType(Enum):
    """An enumeration of available render types for the Perspective XY Chart Component."""
    CANDLESTICK = "candlestick"
    COLUMN = "column"
    LINE = "line"
    STEP_LINE = "step line"


class XYChart(BasicPerspectiveComponent):
    """A Perspective XY Chart Component."""

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
        self._bar_coll = {}
        self._series_coll = {}

    def click(self, wait_timeout: Optional[Union[int, float]] = None, binding_wait_time: float = 0) -> None:
        """
        Please do not blindly click the XY Chart; no good will come of it.

        :raises NotImplementedError: Because you shouldn't do it.
        """
        raise NotImplementedError("Please don't blindly click the XYChart.")

    def click_series_label_in_legend_by_text(self, label_text: str, binding_wait_time: float = 0) -> None:
        """
        Click the label of a series within the legend of the XY Chart.

        :param label_text: The text of the label to click. This should be the name of the series.
        :param binding_wait_time: How long to wait after the click before allowing code to continue.

        :raises TimeoutException: If no label with the provided text is present.
        :raises NoSuchElementException: If unable to locate the click target of the label.
        """
        self._get_series_label_from_legend(label_text=label_text).find_element(*(By.TAG_NAME, "rect")).click()
        self.wait_on_binding(time_to_wait=binding_wait_time)

    def get_count_of_bars_in_series(self, series_label: str) -> int:
        """
        Obtain a count of bars displayed for a given series.

        :param series_label: The name of the series for which we will obtain a count of bars.

        :returns: The count of displayed bars for the provided series.
        """
        try:
            return len(self._get_paths_for_series(series_label=series_label).find_all())
        except TimeoutException:
            return 0

    def hover_over_bar_of_series(self, bar_index: int, series_label: str) -> None:
        """
        Hover over a specific bar for a given series.

        :param bar_index: The zero-based index of the bar you would like to hover over.
        :param series_label: The name of the series to target.

        :raises IndexError: If the supplied index is invalid based on the number of displayed bars.
        :raises TimeoutException: If no bars exist for the provided series.
        """
        IASelenium(driver=self.driver).hover_over_web_element(
            web_element=self._get_paths_for_series(series_label=series_label).find_all()[bar_index])

    def series_label_is_displayed_in_legend(self, label_text: str) -> bool:
        """
        Determine if a series is displayed in the legend of the XY Chart.

        :param label_text: The name of the series.

        :returns: True, if the provided series is listed in the legend - False otherwise.
        """
        try:
            return self._get_series_label_from_legend(label_text=label_text).is_displayed()
        except IndexError:
            return False

    def series_is_displayed_in_chart_body(self, series_name: str) -> bool:
        """
        Determine if a series is displayed in the body (graph) of the XY Chart.

        :param series_name: The name of the series to look for in the body of the XY Chart.

        :returns: True, if the provided series is graphed in some manner - False otherwise.
        """
        return self._get_top_level_series_element(series_label=series_name).find().is_displayed()

    def _get_series_label_from_legend(self, label_text: str) -> WebElement:
        """
        Obtain the WebElement which is the label for a series in the legend of the XY Chart.

        :param label_text: The text of the label to query for.

        :returns: A WebElement which is the label of the provided series within the legend of the XY Chart.

        :raises IndexError: If no label with the provided text is present.
        :raises NoSuchElementException: If no labels are found at all.
        """
        return list(
            filter(
                lambda e: e.text == label_text,
                self.driver.find_elements(
                    *ComponentPiece(
                        locator=(By.CSS_SELECTOR, 'g[focusable="true"]'),
                        driver=self.driver,
                        parent_locator_list=self.locator_list).get_full_css_locator())))[0]

    def _get_paths_for_series(self, series_label: str) -> ComponentPiece:
        """
        Obtain the Component Piece which describes the paths for a given series.

        :param series_label: The name of the series we would like the paths for.

        :returns: A Component piece which can be used to describe ALL <paths> for a series.
        """
        bar = self._bar_coll.get(series_label)
        if not bar:
            bar = ComponentPiece(
                locator=(By.CSS_SELECTOR, 'path'),
                driver=self.driver,
                parent_locator_list=self._get_top_level_series_element(series_label=series_label).locator_list,
                description="The <path> elements which define the lines drawn for the series.")
            self._bar_coll[series_label] = bar
        return bar

    def _get_top_level_series_element(self, series_label: str) -> ComponentPiece:
        """
        Obtain a ComponentPiece which describes a series in the body of the XY Chart.

        :param series_label: The name of the series we would like the graph overview of.

        :returns: A Component piece which can be used to describe the series in the body of the XY Chart.
        """
        series = self._series_coll.get(series_label)
        if not series:
            series = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'g[aria-label="{series_label}"]'),
                driver=self.driver,
                parent_locator_list=self.locator_list,
                description=f"The label for the '{series_label}' series.")
            self._series_coll[series_label] = series
        return series
