"""
A collection of our defined Expected Conditions. For a brief explanation on how to create more, go to the Custom Wait
Conditions on https://selenium-python.readthedocs.io/waits.html.
Leaving class names in lowercase to conform with existing expected_conditions classes.
"""
from enum import Enum
from typing import Tuple, Callable

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


class TextCondition(Enum):
    CONTAINS = 1
    DOES_NOT_CONTAIN = 2
    EQUALS = 3
    DOES_NOT_EQUAL = 4


class NumericCondition(Enum):
    """
    Numeric conditions are not the same as TextConditions, because Numeric Entry Fields render values of
    "1000" as "1,000". Additionally, supplying values like 1.5e2 would display as something like "150".

    When using NumericCondition, commas are always ignored. Note also that this will not account for formatting of
    values applied by the Numeric Entry Field.
    """
    EQUALS = 5
    DOES_NOT_EQUAL = 6


class child_element_has_partial_css_class(object):
    """
    An expectation that within a WebElement there is a specific child WebElement
    which has a provided string as part of its CSS class.
    """
    def __init__(self, parent_web_element: WebElement, locator: Tuple[By, str], text: str):
        """
        :param parent_web_element: The WebElement you expect to contain a child WebElement which contains your
            supplied text as part of its HTML `class` attribute.
        :param locator: The locator used to describe the child you expect to contain the supplied text as part of the
            HTML `class` attribute.
        :param text: The text you expect to be present within the HTML `class` attribute of the child element.
        """
        self.parent_web_element = parent_web_element
        self.locator = locator
        self.text = str(text)

    def __call__(self, driver):
        element = self.parent_web_element.find_element(*self.locator)
        if element:
            if self.text in element.get_attribute('class'):
                return self.parent_web_element
        return False


class element_has_exact_css_class(object):
    """
    An expectation that a WebElement has an exact class attribute.
    """
    def __init__(self, web_element: WebElement, expected_css_class: str):
        """
        :param web_element: The WebElement you expect to have some exact HTML `class` attribute.
        :param expected_css_class: The exact contents you expect to be present in the HTML `class` attribute of the
            supplied WebElement.
        """
        self.web_element = web_element
        self.expected_css_class = str(expected_css_class)

    def __call__(self, driver):
        return self.expected_css_class == self.web_element.get_attribute('class')


class element_in_list_contains_text(object):
    """
    An expectation that within a collection of elements, one of the elements contains the expected text.
    Waits if the list of elements is empty, or if none of the elements currently contain the text.
    """
    def __init__(self, locator: Tuple[By, str], text: str):
        """
        :param locator: The tuple used to describe the collection of elements
        :param text: The expected text content of any one of the WebElements described by the supplied locator.
        """
        self.locator = locator
        self.text = str(text)

    def __call__(self, driver):
        elements = driver.find_elements(*self.locator)
        if elements:
            try:
                for element in elements:
                    if element.text == self.text:
                        return element
                return False
            except StaleElementReferenceException:
                return False
        else:
            return False


class element_identified_by_locator_equals_text(object):
    """
    An expectation for checking if the given text is an exact match to the text of the
    element identified by the supplied locator.
    """
    def __init__(self, locator: Tuple[By, str], text: str):
        """
        :param locator: The tuple used to describe the singular WebElement we expect to have the supplied text. If
            more than one WebElement would match the supplied locator, only the first will be checked.
        :param text: The exact text we expect to be present in the WebElement described by the supplied locator.
        """
        self.locator = locator
        self.text = str(text)

    def __call__(self, driver):
        try:
            element = driver.find_element(*self.locator)
            if self.text == element.text:
                return element
            else:
                return False
        except StaleElementReferenceException:
            return False


class element_identified_by_locator_contains_text(object):
    """
    An expectation for checking that the given text is contained in the text of the element identified by the
    supplied locator.
    """
    def __init__(self, locator: Tuple[By, str], text: str):
        """
        :param locator: The tuple used to describe the singular WebElement we expect to contain the supplied text. If
            more than one WebElement would match the supplied locator, only the first will be checked.
        :param text: The text we expect to be present within the full text of the WebElement described by the
            supplied locator.
        """
        self.locator = locator
        self.text = str(text)

    def __call__(self, driver):
        try:
            element = driver.find_element(*self.locator)
            if self.text in element.text:
                return element
            else:
                return False
        except StaleElementReferenceException:
            return False


class element_identified_by_locator_does_not_equal_text(object):
    """
    An expectation for checking that the element identified by the provided locator does not have the provided text.
    Sometimes we want to wait for text to change away from a value and evaluate instead of evaluating while waiting
    for some expected value
    """
    def __init__(self, locator: Tuple[By, str], text: str):
        """
        :param locator: The tuple which describes the singular WebElement you expect to not have the supplied text.
        :param text: The text you expect to not be present in the WebElement described by the supplied locator.
        """
        self.locator = locator
        self.text = str(text)

    def __call__(self, driver):
        try:
            element = driver.find_element(*self.locator)
            if self.text == element.text:
                return False
            else:
                return element  # Returns whole element once the condition fulfilled
        except StaleElementReferenceException:
            return False


