from typing import List, Optional, Tuple, Union

from selenium.common.exceptions import TimeoutException, NoSuchAttributeException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.select import Select

from Components.BasicComponent import ComponentPiece, BasicPerspectiveComponent
from Components.PerspectiveComponents.Common.ComponentModal import ComponentModal
from Components.PerspectiveComponents.Common.DateTimePicker import CommonDateTimePicker, PerspectiveDate


class DateTimePicker(CommonDateTimePicker, BasicPerspectiveComponent):
    """A Perspective DateTime Picker - distinct from the DateTime Input."""

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 2,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        CommonDateTimePicker.__init__(
            self,
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
        BasicPerspectiveComponent.__init__(
            self,
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)

    def get_selected_day(self) -> Optional[int]:
        """
        Obtain the currently selected day of the DateTime Picker.

        :returns: The currently selected day of the DateTime Picker, or None if no day is selected.
        """
        try:
            # use inherited function which in this case should only return a list with one day.
            return int(self.get_selected_days()[0])
        except IndexError:
            return None

    def is_in_date_time_mode(self) -> bool:
        """
        Determine if the DateTime Picker is currently displaying the hours/minutes inputs.

        :returns: True, if the DateTime Picker is currently displaying the hours and minutes input fields - False
            otherwise.
        """
        try:
            return self._hours_input.find(wait_timeout=0) is not None and \
                self._minutes_input.find(wait_timeout=0) is not None
        except TimeoutException:
            return False

    def is_seconds_input_displayed(self) -> bool:
        """
        Determine if the DateTime Picker is currently displaying the input for seconds.

        :returns: True, if the seconds input field is displayed - False otherwise.
        """
        try:
            return self._seconds_input.find(0) is not None
        except TimeoutException:
            return False


class DateTimeInput(BasicPerspectiveComponent):
    """A Perspective DateTime Input - distinct from the DateTime Picker."""
    _TIME_CLASS = 'iaTimePickerInput--wrapper'
    _PICKER_LOCATOR = (By.CSS_SELECTOR, "div.ia_dateTimePicker")
    _INPUT_LOCATOR = (By.TAG_NAME, "input")
    _LOCAL_HOURS_INPUT_LOCATOR = (By.CSS_SELECTOR, "")
    _LOCAL_MINUTES_INPUT_LOCATOR = (By.CSS_SELECTOR, "")
    _LOCAL_AM_PM_SELECT_LOCATOR = (By.CSS_SELECTOR, "")

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            wait_timeout: float = 2,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
            poll_freq=poll_freq)
        # picker is in a modal
        self._picker = DateTimePicker(
            locator=self._PICKER_LOCATOR,
            driver=driver,
            parent_locator_list=ComponentModal(
                driver=driver).locator_list,
            wait_timeout=wait_timeout,
            poll_freq=poll_freq)
        self._input = ComponentPiece(
            locator=self._INPUT_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._local_hours_input = ComponentPiece(
            locator=self._LOCAL_HOURS_INPUT_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._local_minutes_input = ComponentPiece(
            locator=self._LOCAL_MINUTES_INPUT_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._local_am_pm_select = ComponentPiece(
            locator=self._LOCAL_AM_PM_SELECT_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)

    def click_next_month(self) -> None:
        """
        Click the next month chevron/arrow.
        """
        self.expand()
        self._picker.click_next_month()

    def click_previous_month(self) -> None:
        """
        Click the previous month chevron/arrow.
        """
        self.expand()
        self._picker.click_previous_month()

    def expand(self) -> None:
        """
        Expands the DateTime Input so that the DateTime Picker is displayed.
        """
        if not self.is_expanded() and not self.is_in_time_mode():
            self._input.click(binding_wait_time=0.5)

    def get_available_months_from_dropdown(self) -> List[str]:
        """
        Return the months available for selection as their full string names (ie: 'January' instead of 1 or 0 or 'Jan').

        :returns: A list of the available months as strings.
        """
        self._expand_and_then_collapse_when_done()
        return self._picker.get_list_of_available_months()

    def get_available_years_from_dropdown(self) -> List[int]:
        self._expand_and_then_collapse_when_done()
        return self._picker.get_list_of_available_years()

    def get_am_pm(self) -> str:
        """
        Obtain the current meridiem (AM or PM).

        :returns: 'AM' or 'PM'

        :raises TimeoutException: if the DateTime Input is using a format which does not support AM/PM.
        """
        if self.is_in_time_mode():
            return self._get_am_pm_from_local_select()
        else:
            self._expand_and_then_collapse_when_done()
            return self._get_am_pm()

    def get_hours(self) -> int:
        """
        Obtain the hours in use by the DateTime Input.
        """
        if self.is_in_time_mode():
            return self._get_hours_from_local_hours_input()
        else:
            self._expand_and_then_collapse_when_done()
            return self._get_hours()

    def get_minutes(self) -> int:
        """
        Obtain the minutes in use by the DateTime Input.
        """
        if self.is_in_time_mode():
            return self._get_minutes_from_local_minutes_input()
        else:
            self._expand_and_then_collapse_when_done()
            return self._get_minutes()

    def get_placeholder(self) -> Optional[str]:
        """
        Obtain the placeholder text currently displayed in the DateTime Input.

        :returns: The currently displayed placeholder text. A value of None means the component already has a date
            selected and so no placeholder text is being displayed.
        """
        self._collapse()
        try:
            return self._input.find().get_attribute(name="placeholder")
        except NoSuchAttributeException:
            return None

    def get_selected_days(self) -> Optional[List[int]]:
        """
        Obtain a list of selected days.

        :returns: A list of all days currently selected. For ranges, this includes all days between the first and last.
            A value of None means no days are selected.
        """
        self._expand_and_then_collapse_when_done()
        return self._picker.get_selected_days()

    def get_selected_month(self) -> str:
        """
        Obtains the month currently in use for the DateTime Input.
        """
        self._expand_and_then_collapse_when_done()
        return self.get_selected_month()

    def get_selected_year(self) -> int:
        """
        Obtain the currently selected year of the DateTime Input.
        """
        self._expand_and_then_collapse_when_done()
        return self.get_selected_year()

    def get_text(self) -> str:
        """
        The DateTime Input component does not emit text, so we return the 'value' attribute.
        """
        return self.get_value_from_input()

    def get_value_from_input(self) -> str:
        """
        Obtain the formatted string value of the DateTime Input.

        :returns: A formatted string which represents he currently selected date/time of the DateTime Input.
        """
        self._collapse()
        return self._input.find().get_attribute(name="value")

    def has_placeholder(self) -> bool:
        """
        Determine if the DateTime Input is currently displaying placeholder text.

        :returns: True, if placeholder text is displayed - False otherwise.
        """
        try:
            potential_placeholder = self.get_placeholder()
            return potential_placeholder is not None and len(potential_placeholder) > 0
        except NoSuchAttributeException:
            return False

    def is_enabled(self) -> bool:
        """
        Determine if the DateTime Input is currently enabled.

        :returns: True, if currently enabled - False otherwise.
        """
        return self._local_hours_input.find().is_enabled() \
            if self.is_in_time_mode() else self._input.find().is_enabled()

    def is_expanded(self) -> bool:
        """
        Determine if the DateTime Input is currently displaying its 'picker'.

        :returns: True, if the picker is displayed
        """
        try:
            return self._picker.find(wait_timeout=0.5) is not None
        except TimeoutException:
            return False

    def is_in_date_mode(self) -> bool:
        """
        Determine if the DateTime Input is currently configured to only allow for selecting year/month/day.

        :returns: True, if a user would only be able to select the year, month, and day. False if the user would be able
            to select any piece of time (hour, minute, or second).
        """
        return (not self.is_in_time_mode()) and (not self._is_in_date_time_mode())

    def is_in_date_time_mode(self) -> bool:
        """
        Determine if a user would be able to select the year, month, day and ANY piece of time for a date.

        :returns: True, if a user can select a year, month, day and ANY piece of time (hours, minutes, or seconds).
        """
        return (not self.is_in_time_mode()) and self._is_in_date_time_mode()

    def is_in_time_mode(self) -> bool:
        """
        Determine if the DateTime Input only allows for selecting time values.

        :returns: True, if only time values are available for modification. False if a user would be able to select the
            year, month, or day.
        """
        return self._TIME_CLASS in self.find().find_elements(By.XPATH, 'child::*')[0].get_attribute('class')

    def select_date(self, date: PerspectiveDate, collapse_when_done: bool = True) -> None:
        """
        Select a date within the DateTime Input

        :param date: The date to select.
        :param collapse_when_done: If True, the picker will be collapsed when done. If False, the picker will be left
            expanded.
        """
        self.expand()
        self._picker.select_date_only_not_time(date=date)
        if date.hours12 or date.hours24 or date.minutes or date.seconds:
            # re-expand after potentially selecting a day
            self.expand()
            self._picker.select_time_only_not_date(date=date)
            if not self.is_expanded():
                self.click()
            self._picker.select_date_only_not_time(date=PerspectiveDate(day=date.day))
        if collapse_when_done:
            self._collapse()

    def select_month(self, month: Union[int, str]) -> None:
        """
        Select a month within the DateTime Input.

        :param month: The month to select by clicking the previous/next chevrons/arrows.
        """
        self.expand()
        self._picker.select_month(month=month)

    def select_year(self, year: Union[int, str]) -> None:
        """
        Select a year within the DateTime Input.

        :param year: The four-digit numeric year you would like to select by clicking the previous/next chevrons/arrows.
        """
        self.expand()
        self._picker.select_year(year=year)

    def _collapse(self) -> None:
        """
        Collapse the DateTime Picker. Takes no action if the picker modal is not displayed.
        """
        if self.is_expanded():
            self.click()

    def _get_am_pm(self) -> Optional[str]:
        """
        Obtain the current meridiem.

        :returns: 'am' or 'pm' while the DateTime Input is using a 12-hour format.

        :raises TimeoutException: If the format of the input is such that the AM/PM picker is not present.
        """
        self._expand_and_then_collapse_when_done()
        return self._picker.get_am_pm()

    def _get_hours(self) -> int:
        """
        Obtain the currently selected hours of the DateTime Input.

        :raises TimeoutException: If the format of the input is such that the hours input is not present.
        """
        self._expand_and_then_collapse_when_done()
        return self._picker.get_hours()

    def _get_minutes(self) -> int:
        """
        Obtain the currently selected minutes of the DateTime Input.

        :raises TimeoutException: If the format of the input is such that the minutes input is not present.
        """
        self._expand_and_then_collapse_when_done()
        return self._picker.get_minutes()

    def _is_in_date_time_mode(self) -> bool:
        """
        Determine if the DateTime Input is currently displaying the ability to select years, months, days and any
        piece of time.

        :returns: True, if the user may apply year, month, day, and at least one from among hours, minutes, or
            seconds. False, if the user may not select any piece of time, or does not have the ability to apply year,
            month or day.
        """
        self._expand_and_then_collapse_when_done()
        return self._picker.is_in_date_time_mode()

    def _collapse_during_teardown_if_was_not_expanded(self) -> None:
        """
        Convenience function to deterministically collapse the expanded picker only if it was not open to begin with.
        """
        expanded_originally = self.is_expanded()
        self.expand()
        yield
        if not expanded_originally:
            self._collapse()

    def _expand_and_then_collapse_when_done(self) -> None:
        """
        Convenience function to first expand the picker, and then force collapse after task completion.
        """
        self.expand()
        self._collapse_during_teardown_if_was_not_expanded()

    def _get_am_pm_from_local_select(self) -> str:
        """
        Obtain the current meridiem ('am' or 'pm').

        :returns: 'AM' or 'PM'

        :raises TimeoutException: If using a time format which does not support AM/PM.
        """
        return Select(webelement=self._local_am_pm_select.find()).all_selected_options[0].text

    def _get_hours_from_local_hours_input(self) -> int:
        """
        Obtain the hours currently applied to the DateTime Input while in 'time' mode.

        :raises TimeoutException: If the DateTime Input is not in 'time' mode.
        """
        return int(self._local_hours_input.find().get_attribute(name="value"))

    def _get_minutes_from_local_minutes_input(self) -> int:
        """
        Obtain the minutes currently applied to the DateTime Input while in 'time' mode.

        :raises TimeoutException: If the DateTime Input is not in 'time' mode.
        """
        return int(self._local_minutes_input.find().get_attribute(name="value"))
