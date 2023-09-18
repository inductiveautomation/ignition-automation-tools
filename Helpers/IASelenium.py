import datetime
import logging
import os
import time
from typing import List

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.support.wait import WebDriverWait

from Helpers.Formatting import FilePathFormatting
from Helpers.IAExpectedConditions import IAExpectedConditions as IAec


class IASelenium:
    """
    A collection of functions intended to provide easier/uniform interactions with the Selenium browser session.
    """

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.logger = logging.getLogger(name='IASelenium')

    def click_at_offset(self, x: int = 0, y: int = 0) -> None:
        """
        Move some number of pixels away from the current position of the cursor and then click.

        :param x: The number of pixels to move left/right. Positive values are right, and negative values are left.
        :param y: The number of pixels to move up/down. Positive values are down, and negative values are up.
        """
        ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=y).click().perform()

    def click_drag_release(self, web_element: WebElement, x: int, y: int) -> None:
        """
        Click-and-hold on a WebElement, then drag it some number of pixels before finally releasing the held click.

        :param web_element: The WebElement to be dragged.
        :param x: The number of pixels to drag left/right. Positive values are right, and negative values are left.
        :param y: The number of pixels to drag up/down. Positive values are down, and negative values are up.
        """
        ActionChains(self.driver) \
            .move_to_element(web_element) \
            .click_and_hold(on_element=web_element) \
            .move_by_offset(x, y) \
            .release() \
            .perform()

    def click_element_with_offset(self, web_element: WebElement, x_offset: int, y_offset: int) -> None:
        """
        Hover over a WebElement before then moving some number of pixels and clicking.

        :param web_element: The WebElement to hover over.
        :param x_offset: The number of pixels to drag left/right. Positive values are right, and negative values
            are left.
        :param y_offset: The number of pixels to drag up/down. Positive values are down, and negative values are up.
        """
        ActionChains(self.driver).move_to_element_with_offset(
            to_element=web_element,
            xoffset=x_offset,
            yoffset=y_offset).click().perform()

    def close_current_tab(self) -> None:
        """
        Close the current tab in use by the browser. CAUTION: if invoked on the only available tab, the browser
        session will end.
        """
        self.driver.close()

    def close_extra_tabs(self) -> None:
        """
        Close any browser tabs which are not the 0th tab, and then switch to the 0th tab.
        """
        while self.get_tab_count() > 1:
            self.switch_to_tab_by_index(zero_based_index=1)
            self.close_current_tab()
        self.switch_to_tab_by_index(zero_based_index=0)

    def current_tab_index(self) -> int:
        """
        Obtain the zero-based index of the tab currently in use by the browser.

        :returns: The index of the tab currently in use by the browser.
        """
        handle = self.driver.current_window_handle
        count = len(self.driver.window_handles)
        for i in range(count):
            if str(self.driver.window_handles[i]) == handle:
                return i
        assert False, 'We never found a matching window handle.'

    def disable_context_menu(self) -> None:
        """
        Modify the browser so that context menu does not open on right-click.
        """
        self.driver.execute_script('document.body.setAttribute("oncontextmenu", "return false");')

    def enable_context_menu(self) -> None:
        """
        Modify the browser so that context menu opens on right-click.
        """
        self.driver.execute_script('document.body.setAttribute("oncontextmenu", "return true");')

    def double_click(self, web_element: WebElement) -> None:
        """
        Double-click on a WebElement. Fundamentally different from clicking on a WebElement and then clicking again.

        :param web_element: The WebElement which will receive the double-click.
        """
        ActionChains(self.driver).move_to_element(to_element=web_element).double_click(on_element=web_element).perform()

    def get_inner_height(self) -> int:
        """
        Obtain the height of the viewable area of the browser.
        """
        return self.driver.execute_script(script='return window.innerHeight')

    def get_inner_width(self) -> int:
        """
        Obtain the width of the viewable area of the browser.
        """
        return self.driver.execute_script(script='return window.innerWidth')

    def get_tab_count(self) -> int:
        """
        Obtain a count of all tabs open within the browser.

        :returns: The count of all tabs open within the current browser.
        """
        return len(self.driver.window_handles)

    def get_tab_title(self) -> str:
        """
        Obtain the title of the current tab. This is the text displayed in the tab of the browser.

        :returns: The text content of the browser tab.
        """
        return self.driver.title

    def go_back(self) -> None:
        """
        Go back to the previous browser page.
        """
        self.driver.back()

    def highlight_web_element(self, web_element: WebElement) -> None:
        """
        Force a yellow background and red border onto the supplied WebElement.

        :param web_element: The WebElement to be modified.
        """
        original_style = web_element.get_attribute('style')
        highlight_style = original_style + 'background: yellow; border: 2px solid red; color: black;'

        self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                   web_element, highlight_style)

    def hover_over_web_element(self, web_element: WebElement) -> WebElement:
        """
        Hover over a WebElement.

        :param web_element: The WebElement to hover over.

        :returns: The WebElement supplied, to allow for chaining.
        """
        ActionChains(self.driver).move_to_element(web_element).perform()
        return web_element

    def inclusive_multi_select_elements(self, web_element_list: List[WebElement]) -> None:
        """
        Click on each element in the supplied list while holding SHIFT.

        :param web_element_list: A list of WebElements, where we will click on each WebElement while holding down
            the SHIFT key.
        """
        actions = ActionChains(self.driver)
        actions.key_down(Keys.SHIFT)
        for element in web_element_list:
            actions.click(element)
        actions.key_up(Keys.SHIFT)
        actions.perform()

    def long_click(self, web_element: WebElement) -> None:
        """
        Click-and-hold on a WebElement for 2 seconds.

        :param web_element: The WebElement which will receive the elongated click event.
        """
        ActionChains(self.driver).move_to_element(to_element=web_element).click_and_hold().pause(2).release().perform()

    def move_mouse(self, x_offset: int = 0, y_offset: int = 0) -> None:
        """
        Move the mouse from its current location by some number of pixels.
        :param x_offset: The number of pixels to move left/right. Positive values are right, and negative values
            are left.
        :param y_offset: The number of pixels to move up/down. Positive values are down, and negative values are up.
        """
        ActionChains(self.driver).move_by_offset(xoffset=x_offset, yoffset=y_offset).perform()

    def open_new_tab_and_switch_to_it(self) -> None:
        """
        Open a new tab before then switching to the new created tab.
        """
        current_index = self.current_tab_index()  # need this BEFORE we open
        self.driver.execute_script("window.open('','_blank');")
        self.switch_to_tab_by_index(current_index + 1)

    def right_click(self, web_element: WebElement) -> None:
        """
        Right-click on a WebElement. To bypass the context menu of the browser, we disable the context menu before
        we right-click, then re-enable the context menu when done.

        :param web_element: The WebElement which should receive the right-click.
        """
        try:
            self.disable_context_menu()
            self.scroll_to_element(web_element=web_element)
            ActionChains(self.driver).context_click(on_element=web_element).perform()
        finally:
            self.enable_context_menu()

    def scroll_to_element(self, web_element: WebElement, align_to_top: bool = True) -> WebElement:
        """
        Scroll to a WebElement.

        :param web_element: The WebElement to scroll to.
        :param align_to_top: If True, page will attempt to scroll such that the WebElement will have its top edge
            touching the top of the viewport. If False, the page will attempt to scroll such that the WebElement will
            have its bottom edge touching the bottom of the viewport.

        :returns: The supplied WebElement, to allow for chaining.
        """
        align_string = str(align_to_top).lower()
        self.driver.execute_script('arguments[0].scrollIntoView(' + align_string + ');', web_element)
        return web_element

    def scroll_to_element_with_settings(
            self, web_element: WebElement, block_setting: str, inline_setting: str) -> WebElement:
        """
        A highly-specialized scrolling event, used primarily for dealing with input components which are hidden from
        the view of the user. These are common within File Upload components, but - unfortunately - it makes them
        impossible for Selenium to use without these particular settings.

        :param web_element: The WebElement which should be scrolled to and have its display settings modified.
        :param block_setting: The CSS 'block' setting to apply to the WebElement.
        :param inline_setting: The CSS 'inline' setting to apply to the WebElement.

        :returns: The Supplied WebElement, to allow for chaining.
        """
        _script = 'arguments[0].scrollIntoView({block:"' + block_setting + '", inline:"' + inline_setting + '"});'
        self.driver.execute_script(_script, web_element)
        return web_element

    def set_inner_window_dimensions(self, inner_width=None, inner_height=None) -> None:
        """
        Set the dimensions of the inner viewport of the browser.

        :param inner_width: The desired width of the viewport.
        :param inner_height: The desired height of the viewport.

        :raises ValueError: If the supplied inner_width is less than 500px.
        """
        if inner_width is not None and inner_width < 500:
            raise ValueError("Browser constraints prevent setting of inner width below 500px.")
        current_size = self.driver.get_window_size()
        current_width = current_size['width']  # OUTER dimension
        current_height = current_size['height']  # OUTER dimension
        adjusted_width = current_width
        adjusted_height = current_height
        if inner_width:
            adjusted_width = current_size['width'] + inner_width - self.get_inner_width()
        if inner_height:
            adjusted_height = current_size['height'] + inner_height - self.get_inner_height()
        print(f'\nAdjusting browser outer dimensions to {adjusted_width}x{adjusted_height}')
        # this actually sets the OUTER dimensions to our adjusted dimensions
        self.driver.set_window_size(width=adjusted_width, height=adjusted_height)

    def simple_click(self, web_element: WebElement) -> None:
        """
        Perform a "brainless" click on a WebElement. Standard Selenium clicks are actually quite complicated on the
        back-end, where several checks are performed, and exceptions may be raised before a click even occurs. This
        functions instead uses the primitive click options which performs no checks and will click the WebElement
        regardless of state.

        :param web_element: The WebElement to click.
        """
        ActionChains(self.driver).click(on_element=web_element).perform()

    def switch_to_tab_by_index(self, zero_based_index: int) -> None:
        """
        Switch to a specific tab based on its zero-based index.

        :param zero_based_index: The index of the tab to switch to.

        :raises TimeoutException: If there are fewer open tabs than the supplied index.
        """
        # if targeting anything beyond the first tab, wait for it to exist / finish opening
        if zero_based_index > 0:
            necessary_length = zero_based_index + 1

            def desired_tab_exists() -> bool:
                handles = len(self.driver.window_handles)
                return handles >= necessary_length
            try:
                WebDriverWait(self.driver, 1).until(IAec.function_returns_true(
                    custom_function=desired_tab_exists,
                    function_args={}))
            except TimeoutException as toe:
                raise TimeoutException(
                    msg=f"An attempt was made to switch tabs to index {zero_based_index}, but there weren't that "
                        f"many tabs present.") from toe
        handle = self.driver.window_handles[zero_based_index]
        self.switch_to_tab_by_title(title=handle)
        time.sleep(1)

    def switch_to_tab_by_title(self, title: str) -> None:
        """
        Switch to a tab by the text of the tab.

        :param title: The text content of the tab to switch to.
        """
        assert title in self.driver.window_handles, f'There is no tab titled \'{title}\' in the available tab listings.'
        self.driver.switch_to.window(title)
        time.sleep(1)

    def take_screenshot(self, directory: str = 'Screenshots', screenshot_name: str = None) -> str:
        """
        Take a screenshot of the tab currently in use.

        :param directory: The path of the directory into which the file will be saved.
        :param screenshot_name: The name to supply to the screenshot. If no name is provided, a filename which includes
            the current time will be generated.

        :returns: The location and name of the saved screenshot.
        """
        current_time = str(datetime.datetime.now()).replace(' ', '').replace(':', '')
        screenshot_title = 'AutoScreenshot' + current_time
        if screenshot_name:
            screenshot_title = str(screenshot_name)
        screenshot_title += '.png'
        screenshot_folder = f'{os.getcwd()}/{directory}'
        if not os.path.exists(screenshot_folder):
            os.mkdir(screenshot_folder)
        safe_path = FilePathFormatting.system_safe_file_path(screenshot_folder, screenshot_title)
        self.driver.save_screenshot(safe_path)
        self.logger.info(msg=f'Screenshot taken: {safe_path}')
        return safe_path

    def take_screenshot_of_element(self, web_element: WebElement, directory: str = 'Screenshots') -> str:
        """
        This method will apply a style to the supplied WebElement, giving it a red
        border and yellow background (Perspective <div> elements will only see the border)
        before taking a screenshot and saving the screenshot with a timestamp into the
        /<output_directory>/Screenshots directory of the project.

        :param web_element: The WebElement you'd like to take a screenshot of.
        :param directory: The directory where you are storing screenshots.

        :returns: The filename of the screenshot.
        """
        current_time = str(datetime.datetime.now()).replace(' ', '').replace(':', '')
        self.highlight_web_element(web_element=web_element)
        screenshot_title = 'AutoScreenshot' + current_time + '.png'
        screenshot_folder = f'{os.getcwd()}/{directory}'
        if not os.path.exists(screenshot_folder):
            os.mkdir(screenshot_folder)
        safe_path = FilePathFormatting.system_safe_file_path(screenshot_folder, screenshot_title)
        print(f'Screenshot path: \'{safe_path}\'')
        self.driver.save_screenshot(safe_path)
        return safe_path