class element_identified_by_locator_has_value(object):
    """
    Checks to see if the WebElement described by the supplied locator has the supplied expected value.
    """
    def __init__(self, locator: Tuple[By, str], expected_value: str):
        """
        :param locator: The tuple which describes the singular WebElement from which we will check the HTMl `value`
            attribute for the supplied expected value.
        :param expected_value: The value we expect the WebElement described by the supplied locator to contain.
        """
        self.locator = locator
        self.expected_value = str(expected_value)

    def __call__(self, driver):
        try:
            if driver.find_element(*self.locator).get_attribute("value") == self.expected_value:
                return self.expected_value
            else:
                return False
        except NoSuchElementException:
            return False
        except StaleElementReferenceException:
            return False


class element_does_not_equal_value(object):
    """
    An expectation that the supplied WebElement does not have the specified string value.
    """
    def __init__(self, element: WebElement, value: str):
        """
        :param element: The WebElement we will check for the supplied value.
        :param value: The string value you expect the WebElement to no longer have.
        """
        self.element = element
        self.value = str(value)

    def __call__(self, driver):
        try:
            if self.value == self.element.find_element(By.TAG_NAME, 'input').get_attribute('value'):
                return False
            else:
                return self.element  # Returns whole element once the condition fulfilled
        except StaleElementReferenceException:
            return False


class child_element_exists(object):
    """
    An expectation for checking that a child component exists and returns the child element. This allows us to
    wait for an element to exist within another element
    """
    def __init__(self, parent_web_element: WebElement, child_locator: Tuple[By, str]):
        """
        :param parent_web_element: The WebElement you expect to contain a child described by the supplied child locator.
        :param child_locator: The locator which describes a WebElement you expect to eventually be a child of the
            supplied parent WebElement.
        """
        self.parent_web_element = parent_web_element
        self.child_locator = child_locator

    def __call__(self, driver):
        try:
            return self.parent_web_element.find_element(*self.child_locator)
        except NoSuchElementException:
            return None


class driver_is_ready(object):
    """
    An expectation that the supplied driver be in a usable state.
    """
    def __init__(self, driver: WebDriver):
        self._driver = driver

    def __call__(self, driver):
        try:
            return self._driver.current_url is not None
        except WebDriverException:
            return False


class function_returns_true(object):
    """
    An expectation that a function will evaluate to True provided a set of kwargs. When providing a function, always
    make sure to exclude the parentheses which would cause an invocation.

    Example:
    def myFunc(arg1, arg2):
        ...

    Should be used in this manner (note no parentheses after "myFunc"):
    IAExpectedCondition.function_returns_true(
        custom_function=myFunc,
        function_args={
            "arg1": someValue:
            "arg2": someOtherValue})
    """
    def __init__(self, custom_function: Callable, function_args: dict):
        """
        :param custom_function: An actual function (non-invoked) to execute with some supplied arguments.
        :param function_args: A dictionary containing the arguments of the supplied function.
        """
        self.custom_function = custom_function
        self.function_args = function_args

    def __call__(self, driver):
        try:
            return self.custom_function(**self.function_args)
        except StaleElementReferenceException:
            return False


class function_returns_false(object):
    """
    An expectation that a function will evaluate to False provided a set of kwargs. When providing a function, always
    make sure to exclude the parentheses which would cause an invocation.

    Example:
    def myFunc(arg1, arg2):
        ...

    Should be used in this manner (note no parentheses after "myFunc"):
    IAExpectedCondition.function_returns_false(
        custom_function=myFunc,
        function_args={
            "arg1": someValue:
            "arg2": someOtherValue})
    """
    def __init__(self, custom_function: Callable, function_args: dict):
        """
        :param custom_function: An actual function (non-invoked) to execute with some supplied arguments.
        :param function_args: A dictionary containing the arguments of the supplied function.
        """
        self.custom_function = custom_function
        self.function_args = function_args

    def __call__(self, driver):
        try:
            return not self.custom_function(**self.function_args)
        except StaleElementReferenceException:
            return False


class element_is_fully_in_viewport(object):
    def __init__(self, driver: WebDriver, locator: Tuple[By, str]):
        """
        :param driver: The WebDriver of the Selenium session.
        :param locator: The locator which describes the singular element to verify is within the boundaries of the
            viewport.
        """
        self.driver = driver
        self.locator = locator

    def __call__(self, driver):
        _rect = self.driver.find_element(*self.locator).rect
        _viewport_height = self.driver.execute_script('return window.innerHeight')
        _viewport_width = self.driver.execute_script('return window.innerWidth')
        return (_rect['x'] >= 0) and \
               (_rect['x'] + _rect['width'] <= _viewport_width) and \
               (_rect['y'] >= 0) and \
               (_rect['y'] + _rect['height'] <= _viewport_height)
