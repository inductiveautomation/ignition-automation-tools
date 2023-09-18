from typing import Optional, List, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece


class TimeSeriesChart(BasicPerspectiveComponent):
    """A Perspective Time Series Chart."""
    _DATE_TIME_CONTAINER_LOCATOR = (By.CSS_SELECTOR, ".date-time-container:nth-of-type(1)")
    _DATE_CONTAINER_LOCATOR = (By.CSS_SELECTOR, ".date-container")
    _TIME_CONTAINER_LOCATOR = (By.CSS_SELECTOR, ".time-container")
    _TIME_AXIS_LABEL_LOCATOR = (By.CSS_SELECTOR, "text.ia_timeSeriesChartComponent__timeAxis__values")

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
        self._date_time_container = ComponentPiece(
            locator=self._DATE_TIME_CONTAINER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            description="The container for the date/time labels.",
            poll_freq=poll_freq)
        self._date_container = ComponentPiece(
            locator=self._DATE_CONTAINER_LOCATOR,
            driver=driver,
            parent_locator_list=self._date_time_container.locator_list,
            wait_timeout=1,
            description="The container which contains only the date information.",
            poll_freq=poll_freq)
        self._time_container = ComponentPiece(
            locator=self._TIME_CONTAINER_LOCATOR,
            driver=driver,
            parent_locator_list=self._date_time_container.locator_list,
            wait_timeout=1,
            description="The container which contains only the time information.",
            poll_freq=poll_freq)
        self._time_axis_label = ComponentPiece(
            locator=self._TIME_AXIS_LABEL_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            description="The label which contains the text of the time axis of the Time Series Chart.",
            poll_freq=poll_freq)

    def get_date_range_text(self) -> str:
        """
        Obtain the text which describes the date range of the graphed data.

        :returns: The text visible to a user which describes the date range of the graphed data.

        :raises TimeoutException: If the date is not present.
        """
        return self._date_container.get_text()

    def get_text_of_last_time_meridian(self) -> str:
        """
        Obtain the text of the last displayed time meridian (am/pm) of the chart.

        :returns: The text of the last displayed time meridian.

        :raises TimeoutException: If the time range is not present.
        """
        return self._time_container.get_text().split(" ")[-1]

    def get_time_axis_label(self, zero_based_index: int) -> str:
        """
        Obtain the text of a time axis label as it is displayed to the user.
        
        :param zero_based_index: The zero-based index of the label to obtain.
        
        :returns: The text of a time axis (x axis) label.

        :raises IndexError: If the supplied index is invalid based o the number of labels displayed.
        :raises TimeoutException: If no time axis labels are present.
        """
        return self._time_axis_label.find_all()[zero_based_index].text
