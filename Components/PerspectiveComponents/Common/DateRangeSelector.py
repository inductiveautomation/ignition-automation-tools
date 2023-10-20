from enum import Enum
from typing import Optional, Union, List, Tuple

from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.select import Select

from Components.BasicComponent import ComponentPiece
from Components.Common.Button import CommonButton
from Components.PerspectiveComponents.Common.ComponentModal import ComponentModal
from Components.PerspectiveComponents.Common.DateTimePicker import CommonDateTimePicker, PerspectiveDate
from Components.PerspectiveComponents.Common.Icon import CommonIcon
from Helpers.IAAssert import IAAssert


class DateRangeSelectorTab(Enum):
    HISTORICAL = "historical"
    REALTIME = "realtime"


class DateRangeSelectorTimeUnit(Enum):
    DAYS = "days"
    HOURS = "hours"
    MINUTES = "minutes"
    SECONDS = "seconds"
    WEEKS = "weeks"
    YEARS = "years"


class HistoricalRange:

    def __init__(
            self,
            beginning_day: Optional[Union[int, str]] = None,
            beginning_month: Optional[Union[int, str]] = None,
            beginning_year: Optional[Union[int, str]] = None,
            beginning_hours: Optional[Union[int, str]] = None,
            beginning_minutes: Optional[Union[int, str]] = None,
            beginning_am: Optional[bool] = None,
            ending_day: Optional[Union[int, str]] = None,
            ending_month: Optional[Union[int, str]] = None,
            ending_year: Optional[Union[int, str]] = None,
            ending_hours: Optional[Union[int, str]] = None,
            ending_minutes: Optional[Union[int, str]] = None,
            ending_am: Optional[bool] = None):
        self.beginning_day = beginning_day
        self.beginning_month = beginning_month
        self.beginning_year = beginning_year
        self.beginning_hours = beginning_hours
        self.beginning_minutes = beginning_minutes
        self.beginning_am = beginning_am
        self.ending_day = ending_day
        self.ending_month = ending_month
        self.ending_year = ending_year
        self.ending_hours = ending_hours
        self.ending_minutes = ending_minutes
        self.ending_am = ending_am


