from selenium.common.exceptions import TimeoutException, NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicComponent
from Helpers.IAAssert import IAAssert
from Pages.Perspective.AppBar import AppBar
from Pages.Perspective.TerminalStates.LoggedOut import LoggedOut


class LoginHelper:
    """
    A Login Helper for Perspective Sessions. Functions here assist in logging users into sessions with provided
    credentials either via the Perspective Login page or active Perspective Sessions. Note that if your session ends up
    on the LoggedOut Terminal State Page that you must handle that scenario on your own - it is unsafe for this class
    to naively click the "Back" button of the LoggedOut Terminal State Page due to the potential for cached credentials.
    """
    _USERNAME_FIELD_CSS_LOCATOR = (By.CSS_SELECTOR, 'input.username-field')
    _PASSWORD_FIELD_LOCATOR = (By.CSS_SELECTOR, 'input.password-field')
    _EXIT_LOGIN_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'button.exit-login-button')
    _SUBMIT_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'div.submit-button')
    _CONTINUE_DESCRIPTOR_LOCATOR = (By.CSS_SELECTOR, 'div.panel-header p.panel-description')

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self._logged_out_ts_page = LoggedOut(driver=driver)
        self._app_bar = AppBar(driver=driver)
        self._username_input = BasicComponent(
            locator=self._USERNAME_FIELD_CSS_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=0,
            description="The username input of the Perspective Login page.")
        self._exit_login_button = BasicComponent(
            locator=self._EXIT_LOGIN_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=0,
            description="The button which allows a user to exit login. Available only within projects which do not "
                        "require authentication.")
        self._submit_button = BasicComponent(
            locator=self._SUBMIT_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=0,
            description="A generic 'submit' button, available while inputting both the username and the password on "
                        "the Perspective Login page.")
        self._password_input = BasicComponent(
            locator=self._PASSWORD_FIELD_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=0,
            description="The password input of the Perspective Login page.")
        self._continue_descriptor = BasicComponent(
            locator=self._CONTINUE_DESCRIPTOR_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            wait_timeout=0,
            description="The label on the interstitial 'continue' page which informs a user they must continue to the "
                        "Login page.")

    def click_exit_login(self) -> None:
        """
        Click the button to exit the login process and go back to the Perspective session.
        """
        self._exit_login_button.click()

    def continue_to_log_in(self) -> None:
        """
        Click the button on the interstitial 'continue' page so that you may continue to the main Perspective Login
        page.
        """
        try:
            self._submit_button.click(wait_timeout=3)
        except TimeoutException:
            pass
        self.wait_for_login_page()

    def log_in_through_login_page(self, username: str, password: str = "password") -> None:
        """
        Login to a Perspective project via the main Perspective Login page.

        :param username: The username to be used for the login process.
        :param password: The password to use for the supplied user.

        :raises AssertionError: If the project being logged into both has an App Bar configured to display, and this
            function was unsuccessful in logging in with the supplied credentials.
        """
        self.continue_to_log_in()
        try:
            self._username_input.find().send_keys(username)
            self._submit_button.click(binding_wait_time=1)
            self._password_input.find(wait_timeout=1).send_keys(password)
            self._submit_button.click()
        except TimeoutException:
            pass  # user credentials may have been cached.
        try:
            # wait for the Perspective page to load.
            self._app_bar.wait_for_revealer_or_app_bar_to_be_displayed()
            while self._app_bar.is_present() and not self._app_bar.is_expanded():
                # interaction with the revealer can sometimes occur too quickly after a page loads, so keep trying
                # if we are unsuccessful in expanding the App Bar
                try:
                    self._app_bar.expand()
                except AssertionError:
                    pass
            IAAssert.is_equal_to(
                actual_value=self._app_bar.get_logged_in_user(),
                expected_value=username,
                failure_msg=f"Failed to log in as the '{username}' user. Credentials from the previous user might have "
                            f"been cached by the browser.")
            self._app_bar.collapse()
        except TimeoutException:
            pass  # maybe the AppBar is not present in this project
        except NoSuchWindowException:
            pass  # AuthChallenge could force login in a new window

    def log_in_through_active_session(self, username: str, password: str = "password") -> None:
        """
        Log into an active Perspective Session, where the user is currently viewing a Perspective page which belongs
        to a project. If the supplied username is already logged in, no action is taken.

        :param username: The username to be used for the login process.
        :param password: The password to use for the supplied user.

        :raises AssertionError: If the current project does not allow for authentication (and therefore the
            SIGN IN/OUT buttons are not present in the App Bar), or if unsuccessful in logging in with the supplied
            credentials.
        :raises TimeoutException: If the App Bar is not present on the current page.
        """
        if self._app_bar.get_logged_in_user() != username:
            IAAssert.is_true(
                value=self._app_bar.sign_out_button_is_displayed() or self._app_bar.sign_in_button_is_displayed(),
                failure_msg="Unable to perform login, as neither the 'SIGN IN' nor 'SIGN OUT' button was present in "
                            "the App Bar.")
            if self._app_bar.sign_out_button_is_displayed():  # potential for project to not require auth
                self._app_bar.click_sign_out_button()
                self._app_bar.wait_for_revealer_or_app_bar_to_be_displayed(wait_timeout=3)
            if not (self.on_interstitial_continue_to_login_page() or self.on_login_page()):
                # Still in project, because auth not required
                self._app_bar.click_sign_in_button()
            self.log_in_through_login_page(username=username, password=password)

    def on_interstitial_continue_to_login_page(self) -> bool:
        """
        Determine if the session is currently viewing the 'Continue to Login' page. This is not considered to be the
        'main Login page'.

        :returns: True, if the user can see 'Continue to Login' - False otherwise.
        """
        try:
            self._submit_button.find(wait_timeout=0)  # to trigger the TOE if we are not on this page.
            return self._continue_descriptor.get_text() == 'You must log in to continue.'
        except TimeoutException:
            return False

    def on_login_page(self) -> bool:
        """
        Determine if you are currently on the main Perspective Login page.

        :returns: True, if you are currently on the main Perspective Login page. False, if you are not on the main
            Perspective Login page - even if you are on the interstitial 'continue' page.
        """
        try:
            return self._username_input.find() is not None
        except TimeoutException:
            return False

    def wait_for_login_page(self, time_to_wait: int = 10) -> None:
        """
        Wait up to some specified period of time for the main Login page to be displayed.

        :param time_to_wait: The amount of time (in seconds) you are prepared to wait for the Login page to be
            displayed before allowing code to continue.
        """
        try:
            self._username_input.find(wait_timeout=time_to_wait)
        except TimeoutException:
            pass
