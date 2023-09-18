from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec

from Helpers.IASelenium import IASelenium
from Helpers.PerspectivePages.LoginHelper import LoginHelper as LoginHelper
from Pages.PagePiece import PagePiece


class AuthChallengeHelper(PagePiece):
    _AC_EMBEDDED_FRAME_POPUP_LOCATOR = (By.CSS_SELECTOR, 'div.popup-header')

    def __init__(self, driver: WebDriver):
        super().__init__(driver=driver)
        self._selenium = IASelenium(driver=self.driver)
        self.perspective_login_helper = LoginHelper(driver=driver)

    def authenticate_with_ignition_idp_within_iframe(self, username: str, password: str) -> None:
        self.switch_driver_to_embedded_frame()
        try:
            self.perspective_login_helper.log_in_through_login_page(username=username, password=password)
        except AssertionError:
            pass
        self.switch_driver_back_to_page()

    def authenticate_with_ignition_idp_on_new_tab(self, username: str, password: str) -> None:
        self._selenium.switch_to_tab_by_index(zero_based_index=1)
        try:
            self.perspective_login_helper.log_in_through_login_page(username=username, password=password)
        except AssertionError:
            pass
        self._selenium.switch_to_tab_by_index(zero_based_index=0)

    def embedded_ac_login_popup_is_displayed(self) -> bool:
        try:
            return self.wait.until(ec.text_to_be_present_in_element(self._AC_EMBEDDED_FRAME_POPUP_LOCATOR, 'Login'))
        except TimeoutException:
            return False

    def switch_driver_to_embedded_frame(self, iframe_index: int = 0) -> None:
        """
        Point the webdriver to the content of the embedded iframe in order to interact with it.
        """
        self.driver.switch_to.frame(self.driver.find_elements(By.TAG_NAME, "iframe")[iframe_index])

    def switch_driver_back_to_page(self) -> None:
        """
        Point the driver back to the main page after switching to an iframe to authenticate.
        """
        self.driver.switch_to.default_content()

    def switch_driver_back_to_project_tab(self) -> None:
        """
        Point the driver back to the main project tab after switching toa new tab to authenticate.
        """
        self._selenium.switch_to_tab_by_index(zero_based_index=0)