class CommonDateRangeSelector(ComponentModal):
    """
    The DateRange Selector used in multiple larger components, including the Alarm Journal Table, the Power Chart, and
    During filtering of Table columns which render as a date.

    In some cases the range selector may change between a Historical 'Picker' which allows for specifying a beginning
    date/time and an ending date/time, or a Realtime range selector which allows for specifying a range of time before
    the current time, where a value of '8 Hours' would specify a range of anything between 'now and 8 hours ago'.

    Use of the Historical picker requires the presence of the default chevrons/arrows/spinners.
    """

    class _HistoricalPicker(CommonDateTimePicker):
        """
        The Historical Picker piece of the Range Selector. Interaction with this component with Selenium requires use
        of the chevrons/arrows/spinners; this class will not work if those pieces are removed through CSS styling.
        """

        _CLEAR_HISTORICAL_ICON_LOCATOR = (By.CSS_SELECTOR, "div.clear-icon")
        _AM_PM_SELECTS_LOCATOR = (By.CSS_SELECTOR, "div.timePickerAmPmPicker select")
        _APPLY_BUTTON_LOCATOR = (By.CSS_SELECTOR, f"button.{CommonButton.PRIMARY_CLASS}")
        _CANCEL_BUTTON_LOCATOR = (By.CSS_SELECTOR, f"button.{CommonButton.SECONDARY_CLASS}")
        _ACTIVE_DAYS_LOCATOR = (By.CSS_SELECTOR, "div.dayTile.active")  # active means "this month", not "enabled"
        _END_TIME_INPUT_CONTAINER_LOCATOR = (By.CSS_SELECTOR, 'div.timeInputContainer[data-end-time="true"]')
        _START_TIME_INPUT_CONTAINER_LOCATOR = (By.CSS_SELECTOR, 'div.timeInputContainer[data-start-time="true"]')
        _TIME_PICKER_RANGE_INFO_TEXT_LOCATOR = (By.CSS_SELECTOR, "div.ia_dateRangeTimePicker__rangeInfo")
        _SELECTED_START_AND_END_DATES_DATE_RANGE_LOCATOR = (By.CSS_SELECTOR, "div.node")
        _BEGINNING_INDEX = 0
        _ENDING_INDEX = 1

        def __init__(
                self,
                driver: WebDriver,
                description: Optional[str] = None,
                poll_freq: float = 0.5):
            super().__init__(
                locator=(By.CSS_SELECTOR, 'div[class*="iaDateRange"]'),
                driver=driver,
                parent_locator_list=ComponentModal(driver=driver).locator_list,
                description=description,
                poll_freq=poll_freq)
            self._next_month_chevron = ComponentPiece(
                locator=self._NEXT_MONTH_CHEVRON_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)
            self._previous_month_chevron = ComponentPiece(
                locator=self._PREVIOUS_MONTH_CHEVRON_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)
            self._clear_link = ComponentPiece(
                locator=self._CLEAR_RANGE_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)
            self._month_dropdown = ComponentPiece(
                locator=self._MONTH_SELECT_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)
            self._year_dropdown = ComponentPiece(
                locator=self._YEAR_SELECT_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)
            self._active_days = ComponentPiece(
                locator=self._ACTIVE_DAYS_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)
            self._clear_icon = ComponentPiece(
                locator=self._CLEAR_HISTORICAL_ICON_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list)
            self._start_time_input_container = ComponentPiece(
                locator=self._START_TIME_INPUT_CONTAINER_LOCATOR, driver=driver, parent_locator_list=self.locator_list)
            self._start_time_hour_input = ComponentPiece(
                locator=self._HOURS_INPUT_LOCATOR, 
                driver=driver, 
                parent_locator_list=self._start_time_input_container.locator_list)
            self._start_time_minute_input = ComponentPiece(
                locator=self._MINUTES_INPUT_LOCATOR, 
                driver=driver, 
                parent_locator_list=self._start_time_input_container.locator_list)
            self._start_time_second_input = ComponentPiece(
                locator=self._SECONDS_INPUT_LOCATOR,
                driver=driver,
                parent_locator_list=self._start_time_input_container.locator_list)
            self._start_time_next_hour_spinner = ComponentPiece(
                locator=self._NEXT_HOUR_SPINNER_LOCATOR, 
                driver=driver, 
                parent_locator_list=self._start_time_input_container.locator_list)
            self._start_time_next_minute_spinner = ComponentPiece(
                locator=self._NEXT_MINUTE_SPINNER_LOCATOR, 
                driver=driver, 
                parent_locator_list=self._start_time_input_container.locator_list)
            self._start_time_next_second_spinner = ComponentPiece(
                locator=self._NEXT_SECOND_SPINNER_LOCATOR, 
                driver=driver, 
                parent_locator_list=self._start_time_input_container.locator_list)
            self._start_time_previous_hour_spinner = ComponentPiece(
                locator=self._PREVIOUS_HOUR_SPINNER_LOCATOR, 
                driver=driver, 
                parent_locator_list=self._start_time_input_container.locator_list)
            self._start_time_previous_minute_spinner = ComponentPiece(
                locator=self._PREVIOUS_MINUTE_SPINNER_LOCATOR, 
                driver=driver, 
                parent_locator_list=self._start_time_input_container.locator_list)
            self._start_time_previous_second_spinner = ComponentPiece(
                locator=self._PREVIOUS_SECOND_SPINNER_LOCATOR, 
                driver=driver, 
                parent_locator_list=self._start_time_input_container.locator_list)
            self._start_time_am_pm_select = ComponentPiece(
                locator=self._AM_PM_SELECTS_LOCATOR,
                driver=driver,
                parent_locator_list=self._start_time_input_container.locator_list,
                wait_timeout=1)
            self._end_time_input_container = ComponentPiece(
                locator=self._END_TIME_INPUT_CONTAINER_LOCATOR, driver=driver, parent_locator_list=self.locator_list)
            self._end_time_hour_input = ComponentPiece(
                locator=self._HOURS_INPUT_LOCATOR, 
                driver=driver, 
                parent_locator_list=self._end_time_input_container.locator_list)
            self._end_time_minute_input = ComponentPiece(
                locator=self._MINUTES_INPUT_LOCATOR, 
                driver=driver, 
                parent_locator_list=self._end_time_input_container.locator_list)
            self._end_time_second_input = ComponentPiece(
                locator=self._SECONDS_INPUT_LOCATOR,
                driver=driver,
                parent_locator_list=self._end_time_input_container.locator_list)
            self._end_time_next_hour_spinner = ComponentPiece(
                locator=self._NEXT_HOUR_SPINNER_LOCATOR, 
                driver=driver, 
                parent_locator_list=self._end_time_input_container.locator_list)
            self._end_time_next_minute_spinner = ComponentPiece(
                locator=self._NEXT_MINUTE_SPINNER_LOCATOR, 
                driver=driver, 
                parent_locator_list=self._end_time_input_container.locator_list)
            self._end_time_next_second_spinner = ComponentPiece(
                locator=self._NEXT_SECOND_SPINNER_LOCATOR, 
                driver=driver, 
                parent_locator_list=self._end_time_input_container.locator_list)
            self._end_time_previous_hour_spinner = ComponentPiece(
                locator=self._PREVIOUS_HOUR_SPINNER_LOCATOR, 
                driver=driver, 
                parent_locator_list=self._end_time_input_container.locator_list)
            self._end_time_previous_minute_spinner = ComponentPiece(
                locator=self._PREVIOUS_MINUTE_SPINNER_LOCATOR, 
                driver=driver, 
                parent_locator_list=self._end_time_input_container.locator_list)
            self._end_time_previous_second_spinner = ComponentPiece(
                locator=self._PREVIOUS_SECOND_SPINNER_LOCATOR, 
                driver=driver, 
                parent_locator_list=self._end_time_input_container.locator_list)
            self._end_time_am_pm_select = ComponentPiece(
                locator=self._AM_PM_SELECTS_LOCATOR,
                driver=driver,
                parent_locator_list=self._end_time_input_container.locator_list,
                wait_timeout=1,
                poll_freq=poll_freq)
            self._time_picker_range_info_text = ComponentPiece(
                locator=self._TIME_PICKER_RANGE_INFO_TEXT_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)
            self._selected_start_and_end_dates_calendar_values = ComponentPiece(
                locator=self._SELECTED_START_AND_END_DATES_DATE_RANGE_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)

        def click_clear(self) -> None:
            """
            Click the 'clear' link in the Historical tab.

            :raises TimeoutException: If the clear link is not present. Verify you are using the Historical tab and not
                the Realtime range tab.
            """
            self._clear_link.click(wait_timeout=0.5)

        def click_historical_day(self, numeric_day: Union[int, str]) -> None:
            """
            Click a numeric day of the current month.

            :param numeric_day: The number of the day to click.

            :raises AssertionError: If the specified day was not selected.
            :raises TimeoutException: If the clear link is not present. Verify you are using the Historical tab and not
                the Realtime range tab.
            """
            self.select_date(date=PerspectiveDate(day=numeric_day))
            IAAssert.contains(
                iterable=[int(_) for _ in self.get_selected_days()],
                expected_value=int(numeric_day),
                failure_msg=f"Failed to select '{numeric_day}' as part of a Historical range.")

        def day_is_node_of_range(self, numeric_day: Union[int, str]) -> bool:
            """
            Determine if the specified day is the beginning or end day of the current Historical range.

            :param numeric_day: The day which is to be checked as a terminus of the range.

            :returns: True, if the supplied numeric_day is either the beginning day or the ending day of the current
                Historic range. False, if the numeric_day is within the current range or is not a part of the range.
            """
            return "node" in self._get_day_tile(numeric_day=numeric_day).find().get_attribute("class")

        def day_is_within_current_range(self, numeric_day: Union[int, str]) -> bool:
            """
            Determine if the supplied day is the beginning day, ending day, or any day in-between those days for the
            currently selected Historical range.

            :param numeric_day: The day which is to be checked for inclusion in the range.

            :returns: True, if the supplied day falls anywhere within the current Historical range - False otherwise.
            """
            return self.day_is_node_of_range(numeric_day=numeric_day) or \
                "range" in self._get_day_tile(numeric_day=numeric_day).find().get_attribute("class")
                
        def end_time_hour_input_is_displayed(self) -> bool:
            """
            Determine if the hours input is displayed for the 'ending' time.

            :returns: True, if the hours input is displayed for the ending time of the range - False otherwise.

            :raises TimeoutException: If the hours input is not present.
            """
            return self._end_time_hour_input.find().is_displayed()
                
        def end_time_minute_input_is_displayed(self) -> bool:
            """
            Determine if the minutes input is displayed for the 'ending' time.

            :returns: True, if the minutes input is displayed for the ending time of the range - False otherwise.

            :raises TimeoutException: If the minutes input is not present.
            """
            return self._end_time_minute_input.find().is_displayed()
                
        def end_time_second_input_is_displayed(self) -> bool:
            """
            Determine if the seconds input is displayed for the 'ending' time.

            Note: Date Range Selector does not support seconds as of 8.1.22, so this will always throw a
            TimeoutException.

            :returns: True, if the seconds input is displayed for the ending time of the range - False otherwise.

            :raises TimeoutException: If the seconds input is not present.
            """
            return self._end_time_second_input.find().is_displayed()
                
        def end_time_hour_input_is_enabled(self) -> bool:
            """
            Determine if the hours input is enabled for the 'ending' time.

            :returns: True, if the hours input is enabled for the ending time of the range - False otherwise.

            :raises TimeoutException: If the hours input is not present.
            """
            return self._end_time_hour_input.find().is_enabled()
                
        def end_time_minute_input_is_enabled(self) -> bool:
            """
            Determine if the minutes input is enabled for the 'ending' time.

            :returns: True, if the minutes input is enabled for the ending time of the range - False otherwise.

            :raises TimeoutException: If the minutes input is not present.
            """
            return self._end_time_minute_input.find().is_enabled()
                
        def end_time_second_input_is_enabled(self) -> bool:
            """
            Determine if the seconds input is enabled for the 'ending' time.

            Note: Date Range Selector does not support seconds as of 8.1.22, so this will always throw a
            TimeoutException.

            :returns: True, if the seconds input is enabled for the ending time of the range - False otherwise.

            :raises TimeoutException: If the seconds input is not present.
            """
            return self._end_time_second_input.find().is_enabled()

        def get_current_range(self) -> Optional[HistoricalRange]:
            """
            Obtain the current Historical range.

            Currently only supports ranges within a single month, and formats which use 12-hour times.

            :returns: The currently applied Historical Range if one is fully applied, or None if a valid Historical
                Range is not currently applied or if the range begins and ends in different months.
            """
            try:
                _active_days = self._active_days.find_all()
                beginning_day = _active_days[0].text
                ending_day = _active_days[-1].text
                month = self.get_selected_month()
                year = self.get_selected_year()
                return HistoricalRange(
                    beginning_day=beginning_day,
                    beginning_month=month,
                    beginning_year=year,
                    beginning_hours=self._start_time_hour_input.get_text(),
                    beginning_minutes=self._start_time_minute_input.get_text(),
                    beginning_am=Select(webelement=self._start_time_am_pm_select.find()).first_selected_option == "am",
                    ending_day=ending_day,
                    ending_month=month,
                    ending_year=year,
                    ending_hours=self._end_time_hour_input.get_text(),
                    ending_minutes=self._end_time_minute_input.get_text(),
                    ending_am=Select(webelement=self._end_time_am_pm_select.find()).first_selected_option == "am")
            except IndexError:
                # possible if only one day has been selected, or if our range spans more than one month
                return None

        def get_selected_start_and_end_days_from_date_range_selector(self) -> List[int]:
            """
            Obtain the currently selected beginning and end days of the Historical range.

            Note: This only returns days of the current calendar month, so ranges which span months will only return
            one day.

            :returns: The beginning and end days of the current Historical range, where the
                first element in the list is the start day and the second element is the end day.
            """
            try:
                return [int(_.text) for _ in self._selected_start_and_end_dates_calendar_values.find_all()]
            except TimeoutException:
                return []

        def get_time_picker_range_info_text(self) -> str:
            """
            Obtain the start and end dates of the currently applied Historical range as the user would see them.

            :returns: The displayed formatted date range (sans time) as the user sees it.
            """
            return self._time_picker_range_info_text.get_text()

        def is_displayed(self) -> bool:
            """
            Determine if the Historical range picker is currently displayed to the user.

            :returns: True, if the picker is present - False otherwise.
            """
            try:
                return self.find(wait_timeout=0.5) is not None
            except TimeoutException:
                return False

        def set_end_time(self, date: PerspectiveDate) -> None:
            """
            Set the ending time to use for the Historical range.

            :param date: A PerspectiveDate object from which we will only use the time aspects.

            :raises AssertionError: If any of the end time values do not match what is supplied after attempting to
                apply them.
            """
            am_pm_found = False
            if date.hours24 and self._end_time_hour_input.find().is_enabled():
                try:
                    # this picker determines our input approach (12 vs 24 hour)
                    am_pm_found = self._end_time_am_pm_select.find() is not None
                    target_value = date.hours12
                except TimeoutException:
                    # 24-hour format
                    am_pm_found = False
                    target_value = date.hours24
                self._set_end_hours(target_value=target_value)
            if date.minutes and self._end_time_minute_input.find().is_enabled():
                self._set_end_minutes(target_value=date.minutes)
            if am_pm_found:
                Select(webelement=self._end_time_am_pm_select.find()).select_by_value(value=date.am_pm)
            # assert new settings were applied
            if date.hours24 is not None:
                IAAssert.is_equal_to(
                    actual_value=self._end_time_hour_input.find().get_attribute("value"),
                    expected_value=date.hours12 if am_pm_found else date.hours24,
                    as_type=int,
                    failure_msg="Failed to set the hours for the end time.")
            if date.minutes is not None:
                IAAssert.is_equal_to(
                    actual_value=self._end_time_minute_input.find().get_attribute("value"),
                    expected_value=date.minutes,
                    as_type=int,
                    failure_msg="Failed to set the minutes for the end time.")
            if date.am_pm and date.am_pm is not None:
                IAAssert.is_equal_to(
                    actual_value=Select(
                        webelement=self._end_time_am_pm_select.find()).first_selected_option.text.upper(),
                    expected_value=date.am_pm.upper(),
                    as_type=str,
                    failure_msg="Failed to set AM/PM for the end time.")

        def set_range(self, historical_range: HistoricalRange) -> None:
            """
            Set the Historical range by specifying all time pieces of both the beginning and end dates.

            :param historical_range: A HistoricalRange object containing information about both the start date/time and
                end date/time for the desired range.

            :raises AssertionError: If unsuccessful in applying any of the range values.
            """
            _beginning_hours = 0
            _ending_hours = 0
            if historical_range.beginning_hours is not None:
                _beginning_hours = int(historical_range.beginning_hours)
            if not historical_range.beginning_am:
                _beginning_hours += 12
            if historical_range.ending_hours is not None:
                _ending_hours = int(historical_range.ending_hours)
            if not historical_range.ending_am:
                _ending_hours += 12
            beginning_date = PerspectiveDate(
                year=historical_range.beginning_year,
                month=historical_range.beginning_month,
                day=historical_range.beginning_day,
                hours24=_beginning_hours,
                minutes=historical_range.beginning_minutes)
            ending_date = PerspectiveDate(
                year=historical_range.ending_year,
                month=historical_range.ending_month,
                day=historical_range.ending_day,
                hours24=_ending_hours,
                minutes=historical_range.ending_minutes)
            self.select_date_only_not_time(date=beginning_date)
            self.select_date_only_not_time(date=ending_date)
            self.set_start_time(date=beginning_date)
            self.set_end_time(date=ending_date)

        def set_start_time(self, date: PerspectiveDate) -> None:
            """
            Set the starting time to use for the Historical range.

            :param date: A PerspectiveDate object from which we will only use the time aspects.

            :raises AssertionError: If any of the end time values do not match what is supplied after attempting to
                apply them.
            """
            am_pm_found = False
            if date.hours24 and self._start_time_hour_input.find().is_enabled():
                try:
                    # this picker determines our input approach (12 vs 24 hour)
                    am_pm_found = self._start_time_am_pm_select.find() is not None
                    target_value = date.hours12
                except TimeoutException:
                    # 24-hour format
                    am_pm_found = False
                    target_value = date.hours24
                self._set_start_hours(target_value=target_value)
            if date.minutes and self._start_time_minute_input.find().is_enabled():
                self._set_start_minutes(target_value=date.minutes)
            if am_pm_found:
                Select(webelement=self._start_time_am_pm_select.find()).select_by_value(value=date.am_pm)
            # assert new settings were applied
            if date.hours24 is not None:
                IAAssert.is_equal_to(
                    actual_value=self._start_time_hour_input.find().get_attribute("value"),
                    expected_value=date.hours12 if am_pm_found else date.hours24,
                    as_type=int,
                    failure_msg="Failed to set the hours for the start time.")
            if date.minutes is not None:
                IAAssert.is_equal_to(
                    actual_value=self._start_time_minute_input.find().get_attribute("value"),
                    expected_value=date.minutes,
                    as_type=int,
                    failure_msg="Failed to set the minutes for the start time.")
            if am_pm_found and date.am_pm is not None:
                IAAssert.is_equal_to(
                    actual_value=Select(
                        webelement=self._start_time_am_pm_select.find()).first_selected_option.text.upper(),
                    expected_value=date.am_pm.upper(),
                    as_type=str,
                    failure_msg="Failed to set AM/PM for the start time.")
                
        def start_time_hour_input_is_displayed(self) -> bool:
            """
            Determine if the hours input for the starting time is displayed.

            :returns: True, if the hours input of the starting time is displayed - False otherwise.

            :raises TimeoutException: If the hours input of the starting time is not present.
            """
            return self._start_time_hour_input.find().is_displayed()
                
        def start_time_minute_input_is_displayed(self) -> bool:
            """
            Determine if the minutes input for the starting time is displayed.

            :returns: True, if the minutes input of the starting time is displayed - False otherwise.

            :raises TimeoutException: If the minutes input of the starting time is not present.
            """
            return self._start_time_minute_input.find().is_displayed()
                
        def start_time_second_input_is_displayed(self) -> bool:
            """
            Determine if the seconds input for the starting time is displayed.

            :returns: True, if the seconds input of the starting time is displayed - False otherwise.

            :raises TimeoutException: If the seconds input of the starting time is not present.
            """
            return self._start_time_second_input.find().is_displayed()
                
        def start_time_hour_input_is_enabled(self) -> bool:
            """
            Determine if the hours input for the starting time is enabled.

            :returns: True, if the hours input of the starting time is enabled - False otherwise.

            :raises TimeoutException: If the hours input of the starting time is not present.
            """
            return self._start_time_hour_input.find().is_enabled()
                
        def start_time_minute_input_is_enabled(self) -> bool:
            """
            Determine if the minutes input for the starting time is enabled.

            :returns: True, if the minutes input of the starting time is enabled - False otherwise.

            :raises TimeoutException: If the minutes input of the starting time is not present.
            """
            return self._start_time_minute_input.find().is_enabled()
                
        def start_time_second_input_is_enabled(self) -> bool:
            """
            Determine if the seconds input for the starting time is enabled.

            :returns: True, if the seconds input of the starting time is enabled - False otherwise.

            :raises TimeoutException: If the seconds input of the starting time is not present.
            """
            return self._start_time_second_input.find().is_enabled()
                
        def _set_end_hours(self, target_value: int) -> None:
            """
            Set the ending hours of the Historical range by clicking the chevrons/arrows.

            :param target_value: The desired hours to apply as part of the ending date.

            :raises AssertionError: If unsuccessful in applying the supplied target_value.
            """
            current_hours = int(self._end_time_hour_input.find().get_attribute("value"))
            if target_value != current_hours:
                while current_hours < target_value:
                    self._end_time_next_hour_spinner.click()
                    current_hours = int(self._end_time_hour_input.find().get_attribute("value"))
                while current_hours > target_value:
                    self._end_time_previous_hour_spinner.click()
                    current_hours = int(self._end_time_hour_input.find().get_attribute("value"))
            IAAssert.is_equal_to(
                actual_value=current_hours,
                expected_value=target_value,
                as_type=int,
                failure_msg=f"failed to set the ending hours ({target_value}) for the range.")
                    
        def _set_end_minutes(self, target_value: int) -> None:
            """
            Set the ending minutes of the Historical range by clicking the chevrons/arrows.

            :param target_value: The desired minutes to apply as part of the ending date.

            :raises AssertionError: If unsuccessful in applying the supplied target_value.
            """
            current_minutes = int(self._end_time_minute_input.find().get_attribute("value"))
            if target_value != current_minutes:
                while current_minutes < target_value:
                    self._end_time_next_minute_spinner.click()
                    current_minutes = int(self._end_time_minute_input.find().get_attribute("value"))
                while current_minutes > target_value:
                    self._end_time_previous_minute_spinner.click()
                    current_minutes = int(self._end_time_minute_input.find().get_attribute("value"))
            IAAssert.is_equal_to(
                actual_value=current_minutes,
                expected_value=target_value,
                as_type=int,
                failure_msg=f"failed to set the ending minutes ({target_value}) for the range.")
                
        def _set_start_hours(self, target_value: int) -> None:
            """
            Set the starting hours of the Historical range by clicking the chevrons/arrows.

            :param target_value: The desired hours to apply as part of the starting date.

            :raises AssertionError: If unsuccessful in applying the supplied target_value.
            """
            current_hours = int(self._start_time_hour_input.find().get_attribute("value"))
            if target_value != current_hours:
                while current_hours < target_value:
                    self._start_time_next_hour_spinner.click()
                    current_hours = int(self._start_time_hour_input.find().get_attribute("value"))
                while current_hours > target_value:
                    self._start_time_previous_hour_spinner.click()
                    current_hours = int(self._start_time_hour_input.find().get_attribute("value"))
            IAAssert.is_equal_to(
                actual_value=current_hours,
                expected_value=target_value,
                as_type=int,
                failure_msg=f"failed to set the starting hours ({target_value}) for the range.")
                    
        def _set_start_minutes(self, target_value: int) -> None:
            """
            Set the starting minutes of the Historical range by clicking the chevrons/arrows.

            :param target_value: The desired minutes to apply as part of the starting date.

            :raises AssertionError: If unsuccessful in applying the supplied target_value.
            """
            current_minutes = int(self._start_time_minute_input.find().get_attribute("value"))
            if target_value != current_minutes:
                while current_minutes < target_value:
                    self._start_time_next_minute_spinner.click()
                    current_minutes = int(self._start_time_minute_input.find().get_attribute("value"))
                while current_minutes > target_value:
                    self._start_time_previous_minute_spinner.click()
                    current_minutes = int(self._start_time_minute_input.find().get_attribute("value"))
            IAAssert.is_equal_to(
                actual_value=current_minutes,
                expected_value=target_value,
                as_type=int,
                failure_msg=f"failed to set the starting minutes ({target_value}) for the range.")

    class _RealtimeRange(ComponentModal):
        """The Realtime range piece of the Range Selector, comprised of a simple input and a Dropdown/Select."""
        _REALTIME_NUMERIC_INPUT_LOCATOR = (By.CSS_SELECTOR, 'input.realtimeContentInput')
        _REALTIME_SELECT_LOCATOR = (By.CSS_SELECTOR, 'div.realtimeUnitSelector select')
        _REALTIME_RANGE_MESSAGE_LABEL_LOCATOR = (By.CSS_SELECTOR, 'div.realtimeMessage')

        def __init__(
                self,
                driver: WebDriver,
                description: Optional[str] = None,
                poll_freq: float = 0.5):
            super().__init__(
                driver=driver,
                description=description,
                poll_freq=poll_freq)
            self._input = ComponentPiece(
                locator=self._REALTIME_NUMERIC_INPUT_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)
            self._unit_selector = ComponentPiece(
                locator=self._REALTIME_SELECT_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq)
            self._message_label = ComponentPiece(
                locator=self._REALTIME_RANGE_MESSAGE_LABEL_LOCATOR,
                driver=driver,
                parent_locator_list=self.locator_list,
                poll_freq=poll_freq
            )

        def select_realtime_unit(self, time_unit: DateRangeSelectorTimeUnit) -> None:
            """
            Select which time unit to apply as part of the Realtime range.

            :param time_unit: An enumeration of the available options to select from.

            :raises AssertionError: If unsuccessful in applying the supplied time unit.
            """
            Select(webelement=self._unit_selector.find()).select_by_value(value=time_unit.value)
            IAAssert.is_equal_to(
                actual_value=Select(webelement=self._unit_selector.find()).first_selected_option.text.upper(),
                expected_value=time_unit.value.upper(),
                as_type=str,
                failure_msg=f"Failed to apply {time_unit.value} as the time unit fr the Realtime range.")

        def set_time_value(self, time_value: int) -> None:
            """
            Set the numeric range to be used with the time unit.

            :param time_value: The amount of the time unit you desire to apply as the Realtime range.

            :raises AssertionError: If unsuccessful in applying the supplied time value.
            """
            original = self._input.find().get_attribute("value")
            text_to_set = "".join([Keys.ARROW_RIGHT * len(original), Keys.BACKSPACE * len(original), str(time_value)])
            self._input.click()
            self._input.find().send_keys(text_to_set)
            self._message_label.click(binding_wait_time=0.25)  # force the loss of focus on the input
            IAAssert.is_equal_to(
                actual_value=self._input.find().get_attribute('value'),
                expected_value=time_value,
                as_type=str,
                failure_msg="Failed to set the time value of the Realtime range.")

    ACTIVE_TAB_CLASS = "isActiveTab"
    _TOGGLE_ICON_LOCATOR = (By.CSS_SELECTOR, "svg.iaCalendarIcon")
    _MESSAGE_LOCATOR = (By.CSS_SELECTOR, '[data-message]')
    _RANGE_MESSAGE_LOCATOR = (By.CSS_SELECTOR, '[data-range-message]')
    # modal/popover locators
    _APPLY_BUTTON_LOCATOR = (By.CSS_SELECTOR, f'button.{CommonButton.PRIMARY_CLASS}')
    _CANCEL_BUTTON_LOCATOR = (By.CSS_SELECTOR, f'button.{CommonButton.SECONDARY_CLASS}')
    _POPOVER_CLOSE_ICON_LOCATOR = (By.CSS_SELECTOR, 'div.closeIcon svg')
    _HISTORICAL_TAB_LOCATOR = (By.CSS_SELECTOR, 'div.historicalTab')
    _REALTIME_TAB_LOCATOR = (By.CSS_SELECTOR, 'div.realtimeTab')
    _FOOTER_LOCATOR = (By.CSS_SELECTOR, "div.realtimeOrHistoricalRangeFooter")
    _HEADER_LOCATOR = (By.CSS_SELECTOR, 'div.realtimeOrHistoricalRangeSelectorModalHeader')
    _TAB_CONTAINER_LOCATOR = (By.CSS_SELECTOR, 'div.realtimeOrHistoricalRangeTabContainer')
    _GENERIC_TAB_LOCATOR = (By.CSS_SELECTOR, 'div.ia_realtimeOrHistoricalRange__tabContainer__tab')
    _HISTORICAL_PICKER_LOCATOR = (By.CSS_SELECTOR, 'div.iaDateRangeTimePicker')

    def __init__(
            self,
            driver: WebDriver,
            parent_locator_list: Optional[List[Tuple[By, str]]] = None,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(driver=driver, description=description)
        # toggle icon is actually part of the Power Chart component - not the Date Range Selector/modal
        self._toggle_icon = CommonIcon(
            locator=self._TOGGLE_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=parent_locator_list,
            poll_freq=poll_freq)
        self._message = ComponentPiece(
            locator=self._MESSAGE_LOCATOR,
            driver=driver,
            parent_locator_list=parent_locator_list,
            poll_freq=poll_freq)
        self._range_message = ComponentPiece(
            locator=self._RANGE_MESSAGE_LOCATOR,
            driver=driver,
            parent_locator_list=parent_locator_list,
            poll_freq=poll_freq)
        # modal content
        self._footer = ComponentPiece(
            locator=self._FOOTER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._header = ComponentPiece(
            locator=self._HEADER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._tab_container = ComponentPiece(
            locator=self._TAB_CONTAINER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._apply_button = CommonButton(
            locator=self._APPLY_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self._footer.locator_list,
            poll_freq=poll_freq)
        self._cancel_button = CommonButton(
            locator=self._CANCEL_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self._footer.locator_list,
            poll_freq=poll_freq)
        self._close_icon = CommonIcon(
            locator=self._POPOVER_CLOSE_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self._header.locator_list,
            poll_freq=poll_freq)
        self._historical_tab = ComponentPiece(
            locator=self._HISTORICAL_TAB_LOCATOR,
            driver=driver,
            parent_locator_list=self._tab_container.locator_list,
            poll_freq=poll_freq)
        self._realtime_tab = ComponentPiece(
            locator=self._REALTIME_TAB_LOCATOR,
            driver=driver,
            parent_locator_list=self._tab_container.locator_list,
            poll_freq=poll_freq)
        self._generic_tabs = ComponentPiece(
            locator=self._GENERIC_TAB_LOCATOR,
            driver=driver,
            parent_locator_list=self._tab_container.locator_list,
            poll_freq=poll_freq)
        self._historical_picker = self._HistoricalPicker(driver=driver, poll_freq=poll_freq)
        self._realtime_range = self._RealtimeRange(driver=driver, poll_freq=poll_freq)

    def apply_button_is_enabled(self) -> bool:
        """
        Determine if the Apply button is enabled.

        :returns: True, if the Apply button is enabled - False otherwise.

        :raises TimeoutException: If the Apply button is not present.
        """
        return self._apply_button.is_enabled()

    def apply_changes(self) -> None:
        """
        Click the Apply button.

        :raises TimeoutException: If the Apply button is not present.
        """
        self._apply_button.click()

    def cancel_changes(self) -> None:
        """
        Click the Cancel button.

        :raises TimeoutException: If the Cancel button is not present.
        """
        self._cancel_button.click()

    def click_clear_in_historical_tab(self) -> None:
        """
        Click the 'Clear' link in the Historical Picker.

        :raises TimeoutException: If the Historical Picker is not present.
        """
        self._historical_picker.click_clear()

    def click_historical_day(self, numeric_day: Union[int, str]) -> None:
        """
        Click the supplied numeric day in the Historical Picker.

        :param numeric_day: The day you would like to click.

        :raises AssertionError: If unsuccessful in clicking the supplied day.
        :raises TimeoutException: If the Historical Picker is not present.
        """
        self._historical_picker.click_historical_day(numeric_day=numeric_day)

    def close_date_range_modal_or_popover_if_displayed(self) -> None:
        """
        Close the Date Range Selector if it is already expanded. Takes no action if the Date Range Selector is not
        expanded.
        """
        if self.modal_or_popover_is_displayed():
            self._close_icon.click()

    def date_range_selector_toggle_icon_is_present(self) -> bool:
        """
        Determine if the icon used to expand the DateRangeSelector is present.

        :returns: True, if the icon is present - False otherwise.
        """
        try:
            return self._toggle_icon.find(wait_timeout=0.5) is not None
        except TimeoutException:
            return False

    def day_is_node_of_range(self, numeric_day: Union[int, str]) -> bool:
        """
        Determine if the supplied numeric day is either the start or end day of the current Historical range.

        :returns: True, if the supplied numeric_day is either the starting or ending day of the current range. False, if
            the numeric_day is simply within the range or not a part of the range at all.

        :raises TimeoutException: If the Historical picker is not present; likely to happen if dealing with the Realtime
            range instead of the Historical range.
        """
        return self._historical_picker.day_is_node_of_range(numeric_day=numeric_day)

    def day_is_within_historical_range(self, numeric_day: Union[int, str]) -> bool:
        """
        Determine if the supplied day falls anywhere within the current historical range.

        :param numeric_day: The number of the day to check for validity.

        :returns: True, if the supplied numeric day is the starting day, ending day or any day between those two days -
            False otherwise.

        :raises TimeoutException: If the Historical picker is not present; likely to happen if dealing with the Realtime
            range instead of the Historical range.
        """
        return self._historical_picker.day_is_within_current_range(numeric_day=numeric_day)
        
    def end_time_hour_input_is_enabled(self) -> bool:
        """
        Determine if the hours input of the ending time is enabled.

        :returns: True, if the hours input of the ending time for the Historical range is enabled - False otherwise.

        :raises TimeoutException: If the Historical picker is not present; likely to happen if dealing with the Realtime
            range instead of the Historical range.
        """
        return self._historical_picker.end_time_hour_input_is_enabled()
        
    def end_time_minute_input_is_enabled(self) -> bool:
        """
        Determine if the minutes input of the ending time is enabled.

        :returns: True, if the minutes input of the ending time for the Historical range is enabled - False otherwise.

        :raises TimeoutException: If the Historical picker is not present; likely to happen if dealing with the Realtime
            range instead of the Historical range.
        """
        return self._historical_picker.end_time_minute_input_is_enabled()
        
    def end_time_second_input_is_enabled(self) -> bool:
        """
        Determine if the seconds input of the ending time is enabled.

        Note: Date Range Selector does not support seconds as of 8.1.22, so this will always throw a TimeoutException.

        :returns: True, if the seconds input of the ending time for the Historical range is enabled - False otherwise.

        :raises TimeoutException: If the Historical picker is not present or the seconds input is not present; likely
            to happen if dealing with the Realtime range instead of the Historical range.
        """
        return self._historical_picker.end_time_second_input_is_enabled()

    def get_enabled_days(self) -> List[int]:
        """
        Obtain a list of all days in the current month which allow for selection.

        :returns: All days in the current month which a user may click as part of the range selection.

        :raises TimeoutException: If the historical picker is not present; likely to happen if dealing with the
            Realtime range instead of the Historical range.
        """
        return self._historical_picker.get_enabled_days()

    def get_historical_range(self) -> HistoricalRange:
        """
        Obtain all pieces of information pertaining to the Historical Range.

        :returns: An object containing information about the currently applied Historical Range - even if the Component
            is using a realtime range.
        """
        opened_to_start_with = self.modal_or_popover_is_displayed()
        if not opened_to_start_with:
            self.open_date_range_popover_or_modal_if_not_already_displayed()
            self.select_tab(tab=DateRangeSelectorTab.HISTORICAL)
        current_historical_range = self._historical_picker.get_current_range()
        if not opened_to_start_with:
            self.close_date_range_modal_or_popover_if_displayed()
        return current_historical_range

    def get_historical_text_picker_range_info_text(self) -> str:
        """
        Obtain the historical range as the formatted dates the user would see.

        :returns: A formatted string representation of the dates currently applied as the Historical Range.
        """
        opened_to_start_with = self.modal_or_popover_is_displayed()
        if not opened_to_start_with:
            self.open_date_range_popover_or_modal_if_not_already_displayed()
            self.select_tab(tab=DateRangeSelectorTab.HISTORICAL)
        time_picker_range_info_text = self._historical_picker.get_time_picker_range_info_text()
        if not opened_to_start_with:
            self.close_date_range_modal_or_popover_if_displayed()
        return time_picker_range_info_text

    def get_list_of_available_months_from_historical_picker(self) -> List[str]:
        """
        Obtain all available months from the Historical Range picker.

        :returns: All enabled months available for selection in the historical picker.

        :raises TimeoutException: If the Historical picker is not present; likely to happen if dealing with the
            Realtime range instead of the Historical range.
        """
        return self._historical_picker.get_list_of_available_months()

    def get_message(self) -> str:
        """
        Obtain the message related to the Date Range Selector. Currently only used for the Alarm Journal Table.
        Example: 'X alarm events'

        :returns: The message associated with the Date Range Selector, if available.

        :raises TimeoutException: If not using the Alarm Journal Table, or if the Alarm Journal Table currently has
            disabled the toolbar which houses the Date Range Selector.
        """
        return self._message.get_text()

    def get_range_message(self) -> str:
        """
        Obtain the range message associated with the Date Range Selector. This value describes the applied range.
        Example: 'Last 8 hours', or a breakdown of the date/times used for the Historical range.

        :returns: The range message associated with the Date Range Selector, if available.

        :raises TimeoutException: If the range message is not present.
        """
        return self._range_message.get_text()

    def get_selected_start_and_end_days_from_date_range_selector(self) -> List[int]:
        """
        Obtain the currently selected beginning and end days of the Historical range.

        Note: This only returns days of the current calendar month, so ranges which span months will only return
        one day.

        :returns: The beginning and end days of the current Historical range, where the
            first element in the list is the start day and the second element is the end day.

        :raises TimeoutException: If the Historical picker is not present; likely to happen if dealing with the
            Realtime range instead of the Historical range.
        """
        return self._historical_picker.get_selected_start_and_end_days_from_date_range_selector()

    def get_text_of_tabs(self) -> List[str]:
        """
        Obtain the text of the Realtime and Historical tabs, as a user would see them. Useful for verifying
        localization.

        :returns: A list of strings which represent the text displayed in the Realtime and Historical tabs, with
            Realtime as the 0th element, and Historical as the 1th element.

        :raises TimeoutException: If the Date Range Selector is not expanded.
        """
        return [_.text for _ in self._generic_tabs.find_all()]

    def historical_date_range_is_displayed(self) -> bool:
        """
        Determine if the Historical range picker is currently displayed to the user.

        :returns: True, if the picker is present - False otherwise.
        """
        return self._historical_picker.is_displayed()

    def hour_input_is_displayed(self) -> bool:
        """
        Determine if any hour input is visible.

        :returns: True if any hour input field is displayed.
        """
        return self._historical_picker.hour_input_is_visible()

    def hour_input_is_enabled(self) -> bool:
        """
        Determine if any hour input is enabled.

        :returns: True if any hour input field is enabled.
        """
        return self._historical_picker.hour_input_is_enabled()

    def minute_input_is_displayed(self) -> bool:
        """
        Determine if any minute input is visible.

        :returns: True if any minute input field is displayed.
        """
        return self._historical_picker.minute_input_is_visible()

    def minute_input_is_enabled(self) -> bool:
        """
        Determine if any minute input is enabled.

        :returns: True if any minute input field is enabled.
        """
        return self._historical_picker.minute_input_is_enabled()

    def modal_or_popover_is_displayed(self) -> bool:
        """
        Determine if the Date Range Selector is expanded.

        :returns: True, if the Date Range Selector is expanded as either a modal or 'popover' - False otherwise.
        """
        try:
            return self.find(wait_timeout=0.5) is not None
        except TimeoutException:
            return False

    def open_date_range_popover_or_modal_if_not_already_displayed(self) -> None:
        """
        Expand the Date Range Selector if it is not already expanded.

        :raises TimeoutException: If the icon used to expand the Date Range Selector is not present.
        """
        if not self.modal_or_popover_is_displayed():
            self._toggle_icon.click()

    def seconds_input_is_enabled(self) -> bool:
        """
        Determine if any seconds input is enabled.

        :returns: True, is any seconds input is enabled - False otherwise.
        """
        return self._historical_picker.seconds_input_is_enabled()

    def seconds_input_is_displayed(self) -> bool:
        """
        Determine if any seconds input is visible.

        :returns: True, is any seconds input is visible - False otherwise.
        """
        return self._historical_picker.seconds_input_is_displayed()

    def select_historical_month_from_dropdown(self, month: Union[int, str]) -> None:
        """
        Select a month from the Historical range picker.

        :param month: The name or 1-indexed numeric representation of a month to select (where 1 == January).

        :raises AssertionError: If unsuccessful in applying the supplied month.
        """
        self._historical_picker.select_month(month=month)

    def select_realtime_unit(self, time_unit: DateRangeSelectorTimeUnit) -> None:
        """
        Select a unit of time from the Realtime range selector.

        :param time_unit: The unit of time to select from the selector.

        :raises AssertionError: If unsuccessful in applying the supplied time unit.
        """
        self._realtime_range.select_realtime_unit(time_unit=time_unit)

    def select_date(self, date: PerspectiveDate) -> None:
        """
        Select a date in the picker. This function should only be used when interacting with the picker used as part of
        filtering a date-type Table column. Usage while interacting with an Alarm Journal Table or Power Chart is
        unsupported; please use :func:`set_historical_range_and_apply`

        :param date: The date to select in the Range Selector.

        :raises AssertionError: If unsuccessful in applying the supplied date.
        """
        self._historical_picker.select_date(date=date)

    def select_tab(self, tab: DateRangeSelectorTab) -> None:
        """
        Select either the Realtime or Historical tab within the Date Range Selector.

        :param tab: The tab you would like to click.

        :raises TimeoutException: If the supplied tab is not present.
        """
        _tab_comp = self._historical_tab if tab == DateRangeSelectorTab.HISTORICAL else self._realtime_tab
        try:
            _tab_comp.click(binding_wait_time=1)
        except StaleElementReferenceException:
            self.select_tab(tab=tab)

    def set_historical_range(self, historical_range: HistoricalRange, apply: Optional[bool] = None) -> None:
        """
        Set the historical range and click the Apply button.

        :param historical_range: The Historical Range object which defines the starting and ending dates to apply.
        :param apply: If True, the supplied historical range will be applied. If False, the supplied Historical Range
            will be cancelled upon completion. If None, no action will be taken after completion, leaving the Date
            Range Selector open.

        :raises AssertionError: If unsuccessful in applying the supplied historical range.
        :raises TimeoutException: If the Apply button or the picker were not present.
        """
        self._historical_picker.set_range(historical_range=historical_range)
        if apply:
            self._apply_button.click()
        elif apply is not None:  # False
            self._cancel_button.click()
        else:  # take no action at all
            pass

    def set_realtime_range(self, time_value: int) -> None:
        """
        Set the numeric range to be used with the time unit.

        :param time_value: The scalar amount of time you desire to apply as the Realtime range.

        :raises AssertionError: If unsuccessful in applying the supplied time value.
        """
        self._realtime_range.set_time_value(
            time_value=time_value)
        
    def start_time_hour_input_is_enabled(self) -> bool:
        """
        Determine if the starting time hour input is enabled.

        :returns: True, if the hours input for the starting date of the range is enabled - False otherwise..

        :raises TimeoutException: If the picker is not present.
        """
        return self._historical_picker.start_time_hour_input_is_enabled()
        
    def start_time_minute_input_is_enabled(self) -> bool:
        """
        Determine if the starting time minute input is enabled.

        :returns: True, if the minutes input for the starting date of the range is enabled - False otherwise..

        :raises TimeoutException: If the picker is not present.
        """
        return self._historical_picker.start_time_minute_input_is_enabled()
        
    def start_time_second_input_is_enabled(self) -> bool:
        """
        Determine if the starting time second input is enabled.

        :returns: True, if the seconds input for the starting date of the range is enabled - False otherwise..

        :raises TimeoutException: If the picker is not present.
        """
        return self._historical_picker.start_time_second_input_is_enabled()

    def tab_is_active(self, tab: DateRangeSelectorTab) -> bool:
        """
        Determine if the supplied tab is currently the active tab.

        :param tab: The tab which will have its active status queried.

        :returns: True, if the supplied tab is active - False otherwise.

        :raises TimeoutException: If the Date Range Selector is not present.
        """
        _tab_component = self._historical_tab if tab == DateRangeSelectorTab.HISTORICAL else self._realtime_tab
        return self.ACTIVE_TAB_CLASS in _tab_component.find().get_attribute("class")
