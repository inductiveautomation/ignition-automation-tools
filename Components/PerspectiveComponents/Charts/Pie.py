from typing import Tuple, Optional, List

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece


class Pie(BasicPerspectiveComponent):
    """A Perspective Pie Chart Component."""
    LOGGER = "PIE"
    _SECTION_LOCATOR = (By.CSS_SELECTOR, 'g[role="menu-item"]')
    _CHECKBOX_LOCATOR = (By.CSS_SELECTOR, 'g[role="switch"]')
    _CHECKBOX_LABEL_LOCATOR = (By.CSS_SELECTOR, "tspan")
    _TITLE_LOCATOR = (By.CSS_SELECTOR, "svg > g > g > g > g > g > g > text > tspan")
    _LEGEND_CONTAINER_LOCATOR = (By.CSS_SELECTOR, 'g[aria-label="Legend"]')

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
        self._sections = ComponentPiece(
            locator=self._SECTION_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            description="The actual slices of the Pie.",
            poll_freq=poll_freq)
        self._title = ComponentPiece(
            locator=self._TITLE_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            description="The title of the Pie Chart.",
            poll_freq=poll_freq)
        self._legend_container = ComponentPiece(
            locator=self._LEGEND_CONTAINER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            description="The Legend of the Pie Chart.",
            poll_freq=poll_freq)
        self._checkboxes = ComponentPiece(
            locator=self._CHECKBOX_LOCATOR,
            driver=driver,
            parent_locator_list=self._legend_container.locator_list,
            wait_timeout=1,
            description="The checkboxes within the legend of the Pie Chart.",
            poll_freq=poll_freq)

    def get_chart_title(self) -> str:
        """
        Obtain the title of the Pie Chart.

        :returns: The title of the Pie Chart as it is displayed to the user.

        :raises TimeoutException: If the Pie CHart is not displaying a title.
        """
        try:
            return self._title.get_text()
        except TimeoutException as toe:
            raise TimeoutException(msg="No title is present for the Pie Chart.") from toe

    def get_legend_checkbox_count(self) -> int:
        """
        Obtain a count of displayed checkboxes from the legend.

        :returns: A count of all checkboxes displayed as part of legend of the Pie Chart.
        """
        try:
            return len(self._checkboxes.find_all())
        except TimeoutException:
            return 0

    def get_legend_checkbox_labels(self) -> List[str]:
        """
        Obtain all labels for checkboxes in the legend of the Pie Chart.

        :returns: A list which contains the text of all displayed labels belonging to checkboxes in the legend.

        :raises TimeoutException: If no checkboxes (or labels) are displayed,
        """
        # checkboxes have multiple <tspan> children, and we want ONLY the first one.
        try:
            return [
                checkbox.find_element(*self._CHECKBOX_LABEL_LOCATOR).text for checkbox in self._checkboxes.find_all()]
        except TimeoutException as toe:
            raise TimeoutException(msg="No checkbox labels are present.") from toe

    def get_pie_slice_count(self) -> int:
        """
        Obtain a count of displayed pie slices.

        :returns: A count of pie slices displayed to the user.
        """
        try:
            return len(self._sections.find_all())
        except TimeoutException:
            return 0

    def has_title(self) -> bool:
        """
        Determine if the Pie Chart is displaying a title.

        :returns: True, if the Pie Chart is currently displaying a title - False otherwise.
        """
        try:
            return self._title.find() is not None
        except TimeoutException:
            return False

    def legend_is_displayed(self) -> bool:
        """
        Determine if the Pie Chart is displaying a legend.

        :returns: True, if the Pie Chart is currently displaying a legend - False otherwise.
        """
        try:
            return self._legend_container.find().is_displayed()
        except TimeoutException:
            return False

    def pie_slice_labels_are_displayed(self) -> bool:
        """
        Determine if pie slices are displaying labels.

        :returns: True, if pie slices are currently displaying labels - False otherwise.
        """
        # We can't follow the normal pattern here because we specifically need the 0th instance of the 5th child.
        sections = ComponentPiece(
            locator=(By.CSS_SELECTOR, 'g[aria-label="Series"] > g > g:nth-child(5)'),
            driver=self.driver,
            parent_locator_list=self.locator_list,
            wait_timeout=1,
            poll_freq=self.poll_freq)
        try:
            return len(sections.find_all()[0].find_elements(By.CSS_SELECTOR, 'tspan')) > 0
        except TimeoutException:
            return False
        except NoSuchElementException:
            return False
