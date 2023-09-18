import calendar
from time import sleep
from typing import Optional, Union, Tuple, List

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.select import Select

from Components.BasicComponent import ComponentPiece
from Components.Common.TextInput import CommonTextInput
from Helpers.IAAssert import IAAssert


class PerspectiveDate:
    """
    Perspective inputs use a unique take on dates, and formatting applied to these inputs can result in some values
    making no sense. Is a supplied time of 11:12:13 AM or PM? Should users specify a month by name or index? If index,
    is the month zero-indexed or one-indexed? By forcing interaction with these components to use a uniform class, we
    alleviate many pain points and a lot of confusion.
    """

    def __init__(
            self,
            year: Optional[int] = None,
            month: Optional[Union[int, str]] = None,
            day: Optional[int] = None,
            hours24: Optional[int] = None,
            minutes: Optional[int] = None,
            seconds: Optional[int] = None):
        """
        Create a date-type object Perspective can actually do something with.
        :param year: The numeric year of this date.
        :param month: accepts int or str (1, or "January"), but will be coerced into an int.
        :param day: The numeric day you'd like to select.
        :param hours24: The hours you'd like to select in 24-hour time. The am/pm value will be derived from this
            value, as will the hours12 value.
        :param minutes: The numeric minute of this date/time object.
        :param seconds: The numeric seconds of this date/time object.
        """
        self.year = year
        self._set_month(month=month)  # accept int/str but refine to int
        self.day = day
        self.hours24 = hours24 % 24 if hours24 else hours24
        self._set_hours12()  # calculation to be made
        self._set_am_pm()  # calculation to be made
        self.minutes = minutes
        self.seconds = seconds

    def __str__(self) -> str:
        """Provide a human-readable string representation of this object. Fill missing pieces with "X"."""
        filler = "X"
        return f"{self.month or filler}/{self.day or filler}/{self.year or filler} " \
               f"{self.hours24 or 2 * filler}:{self.minutes or 2 * filler}:{self.seconds or 2 * filler} (24-hour time)"

    def get_new_date_with_offset(
            self,
            year_offset: Optional[int] = None,
            month_offset: Optional[int] = None,
            day_offset: Optional[int] = None,
            hours24_offset: Optional[int] = None,
            minutes_offset: Optional[int] = None,
            seconds_offset: Optional[int] = None):
        """
        Obtain a new date with aspects of the current ('base') date modified by some value.

        :param year_offset: The count of years to add to the base date.
        :param month_offset: The count of months to add to the base date.
        :param day_offset: The count of days to add to the base date.
        :param hours24_offset: The count of hours to add to the base date. Must be less than 24. If larger than 24,
            combine with day_offset.
        :param minutes_offset: The count of minutes to add to the base date. Must be between -60 and 60. If the absolute
            value would be larger than 60, combine with hours24_offset.
        :param seconds_offset: The count of seconds to add to the base date. Must be between -60 and 60. If the absolute
            value would be larger than 60, combine with minutes_offset.

        :returns: A new Perspective Date object offset by some values from a base Perspective Date.

        :raises AssertionError: if the 'base' date being modified does not contain a value for some aspect which has
            been specified for modification, or if day offset values which would result in a day of a new month are
            supplied.
        """
        new_year = self.year
        new_month = self.month
        new_day = self.day
        new_hours24 = self.hours24
        new_minutes = self.minutes
        new_seconds = self.seconds
        if year_offset:
            IAAssert.is_true(
                value=self.year is not None,
                failure_msg="The supplied date had no year to offset from.")
            new_year = self.year + year_offset
        if month_offset:
            IAAssert.is_true(
                value=self.month is not None,
                failure_msg="The supplied date had no month to offset from.")
            new_month = self.month + month_offset
            if new_month < 1:
                new_month = 12 + (new_month % 12)
        if day_offset:
            IAAssert.is_true(
                value=self.day is not None,
                failure_msg="The supplied date had no day to offset from.")
            IAAssert.is_greater_than(
                left_value=day_offset + self.day,
                right_value=0,
                failure_msg="Unable to calculate day with negative offset which would result in new day being "
                            "calculated from end of month because we have no way of knowing what month is being "
                            "interacted with.")
            IAAssert.is_less_than_or_equal_to(
                left_value=day_offset + self.day,
                right_value=31,
                failure_msg="There can only be up to 31 days in a month.")
            new_day = self.day + day_offset
            # no special handling for new day because assertions prevent next/previous month checking
        if hours24_offset:
            new_hours24 = self.hours24 + hours24_offset
            if new_hours24 < 0:
                new_hours24 = 24 - (new_hours24 % 24)
            IAAssert.is_true(
                value=self.hours24 is not None,
                failure_msg="The supplied date had no hours to offset from.")
            IAAssert.is_less_than(
                left_value=abs(hours24_offset),
                right_value=24,
                failure_msg="There are only 0-23:59 hours in a day; please modify the day offset for offsets greater "
                            "than 24 hours.")
        if minutes_offset:
            IAAssert.is_true(
                value=self.minutes is not None,
                failure_msg="The supplied date had no minutes to offset from.")
            IAAssert.is_less_than(
                left_value=abs(minutes_offset),
                right_value=60,
                failure_msg="There are only 0-59 minutes in an hour; please modify the hour offset instead for "
                            "offsets greater than 60 minutes.")
            new_minutes = self.minutes + minutes_offset
            if new_minutes < 0:
                new_minutes = 60 - (new_minutes % 60)
        if seconds_offset:
            IAAssert.is_true(
                value=self.seconds is not None,
                failure_msg="The supplied date had no seconds to offset from.")
            IAAssert.is_less_than(
                left_value=abs(seconds_offset),
                right_value=60,
                failure_msg="There are only 0-59 seconds in a minute; please modify the minute offset instead for "
                            "offsets greater than 60 seconds.")
            new_seconds = self.seconds + seconds_offset
            if new_seconds < 0:
                new_seconds = 60 - (new_seconds % 60)
        return PerspectiveDate(
            year=new_year,
            month=new_month,
            day=new_day,
            hours24=new_hours24,
            minutes=new_minutes,
            seconds=new_seconds
        )

    def _set_am_pm(self) -> None:
        """
        Apply the 12 hour meridiem to use based on the 24-hour supplied value.
        """
        if self.hours24:
            self.am_pm = "am" if self.hours24 < 12 else "pm"
        else:
            self.am_pm = None

    def _set_hours12(self) -> None:
        """
        Apply a 12-hour (am/pm) value for instances where we might need to use a 12-hour format.
        """
        if self.hours24 is not None:
            self.hours12 = self.hours24 - 12 if self.hours24 > 12 else self.hours24
        else:
            self.hours12 = None

    def _set_month(self, month: Union[int, str]) -> None:
        """
        Determine and apply a numeric month based on whether the user supplied the month as a number or a string.
        """
        try:
            self.month = int(month)
        except ValueError:
            # string
            month_dict = {v: k for k, v in enumerate(calendar.month_name)}
            self.month = month_dict[month]
        except TypeError:
            # None
            self.month = month


class CommonDateTimePicker(ComponentPiece):
    """
    A common DateTime Picker component piece, used in not only the Perspective DateTime Input/Picker components, but
    also instances like the Alarm table date range selectors.
    """
    _NEXT_MONTH_CHEVRON_LOCATOR = (By.CSS_SELECTOR, 'div[data-next-month="true"]')
    _PREVIOUS_MONTH_CHEVRON_LOCATOR = (By.CSS_SELECTOR, 'div[data-prev-month="true"]')
    _CLEAR_RANGE_LOCATOR = (By.CSS_SELECTOR, 'a[class*="__clearRange"]')
    _MONTH_SELECT_LOCATOR = (By.CSS_SELECTOR, 'div.monthSelector select')
    _MONTH_OPTIONS_LOCATOR = f'{_MONTH_SELECT_LOCATOR[1]} option'
    _YEAR_SELECT_LOCATOR = (By.CSS_SELECTOR, 'div.yearSelector select')
    _NEXT_HOUR_SPINNER_LOCATOR = (By.CSS_SELECTOR, 'button[data-spinner-next-hour="true"]')
    _NEXT_MINUTE_SPINNER_LOCATOR = (By.CSS_SELECTOR, 'button[data-spinner-next-minute="true"]')
    _NEXT_SECOND_SPINNER_LOCATOR = (By.CSS_SELECTOR, 'button[data-spinner-next-second="true"]')
    _PREVIOUS_HOUR_SPINNER_LOCATOR = (By.CSS_SELECTOR, 'button[data-spinner-prev-hour="true"]')
    _PREVIOUS_MINUTE_SPINNER_LOCATOR = (By.CSS_SELECTOR, 'button[data-spinner-prev-minute="true"]')
    _PREVIOUS_SECOND_SPINNER_LOCATOR = (By.CSS_SELECTOR, 'button[data-spinner-prev-second="true"]')
    _CALENDAR_LOCATOR = (By.CSS_SELECTOR, "div.calendar")
    _HOURS_INPUT_LOCATOR = (By.CSS_SELECTOR, "input.hours")
    _MINUTES_INPUT_LOCATOR = (By.CSS_SELECTOR, "input.minutes")
    _SECONDS_INPUT_LOCATOR = (By.CSS_SELECTOR, "input.seconds")
    _AM_PM_PICKER_LOCATOR = (By.CSS_SELECTOR, "div.timePickerAmPmPicker select")
    # the "filler" class is attached to days outside the current month
    _GENERIC_DAY_LOCATOR = (By.CSS_SELECTOR, f'div[class*="dayTile"]:not([class*="filler"])')  # must be this format
    # disabled days are still "active" because they're in the current month, but they are also "out of range"; enabled
    # days will have none of these three class (including "filler").
    _ENABLED_DAY_LOCATOR = (
        By.CSS_SELECTOR, f'{_GENERIC_DAY_LOCATOR[1]}:not([class*="outOfRange"])')
    _SELECTED_DAYS_SELECTOR = (By.CSS_SELECTOR, "div.node")

    def __init__(
            self,
            locator: Tuple[By, str],
            driver: WebDriver,
            parent_locator_list: List[Tuple[By, str]],
            wait_timeout: float = 1,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=locator,
            driver=driver,
            parent_locator_list=parent_locator_list,
            wait_timeout=wait_timeout,
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
        self._calendar_container = ComponentPiece(
            locator=self._CALENDAR_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._day_tiles_dict = {}
        self._enabled_days = ComponentPiece(
            locator=self._ENABLED_DAY_LOCATOR, driver=driver, parent_locator_list=self.locator_list)
        self.next_hour_chevron = ComponentPiece(
            locator=self._NEXT_HOUR_SPINNER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self.previous_hour_chevron = ComponentPiece(
            locator=self._PREVIOUS_HOUR_SPINNER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self.next_minute_chevron = ComponentPiece(
            locator=self._NEXT_MINUTE_SPINNER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self.next_second_chevron = ComponentPiece(
            locator=self._NEXT_SECOND_SPINNER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self.previous_minute_chevron = ComponentPiece(
            locator=self._PREVIOUS_MINUTE_SPINNER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._hours_input = CommonTextInput(
            locator=self._HOURS_INPUT_LOCATOR, driver=driver, parent_locator_list=parent_locator_list, wait_timeout=1)
        self._minutes_input = CommonTextInput(
            locator=self._MINUTES_INPUT_LOCATOR, driver=driver, parent_locator_list=parent_locator_list, wait_timeout=1)
        self._seconds_input = CommonTextInput(
            locator=self._SECONDS_INPUT_LOCATOR, driver=driver, parent_locator_list=parent_locator_list, wait_timeout=1)
        self._am_pm_picker = ComponentPiece(
            locator=self._AM_PM_PICKER_LOCATOR, driver=driver, parent_locator_list=parent_locator_list, wait_timeout=1)
        self._selected_days = ComponentPiece(
            locator=self._SELECTED_DAYS_SELECTOR, driver=driver, parent_locator_list=self.locator_list)

    def click_next_month(self) -> None:
        """Click the next month chevron/arrow."""
        self._next_month_chevron.click()

    def click_previous_month(self) -> None:
        """Click the previous month chevron/arrow."""
        self._previous_month_chevron.click()

    def get_am_pm(self) -> str:
        """
        Obtain the current meridiem from the picker.

        :returns: A value of 'am', 'pm'. A value of None will be returned if no AM/PM picker is present.
        """
        return self._am_pm_picker.find().get_attribute("value")

    def get_enabled_days(self) -> List[int]:
        """
        Obtain a list of all enabled days for the current month.

        :returns: A numeric list of all days for the current month which are enabled.
        :raises TimeoutException: If the Historical picker is not present.
        """
        return [int(_.text) for _ in self._enabled_days.find_all()]

    def get_hours(self) -> int:
        """
        Obtain the current numeric hour selection.

        :raises TimeoutException: If the current format is preventing the display of the hours input.
        """
        return int(self._hours_input.find().get_attribute("value"))

    def get_list_of_available_months(self) -> List[str]:
        """
        Obtain a list of names of the months available for selection in this picker.

        :returns: a list of string names of months which are currently enabled.
        """
        all_options = Select(webelement=self._month_dropdown.find()).options
        enabled_options = list(filter(lambda e: e.is_enabled(), all_options))
        return [option.text for option in enabled_options]

    def get_list_of_available_years(self) -> List[int]:
        """
        Obtain a list of all the years available for selection in this picker.

        :returns: A list of integers which make up the years available for selection in the picker.
        """
        all_options = Select(webelement=self._year_dropdown.find()).options
        enabled_options = list(filter(lambda e: e.is_enabled(), all_options))
        return [int(option.text) for option in enabled_options]

    def get_minutes(self) -> int:
        """
        Obtain the current minute value in use by the picker.

        :raises TimeoutException: If the current format is preventing the display of the minutes input.
        """
        return int(self._minutes_input.find().get_attribute("value"))

    def get_selected_days(self) -> List[int]:
        """
        Obtain a list of all the days currently selected within the picker. For ranges, this includes all days between
        the start and end of the range.

        :returns: A list of numeric days which display as selected in the picker.
        """
        try:
            return [int(_.text) for _ in self._selected_days.find_all()]
        except TimeoutException:
            return []

    def get_seconds(self) -> int:
        """
        Obtain the current seconds value of the picker.

        :raises TimeoutException: If the picker is rendering in a format that does not allow for specifying seconds.
        """
        return int(self._seconds_input.find().get_attribute("value"))

    def get_selected_month(self) -> str:
        """
        Obtain the name of the month currently selected for the picker.

        :returns: The full name of the currently selected month.
        """
        return Select(self._month_dropdown.find()).first_selected_option.get_attribute("value")

    def get_selected_year(self) -> int:
        """Obtain the currently selected year of the picker."""
        return int(Select(self._year_dropdown.find()).first_selected_option.text)

    def hour_input_is_enabled(self) -> bool:
        """
        Determine if the hour input field is currently enabled.

        :returns: True, if the hour input is enabled - False otherwise.
        """
        try:
            return self._hours_input.find().is_enabled()
        except TimeoutException:
            return False

    def hour_input_is_visible(self) -> bool:
        """
        Determine if the hour input field is currently visible.

        :returns: True, if the hour input is displayed - False otherwise.
        """
        try:
            return self._hours_input.find().is_displayed()
        except TimeoutException:
            return False

    def minute_input_is_enabled(self) -> bool:
        """
        Determine if the minute input field is currently enabled.

        :returns: True, if the minute input is enabled - False otherwise.
        """
        try:
            return self._minutes_input.find().is_enabled()
        except TimeoutException:
            return False

    def minute_input_is_visible(self) -> bool:
        """
        Determine if the minute input field is currently visible.

        :returns: True, if the minute input is visible - False otherwise.
        """
        try:
            return self._minutes_input.find().is_displayed()
        except TimeoutException:
            return False

    def seconds_input_is_enabled(self) -> bool:
        """
        Determine if the seconds input field is currently enabled.

        :returns: True, if the seconds input is enabled - False otherwise.
        """
        try:
            return self._seconds_input.find().is_enabled()
        except TimeoutException:
            return False

    def seconds_input_is_displayed(self) -> bool:
        """
        Determine if the seconds input field is currently visible.

        :returns: True, if the seconds input is visible - False otherwise.
        """
        try:
            return self._seconds_input.find().is_displayed()
        except TimeoutException:
            return False

    def select_date(self, date: PerspectiveDate) -> None:
        """
        Select a date in the picker.

        :param date: The date to select, as an object.

        :raises AssertionError: If unsuccessful in applying the supplied date.
        """
        # date must be selected BEFORE time
        self.select_date_only_not_time(date=date)
        self.select_time_only_not_date(date=date)

    def select_date_only_not_time(self, date: PerspectiveDate) -> None:
        """
        Select only a date (year, month, day), while ignoring any time values.

        :param date: The date to select, as an object. The time values of this object will be ignored.

        :raises AssertionError: If unsuccessful in applying any piece if the date.
        """
        if date.year is not None:
            self.select_year(year=date.year)
        if date.month is not None:
            self.select_month(month=date.month)
        if date.day is not None:
            self._click_day(numeric_day=date.day)

    def select_month(self, month: Union[int, str]) -> None:
        """
        Select a month by using the chevrons/arrows. Selenium has issues with the dropdowns when they are opened in
        Popups, so we avoid their use at all.

        :param month: The month to select. This may be a numeric representation or the string name of the month.

        :raises AssertionError: If the picker could not apply the month.
        """
        try:
            month = int(month)
        except ValueError:
            month_dict = {v: k for k, v in enumerate(calendar.month_name)}
            month = month_dict[month]
        selected_month_value = self._month_value()
        count = 0
        while selected_month_value != month and count < 12:
            self._next_month_chevron.find().click() if selected_month_value < month \
                else self._previous_month_chevron.find().click()
            selected_month_value = self._month_value()
            count += 1
        IAAssert.is_equal_to(
            actual_value=selected_month_value,
            expected_value=month,
            as_type=str,
            failure_msg=f"Failed to set the month to a different 1-indexed value ({month}).")

    def select_time_only_not_date(self, date: PerspectiveDate) -> None:
        """
        Select only a time (hours, minutes, seconds), while ignoring any date values.

        :param date: The date to select, as an object. Only the time piece of the date object will be used.

        :raises AssertionError: If unable to select the supplied time.
        """
        # seconds
        seconds = date.seconds
        if seconds is not None:
            current_seconds = int(self.get_seconds())
            if self._seconds_input.find().is_enabled():
                target = self.previous_minute_chevron if int(seconds) < int(current_seconds) else \
                    self.next_second_chevron
                while current_seconds != int(seconds):
                    target.click(binding_wait_time=0.5)
                    new_seconds = int(self.get_seconds())
                    if new_seconds != current_seconds:
                        current_seconds = new_seconds
                    else:
                        break
            IAAssert.is_equal_to(
                actual_value=current_seconds,
                expected_value=seconds,
                as_type=int,
                failure_msg=f"Failed to set the seconds to a different value ({seconds}).")
        # minutes
        minutes = date.minutes
        if minutes is not None:
            current_minutes = int(self.get_minutes())
            if self._minutes_input.find().is_enabled():
                target = self.previous_minute_chevron if int(minutes) < int(current_minutes) else \
                    self.next_minute_chevron
                while current_minutes != int(minutes):
                    target.click(binding_wait_time=0.5)
                    new_minutes = int(self.get_minutes())
                    if new_minutes != current_minutes:
                        current_minutes = new_minutes
                    else:
                        break
            IAAssert.is_equal_to(
                actual_value=current_minutes,
                expected_value=minutes,
                as_type=int,
                failure_msg=f"Failed to set the minutes to a different value ({minutes}).")
        # hours AND am/pm
        if date.am_pm:  # implies any hours are supplied
            try:
                if date.hours12 is not None and self._hours_input.find().is_enabled():
                    self._set_hours(date.hours12)
                self._am_pm_picker.find().click()
                Select(webelement=self._am_pm_picker.find()).select_by_visible_text(text=date.am_pm.upper())
                # TODO: There is an issue with Selenium/FF where the date time picker is collapsed
                #  after selecting am/pm. With that being the case, the following assertions will fail.
                #
                # IAAssert.is_equal_to(
                #     actual_value=self.get_hours(),
                #     expected_value=date.hours12,
                #     as_type=str,
                #     failure_msg=f"Failed to set the hours to a different value ({date.hours12}).")
                # IAAssert.is_equal_to(
                #     actual_value=Select(webelement=self._am_pm_picker.find()).first_selected_option.text.upper(),
                #     expected_value=date.am_pm.upper(),
                #     as_type=str,
                #     failure_msg="Failed to select am/pm.")
            except TimeoutException:
                # AM/PM Select might not be present, depending on locale
                if date.hours24 is not None:
                    self._set_hours(date.hours24)
                IAAssert.is_equal_to(
                    actual_value=self.get_hours(),
                    expected_value=date.hours24,
                    as_type=str,
                    failure_msg=f"Failed to set the hours to a different value ({date.hours24}).")

    def select_year(self, year: Union[int, str]) -> None:
        """
        Select a year by using the chevrons/arrows. Selenium has issues with the dropdowns when they are opened in
        Popups, so we avoid their use at all.

        :param year: The year to select.

        :raises AssertionError: If the picker could not apply the year.
        """
        max_distance = 120
        count = 0
        selected_year = Select(self._year_dropdown.find()).first_selected_option.text
        year = str(year)
        while selected_year != year and count < max_distance:
            self._next_month_chevron.find().click() if selected_year < year \
                else self._previous_month_chevron.find().click()
            selected_year = Select(self._year_dropdown.find()).first_selected_option.text
            count += 1
        IAAssert.is_equal_to(
            actual_value=selected_year,
            expected_value=year,
            as_type=int,
            failure_msg=f"Failed to set the year to a different value ({year}).")

    def set_time(self, date: PerspectiveDate) -> None:
        """
        Set the time in use by the picker.

        :param date: The date object which contains the time values we will use.

        :raises TimeoutException: If the picker is using a format which does not allow for some unit of the supplied
            time (eg: seconds are supplied, but a format which does not support seconds is in use).
        """
        self.select_time_only_not_date(date=date)

    def _click_day(self, numeric_day: Union[int, str]) -> None:
        """
        Click a specific day tile.

        :param numeric_day: The number fo the day we will click.

        :raises TimeoutException: If no such day exists for the given month.
        """
        # unable to safely assert here because DateTime Inputs will collapse
        self._get_day_tile(numeric_day=numeric_day).click()

    def _get_day_tile(self, numeric_day: Union[int, str]) -> ComponentPiece:
        """
        Obtain a specific day tile.

        :param numeric_day: the 'text' of the day to obtain as a number.
        """
        numeric_day = str(numeric_day)
        tile_component_piece = self._day_tiles_dict.get(numeric_day)
        if not tile_component_piece:
            tile_component_piece = ComponentPiece(
                locator=(By.CSS_SELECTOR, f'>div[data-day="{numeric_day}"]:not([class*="filler"])'),
                driver=self.driver,
                parent_locator_list=self._calendar_container.locator_list,
                poll_freq=self.poll_freq)
            self._day_tiles_dict[numeric_day] = tile_component_piece
        return tile_component_piece

    def _month_value(self) -> int:
        """Obtain the value of the month dropdown, which stores months as numbers."""
        return int(self.driver.execute_script('return arguments[0].value;', self._month_dropdown.find()))

    def _set_hours(self, hours: int) -> None:
        """
        Set the hours in use by the input by clicking the up/down chevrons/arrows.

        :param hours: The hour to select.

        :raises AssertionError: If the supplied hour could not be applied.
        """
        current_hours = int(self.get_hours())
        target = self.previous_hour_chevron if int(hours) < current_hours else self.next_hour_chevron
        while current_hours != int(hours):
            target.click()
            sleep(0.5)
            new_hours = int(self.get_hours())
            if new_hours != current_hours:
                current_hours = new_hours
            else:
                break
