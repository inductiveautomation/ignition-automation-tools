from enum import Enum
from time import sleep
from typing import Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from Components.BasicComponent import ComponentPiece
from Components.PerspectiveComponents.Common.Icon import CommonIcon
from Helpers.CSSEnumerations import CSSPropertyValue
from Helpers.Filtering import Items
from Helpers.IAAssert import IAAssert
from Helpers.IAExpectedConditions import IAExpectedConditions as IAec
from Pages.PagePiece import PagePiece


class AppBar(PagePiece):
    """
    Important terminology:
    App Bar: The thin piece of UI which spans the bottom of the session when expanded.
    Revealer: The tiny piece of UI - usually found in the bottom-right of the session - which expands the App Bar.
    Action Panel: The small panel which contains basic gateway information and the Sign in/out button.
    Session Status modal: The full-blown modal which contains information about the session and the project.
    About modal: The full-blown modal which may contain information about Ignition, or may be overridden with custom
        content.
    """

    class TogglePosition(Enum):
        LEFT = "left"
        RIGHT = "right"

    _ANIMATION_DELAY_IN_SECONDS = 1.5
    _ABOUT_BUTTON_LOCATOR = (By.CSS_SELECTOR, "div svg.about-icon")
    _ABOUT_BUTTON_LOCAL_SYMBOL_LOCATOR = (By.CSS_SELECTOR, "symbol")
    _GATEWAY_PANEL_LOCATOR = (By.ID, 'gateway-nav')
    _PROJECT_PANEL_LOCATOR = (By.ID, 'project-nav')
    _EXIT_PROJECT_LOCATOR = (By.CSS_SELECTOR, '.exit-project-icon')
    _USERNAME_LABEL_LOCATOR = (By.CSS_SELECTOR, 'div.username')
    _APP_BAR_WRAPPER_LOCATOR = (By.CSS_SELECTOR, 'div.app-bar')
    _ACTION_PANEL_TOGGLE_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'div.app-center')
    _ACTION_PANEL_LOCATOR = (By.CSS_SELECTOR, "div.action-panel")
    _ACTION_PANEL_GATEWAY_NAME_LOCATOR = (By.CSS_SELECTOR, "div.primary_message")
    _CONNECTION_SECURITY_LABEL_LOCATOR = (By.CSS_SELECTOR, "div.connection-security")
    _SESSION_STATUS_MODAL_GATEWAY_NAME_LOCATOR = (By.CSS_SELECTOR, "div.gateway-name")
    _TRIAL_TIMER_LOCATOR = (By.CSS_SELECTOR, "div.trial-clock")
    _GENERIC_TEXT_BUTTON_LOCATOR = (By.CSS_SELECTOR, "div.text-button")
    _ABOUT_IGNITION_ICON_LOCATOR = (By.CSS_SELECTOR, 'svg.about-icon')
    _REVEALER_LOCATOR = (By.CSS_SELECTOR, "div.bar-reveal")
    _SHOW_ICON_LOCATOR = (By.CSS_SELECTOR, 'svg.show-icon')
    _HIDE_ICON_LOCATOR = (By.CSS_SELECTOR, 'svg.hide-icon')
    _TIMER_ICON_LOCATOR = (By.CSS_SELECTOR, 'svg.timer-icon')
    _CLOSE_ICON_LOCATOR = (By.CSS_SELECTOR, "svg.close-icon")
    _GENERIC_NOTIFICATION_ICON_LOCATOR = (By.CSS_SELECTOR, "div.notification-icons > svg")
    _TOOLTIP_LOCATOR = (By.CSS_SELECTOR, 'div.app-tooltip')
    _STATUS_BUTTON_LOCATOR = (By.CSS_SELECTOR, 'div.status-button')
    _ABOUT_MODAL_AND_SESSION_STATUS_MODAL_LOCATOR = (By.CSS_SELECTOR, "div.app-modal")
    _ABOUT_MODAL_TITLE_LOCATOR = (By.CSS_SELECTOR, "div.modal-title")
    _GATEWAY_TAB_LOCATOR = (By.ID, "gateway-nav")
    _PROJECT_TAB_LOCATOR = (By.ID, "project-nav")
    _CONNECTION_STATUS_LABEL_LOCATOR = (
        By.CSS_SELECTOR, 'div.modal-connection-status div.gateway-status-message div.message-text')
    _DETAIL_DATA_CLASS = "detail-data"
    _GATEWAY_URL_LABEL_LOCATOR = (By.CSS_SELECTOR, f"div.gateway-url .{_DETAIL_DATA_CLASS}")
    _SESSION_ID_LABEL_LOCATOR = (By.CSS_SELECTOR, f"div.session-id .{_DETAIL_DATA_CLASS}")
    _PAGE_ID_LABEL_LOCATOR = (By.CSS_SELECTOR, f"div.page-id .{_DETAIL_DATA_CLASS}")
    _PROJECT_NAME_LABEL_LOCATOR = (By.CSS_SELECTOR, "div.project-page h4")
    _UPDATE_STATUS_LOCATOR = (By.CSS_SELECTOR, 'div.update-status')
    _LEARN_MORE_BUTTON_LOCATOR = (By.CSS_SELECTOR, "a.visit-site-link")
    _CUSTOM_VIEW_WRAPPER_LOCATOR = (By.CSS_SELECTOR, "div.custom-view-wrapper")
    _CUSTOM_VIEW_LOCATOR = (By.CSS_SELECTOR, "div.view")
    _SESSION_STATUS_MODAL_TITLE_TEXT = "Session Status"

    def __init__(self, driver: WebDriver):
        super().__init__(driver=driver, primary_locator=self._APP_BAR_WRAPPER_LOCATOR)
        self._animation_wait = WebDriverWait(driver=driver, timeout=self._ANIMATION_DELAY_IN_SECONDS)
        self._about_button = CommonIcon(
            locator=self._ABOUT_BUTTON_LOCATOR,
            driver=driver,
            description="The button at the extreme left of the expanded App Bar, which opens an info modal.",
            wait_timeout=0)
        self._about_button_local_symbol = ComponentPiece(
            locator=self._ABOUT_BUTTON_LOCAL_SYMBOL_LOCATOR,
            driver=driver,
            parent_locator_list=self._about_button.locator_list,
            description="The icon used within the 'About' button within the expanded App Bar.",
            wait_timeout=0)
        self._about_panel = ComponentPiece(
            locator=self._ABOUT_MODAL_AND_SESSION_STATUS_MODAL_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            description="The modal displayed which either displays info regarding Ignition, or a configured custom "
                        "View.",
            wait_timeout=0)
        self._about_modal_and_session_status_modal_title = ComponentPiece(
            locator=self._ABOUT_MODAL_TITLE_LOCATOR,
            driver=driver,
            parent_locator_list=self._about_panel.locator_list,
            description="The title of the 'About' modal.",
            wait_timeout=0)
        self._app_bar_wrapper = ComponentPiece(
            locator=self._APP_BAR_WRAPPER_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            description="The highest-level locator available to the App Bar.",
            wait_timeout=0)
        self._action_panel_toggle_button = ComponentPiece(
            locator=self._ACTION_PANEL_TOGGLE_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self._app_bar_wrapper.locator_list,
            description="The button in the center of the App Bar which expands and collapses the Action panel.",
            wait_timeout=0)
        self._generic_app_bar_notification_icon = CommonIcon(
            locator=self._GENERIC_NOTIFICATION_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self._action_panel_toggle_button.locator_list,
            description="A notification icon within the Action panel button (NOT the Revealer).",
            wait_timeout=0)
        self._action_panel = ComponentPiece(
            locator=self._ACTION_PANEL_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            description="The panel which appears above the App Bar when the central button is clicked.",
            wait_timeout=0)
        self._connection_security_label = ComponentPiece(
            locator=self._CONNECTION_SECURITY_LABEL_LOCATOR,
            driver=driver,
            parent_locator_list=self._action_panel.locator_list,
            description="The label which displays the connection security of the Session.",
            wait_timeout=0)
        self._status_button = ComponentPiece(
            locator=self._STATUS_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self._action_panel.locator_list,
            description="The STATUS button within the Action panel.",
            wait_timeout=0)
        self._username_label = ComponentPiece(
            locator=self._USERNAME_LABEL_LOCATOR,
            driver=driver,
            parent_locator_list=self._action_panel.locator_list,
            description="The label in the Action panel which conveys which user is logged in (if any).",
            wait_timeout=0)
        self._revealer = ComponentPiece(
            locator=self._REVEALER_LOCATOR,
            driver=driver,
            parent_locator_list=self._app_bar_wrapper.locator_list,
            description="The small piece of UI in the session (usually bottom-right) which allows for expanding the "
                        "App Bar.",
            wait_timeout=0)
        self._expand_icon = CommonIcon(
            locator=self._SHOW_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self._revealer.locator_list,
            description="The expand icon, which is only present while the App Bar is collapsed.",
            wait_timeout=0)
        self._collapse_icon = CommonIcon(
            locator=self._HIDE_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self._app_bar_wrapper.locator_list,  # Belongs to the App Bar, NOT the Revealer!
            description="The collapse icon, which is only present while the App Bar is expanded.",
            wait_timeout=0)
        self._timer_icon = CommonIcon(
            locator=self._TIMER_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self._revealer.locator_list,
            description="The timer icon, which is only present while using Perspective in Trial mode.",
            wait_timeout=0)
        self._exit_project_icon = CommonIcon(
            locator=self._EXIT_PROJECT_LOCATOR,
            driver=driver,
            parent_locator_list=self._app_bar_wrapper.locator_list,
            description="The Exit Project icon, found only in workstation.",
            wait_timeout=0)
        self._generic_revealer_notification_icon = CommonIcon(
            locator=self._GENERIC_NOTIFICATION_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self._revealer.locator_list,
            description="A notification icon within the Revealer (NOT the Action panel button).",
            wait_timeout=0)
        self._session_status_modal = ComponentPiece(
            locator=self._ABOUT_MODAL_AND_SESSION_STATUS_MODAL_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            description="The Session Status modal, which houses information about the Session and Gateway.",
            wait_timeout=0)
        self._gateway_tab = ComponentPiece(
            locator=self._GATEWAY_TAB_LOCATOR,
            driver=driver,
            parent_locator_list=self._session_status_modal.locator_list,
            description="The GATEWAY tab in the Session Status modal.",
            wait_timeout=0)
        self._project_tab = ComponentPiece(
            locator=self._PROJECT_TAB_LOCATOR,
            driver=driver,
            parent_locator_list=self._session_status_modal.locator_list,
            description="The PROJECT tab in the Session Status modal.",
            wait_timeout=0)
        self._gateway_name = ComponentPiece(
            locator=self._SESSION_STATUS_MODAL_GATEWAY_NAME_LOCATOR,
            driver=driver,
            parent_locator_list=self._session_status_modal.locator_list,
            description="The label which displays the name of the Gateway.",
            wait_timeout=0)
        self._connection_status_label = ComponentPiece(
            locator=self._CONNECTION_STATUS_LABEL_LOCATOR,
            driver=driver,
            parent_locator_list=self._session_status_modal.locator_list,
            description="The label which houses the connection status in the Session Status modal.",
            wait_timeout=0)
        self._session_status_panel_close_icon = CommonIcon(
            locator=self._CLOSE_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self._session_status_modal.locator_list,
            description="The 'X' in the upper-right of the Session Status modal.",
            wait_timeout=0)
        self._gateway_url_label = ComponentPiece(
            locator=self._GATEWAY_URL_LABEL_LOCATOR,
            driver=driver,
            parent_locator_list=self._session_status_modal.locator_list,
            description="The label which houses the Gateway URL information in the Session Status modal.",
            wait_timeout=0)
        self._session_id_label = ComponentPiece(
            locator=self._SESSION_ID_LABEL_LOCATOR,
            driver=driver,
            parent_locator_list=self._session_status_modal.locator_list,
            description="The label which houses the Session ID information in the Session Status modal.",
            wait_timeout=0)
        self._page_id_label = ComponentPiece(
            locator=self._PAGE_ID_LABEL_LOCATOR,
            driver=driver,
            parent_locator_list=self._session_status_modal.locator_list,
            description="The label which houses the Page ID information in the Session Status modal.",
            wait_timeout=0)
        self._project_name_label = ComponentPiece(
            locator=self._PROJECT_NAME_LABEL_LOCATOR,
            driver=driver,
            parent_locator_list=self._session_status_modal.locator_list,
            description="The label which contains the project name at the top of the Project tab.",
            wait_timeout=0)
        self._up_to_date_status_label = ComponentPiece(
            locator=self._UPDATE_STATUS_LOCATOR,
            driver=driver,
            parent_locator_list=self._session_status_modal.locator_list,
            description="The label which describes whether a project is up-to-date with the Gateway.",
            wait_timeout=0)
        self._tooltip = ComponentPiece(
            locator=self._TOOLTIP_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            description="the tooltip which is only visible when hovering over the expand/collapse icon of the "
                        "Revealer.",
            wait_timeout=1)  # this piece does need a wait period as it takes a moment to appear after the hover event.
        self._generic_text_button = ComponentPiece(
            locator=self._GENERIC_TEXT_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            description="A 'button' (<div>) within the greater Action panel.",
            wait_timeout=0)
        self._about_panel_close_icon = CommonIcon(
            locator=self._CLOSE_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            description="The 'X' in the upper-right of the 'About' modal.",
            wait_timeout=0)
        self._learn_more_button = ComponentPiece(
            locator=self._LEARN_MORE_BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self._about_panel.locator_list,
            description="The button within the 'About' modal which has text of 'LEARN MORE ABOUT IGNITION'.",
            wait_timeout=1)
        self._view_wrapper = ComponentPiece(
            locator=self._CUSTOM_VIEW_WRAPPER_LOCATOR,
            driver=driver,
            parent_locator_list=self._about_panel.locator_list,
            wait_timeout=1)
        self._generic_custom_view_top_level = ComponentPiece(
            locator=self._CUSTOM_VIEW_LOCATOR,
            driver=driver,
            parent_locator_list=self._about_panel.locator_list,
            wait_timeout=1)

    def about_modal_is_displayed(self) -> bool:
        """
        Determine if the 'About' panel is displayed.

        :returns: True, if the 'About Ignition' panel is displayed - False otherwise.
        """
        try:
            return self._about_panel.find(wait_timeout=0).is_displayed() \
                and "open" in self._about_panel.find().get_attribute("class") \
                and self._about_modal_and_session_status_modal_title.get_text() != self._SESSION_STATUS_MODAL_TITLE_TEXT
        except TimeoutException:
            return False

    def action_panel_is_expanded(self) -> bool:
        """
        Determine if the Action Panel is currently displayed.

        :returns: True, if the Action Panel is currently displayed - False otherwise.
        """
        try:
            return self._action_panel.find(wait_timeout=0).is_displayed() and \
                self._action_panel.get_termination().Y <= self._app_bar_wrapper.get_origin().Y
        except TimeoutException:
            return False

    def click_about_button(self) -> None:
        """
        Click the About button located in the App Bar.
        """
        self._expand_app_bar_if_not_expanded()
        # some tests check button appearance after click, so let the button have time to change color
        self._about_button.click(binding_wait_time=1)

    def click_sign_in_button(self) -> None:
        """
        Click the "Sign In" button.

        :raises IndexError: When user is already logged in, or if the project does not have a configured Identity
            Provider.
        """
        self._expand_action_panel_if_not_expanded()
        Items(
            items=self._generic_text_button.find_all(
                wait_timeout=1)).filter(
            lambda e: e.text == 'SIGN IN')[0].click()

    def click_sign_out_button(self) -> None:
        """
        Click the "Sign Out" button.

        :raises IndexError: When no user is logged in
        """
        self._expand_action_panel_if_not_expanded()
        Items(
            items=self._generic_text_button.find_all(
                wait_timeout=1)).filter(
            lambda e: e.text == 'SIGN OUT')[0].click()

    def click_status_button(self) -> None:
        """
        Click the Status Button within the App Bar.
        """
        self._expand_action_panel_if_not_expanded()
        self._status_button.click()

    def click_visit_gateway(self) -> None:
        """
        Click the Visit Gateway option in the Session Status modal. This will open a new tab in the browser.
        """
        self._open_session_status_modal_if_not_open()
        self._get_generic_text_button(button_text="VISIT GATEWAY").click()

    def close_about_modal_via_button(self) -> None:
        """
        Close the 'About' modal by clicking the 'About' button which originally opened the modal.

        :raises AssertionError: If the 'About' modal remains open.
        """
        if self.about_modal_is_displayed():
            self._click_about_button()
            self._wait_for_animations_to_cease()
        IAAssert.is_not_true(
            value=self.about_modal_is_displayed(),
            failure_msg="Failed to close the 'About' modal.")

    def close_about_modal_via_close_icon(self) -> None:
        """
        Close the 'About' modal by clicking the 'X' icon in the upper-right corner.

        :raises AssertionError: If the 'About' modal remains open.
        """
        if self.about_modal_is_displayed():
            self._about_panel_close_icon.click()
            self._wait_for_animations_to_cease()
        IAAssert.is_not_true(
            value=self.about_modal_is_displayed(),
            failure_msg="Failed to close the 'About' modal.")

    def close_session_status_modal(self) -> None:
        """
        Close the Session Status modal, if it is open.

        :raises AssertionError: If the Session Status modal remains open.
        """
        self._close_session_status_modal_if_open()
        IAAssert.is_not_true(
            value=self.session_status_modal_is_open(),
            failure_msg="Failed to close the Session Status modal.")

    def collapse_action_panel(self) -> None:
        """
        Collapse the Action Panel if it is open.

        :raises AssertionError: If the Action panel remains open.
        """
        if self.action_panel_is_expanded():
            self._action_panel_toggle_button.click()
            try:
                self._wait_for_action_panel_to_not_be_visible()
            except TimeoutException:
                # allow the following AssertionError to be raised
                pass
        IAAssert.is_not_true(
            value=self.action_panel_is_expanded(),
            failure_msg="Failed to close the Action panel.")

    def collapse(self) -> None:
        """
        Collapse every piece of the App Bar, until only the Revealer is present.

        :raises AssertionError: If unsuccessful in closing or collapsing every piece of the App Bar.
        """
        self.close_session_status_modal()
        self.close_about_modal_via_button()
        self.collapse_action_panel()
        if self.is_expanded():
            self._collapse_icon.click()
            self._wait_for_app_bar_to_be_fully_collapsed()
        IAAssert.is_not_true(
            value=self.is_expanded(),
            failure_msg="Failed to collapse the App Bar.")

    def exit_project(self) -> None:
        """
        Exit the Workstation Session. Unavailable outside of Workstation sessions.

        :raises TimeoutException: If used outside of Workstation.
        """
        self.expand()
        self._exit_project_icon.click()  # only available to Workstation

    def expand_action_panel(self) -> None:
        """
        Expand the Action panel.

        :raises AssertionError: If unsuccessful in expanding the Action Panel.
        """
        self._expand_action_panel_if_not_expanded()

    def expand(self) -> None:
        """
        Expand the App Bar.

        :raises AssertionError: If unsuccessful in expanding the App Bar.
        """
        self._expand_app_bar_if_not_expanded()
        IAAssert.is_true(
            value=self.is_expanded(),
            failure_msg="Failed to expand the App Bar.")

    def get_about_modal_title(self) -> Optional[str]:
        """
        Obtain the title text of the 'About' modal.

        :returns: The text of the title of the 'About' modal, or None if no text is configured to appear.

        :raises AssertionError: If unsuccessful in opening the 'About' modal.
        """
        self._open_about_modal_if_not_open()
        self._wait_for_about_modal_to_be_displayed()  # This piece outside of TOE so that it can raise its own TOE.
        try:
            return self._about_modal_and_session_status_modal_title.get_text()
        except TimeoutException:
            return None

    def get_tooltip_text(self) -> str:
        """
        Obtain the text of the displayed tooltip after hovering over the Revealer.

        :returns: The text of the tooltip.
        """
        self.hover_over_revealer()
        return self._tooltip.get_text()

    def get_connection_security(self) -> str:
        """
        Obtain the connection security status of the Session.

        :returns: The connection security of the Session, along the lines of "Insecure Connection".

        :raises AssertionError: If unsuccessful in expanding the Action Panel.
        """
        self._expand_action_panel_if_not_expanded()
        return self._connection_security_label.get_text()

    def get_connection_status(self) -> str:
        """
        Obtain the current connection status of the Session.

        :returns: The connection status of the Session, along the lines of "CONNECTED".

        :raises AssertionError: If unsuccessful in opening the Session Status modal.
        """
        self._select_gateway_tab()
        return self._connection_status_label.get_text()

    def get_count_of_notification_icons_in_app_bar(self) -> int:
        """
        Obtain a count of notification icons displayed within the App Bar.

        :returns: The number of notification icons found in the App Bar.

        :raises AssertionError: If unsuccessful in expanding the Action Panel.
        """
        self._expand_app_bar_if_not_expanded()  # This piece outside of TOE so that it can raise its own TOE.
        try:
            return len(self._generic_app_bar_notification_icon.find_all())
        except TimeoutException:
            return 0

    def get_count_of_notification_icons_in_revealer(self) -> int:
        """
        Obtain a count of notification icons displayed within the Revealer. Requires the Revealer be displayed, so
        we force a collapse of any open App Bar content first.

        :returns: The number of notification icons found in the Revealer.

        :raises AssertionError: If unsuccessful in collapsing the App Bar.
        """
        self.collapse()
        try:
            return len(self._generic_revealer_notification_icon.find_all())
        except TimeoutException:
            return 0

    def get_css_property_of_about_button(self, property_name: CSSPropertyValue) -> str:
        """
        Obtain any CSS property value of the 'About' button.

        :param property_name: The name of the CSS property you want information about.

        :returns: The underlying CSS property value of the About button.

        :raises AssertionError: If unsuccessful in expanding the Action Panel.
        """
        self._expand_app_bar_if_not_expanded()
        return self._about_button.get_css_property(property_name=property_name)

    def get_custom_view_height(self, include_units: bool = False) -> str:
        """
        Obtain the height of the custom View in use within the 'About' modal.

        :param include_units: Dictates whether the returned height contains units of measurement.

        :returns: The height of the custom View as a string, potentially with units.

        :raises AssertionError: If unsuccessful in opening the 'About' modal.
        """
        self._open_about_modal_if_not_open()
        return self._generic_custom_view_top_level.get_computed_height(include_units=include_units)

    def get_custom_view_width(self, include_units: bool = False) -> str:
        """
        Obtain the width of the custom View in use within the 'About' modal.

        :param include_units: Dictates whether the returned width contains units of measurement.

        :returns: The width of the custom View as a string, potentially with units.

        :raises AssertionError: If unsuccessful in opening the 'About' modal.
        """
        self._open_about_modal_if_not_open()
        return self._generic_custom_view_top_level.get_computed_width(include_units=include_units)

    def get_displayed_gateway_url(self) -> str:
        """
        Obtain the URL of the Gateway.

        :returns: The URL in use for the Gateway this Session is connected to.

        :raises AssertionError: If unsuccessful in opening the Session Status modal.
        """
        self._select_gateway_tab()
        return self._gateway_url_label.get_text()

    def get_displayed_project_name(self) -> str:
        """
        Obtain the name in use for the Project this Session is currently accessing.

        :returns: The name of the project this Page belongs to.

        :raises AssertionError: If unsuccessful in opening the Session Status modal.
        """
        self._select_project_tab()
        return self._project_name_label.get_text()

    def get_gateway_name(self) -> str:
        """
        Obtain the name of the Gateway this Project belongs to.

        :returns: The configured name of the Gateway.

        :raises AssertionError: If unsuccessful in opening the Session Status modal.
        """
        self._select_gateway_tab()
        return self._gateway_name.get_text()

    def get_icon_path_of_about_button(self) -> str:
        """
        Obtain the path of the icon in use for the 'About' button.

        :returns: The path in use by the <svg> of the 'About' button.

        :raises AssertionError: If unsuccessful in expanding the App Bar.
        """
        self._expand_app_bar_if_not_expanded()
        try:
            # Not using the standard icon structure because it isn't technically a Perspective component
            return self._about_button_local_symbol.find(wait_timeout=0).get_attribute("id")
        except TimeoutException:
            return self._about_button.get_icon_name()

    def get_logged_in_user(self) -> Optional[str]:
        """
        Obtain the name of the user currently logged in to this Session.

        :returns: The name of the user currently logged in, or None if no user is logged in.

        :raises AssertionError: If unsuccessful in expanding the Action Panel.
        """
        self._expand_action_panel_if_not_expanded()
        try:
            username = self._username_label.get_text()
            return username if username != "" else None
        except TimeoutException:
            return None

    def get_page_id(self) -> str:
        """
        Obtain the Page ID in use for this Page of the Session.

        :returns: The Perspective Page ID in use for this Page.

        :raises AssertionError: If unsuccessful in opening the Session Status modal.
        """
        self._open_session_status_modal_if_not_open()
        return self._page_id_label.get_text()

    def get_project_status(self) -> str:
        """
        Obtain the status of this project.

        :returns: The status of this project, along the lines of "Project Up to Date".

        :raises AssertionError: If unsuccessful in opening the Session Status modal.
        """
        self._select_project_tab()
        return self._up_to_date_status_label.get_text()

    def get_session_id(self) -> str:
        """
        Obtain the ID in use by this Session.

        :returns: The Perspective Session ID in use by this Session.

        :raises AssertionError: If unsuccessful in opening the Session Status modal.
        """
        self._open_session_status_modal_if_not_open()
        return self._session_id_label.get_text()

    def get_view_wrapper_height(self, include_units: bool = False) -> str:
        """
        Obtain the height of the wrapper of the custom View in use by the 'About' modal.

        :param include_units: Dictates whether the returned value includes units of measurement.

        :returns: The height of the View wrapper of the custom View within the 'About' modal as a string, potentially
            with units of measurement.

        :raises TimeoutException: If no custom View is in use.
        :raises AssertionError: If unsuccessful in opening the 'About' modal.
        """
        self._open_about_modal_if_not_open()
        return self._view_wrapper.get_computed_height(include_units=include_units)

    def get_view_wrapper_width(self, include_units: bool = False) -> str:
        """
        Obtain the width of the wrapper of the custom View in use by the 'About' modal.

        :param include_units: Dictates whether the returned value includes units of measurement.

        :returns: The width of the View wrapper of the custom View within the 'About' modal as a string, potentially
            with units of measurement.

        :raises TimeoutException: If no custom View is in use.
        :raises AssertionError: If unsuccessful in opening the 'About' modal.
        """
        return self._view_wrapper.get_computed_width(include_units=include_units)

    def hover_over_revealer(self) -> None:
        """
        Hover over the icon of the Revealer.
        """
        revealer_icon = \
            self._collapse_icon if self.is_expanded() else self._expand_icon
        revealer_icon.hover()
        revealer_icon.wait_on_binding(time_to_wait=0.5)

    def is_expanded(self) -> bool:
        """
        Determine if the App Bar is currently expanded.

        :returns: True, if the App Bar is spanning the bottom of the Page - False otherwise.
        """
        try:
            return self._action_panel_toggle_button.find().is_displayed() \
                and self._action_panel_toggle_button.get_termination().Y < self.selenium.get_inner_height()
        except TimeoutException:
            return False

    def learn_more_button_is_present(self) -> bool:
        """
        Determines if the 'LEARN MORE ABOUT IGNITION' button is currently displayed.

        :returns: True, if the button is currently displayed - False otherwise.
        :raises AssertionError: If unsuccessful in opening the 'About' modal.
        """
        self._open_about_modal_if_not_open()
        try:
            return self._learn_more_button.find() is not None
        except TimeoutException:
            return False

    def log_out(self) -> None:
        """
        Logs out any signed-in user.

        :raises AssertionError: If unsuccessful in expanding the Action Panel.
        """
        try:
            if self.get_logged_in_user() is not None:
                self.click_sign_out_button()
        finally:
            try:
                self.collapse()
            except TimeoutException:
                # ignore, because we may not be on a Perspective page any longer.
                pass

    def open_about_modal(self) -> None:
        """
        Open the 'About' modal.

        :raises AssertionError: If unsuccessful in opening the 'About' modal.
        """
        self._open_about_modal_if_not_open()

    def open_session_status_modal(self) -> None:
        """
        Open the 'Session Status' modal.

        :raises AssertionError: If unsuccessful in opening the Session Status modal.
        """
        self._open_session_status_modal_if_not_open()

    def revealer_displayed_in_position(self, toggle_position: TogglePosition) -> bool:
        """
        Determine if the Revealer is currently displayed in the expected position.

        :param toggle_position: The position in which you expect the Revealer to be displayed.

        :returns: True, if the Revealer is displayed in the supplied position - False otherwise.
        """
        return (f'bar-reveal-{toggle_position.value}' in self._revealer.find(wait_timeout=0).get_attribute('class'))\
            and self._revealer.find().is_displayed()

    def revealer_tooltip_is_displayed(self) -> bool:
        """
        Determine if the Revealer tooltip is currently displayed. This function does NOT hover over the Revealer icon;
        you must perform that step yourself.

        :returns: True, if the tooltip of the Revealer is currently displayed - False otherwise.
        """
        try:
            return self._tooltip.find(wait_timeout=0).is_displayed()
        except TimeoutException:
            return False

    def select_gateway_tab(self) -> None:
        """
        In the Session Status modal, select the Gateway tab.

        :raises AssertionError: If unsuccessful in opening the Session Status modal.
        """
        self._select_gateway_tab()

    def select_project_tab(self) -> None:
        """
        In the Session Status modal, select the Project tab.

        :raises AssertionError: If unsuccessful in opening the Session Status modal.
        """
        self._select_project_tab()

    def revealer_is_displayed(self) -> bool:
        """
        Determine if the Revealer is currently displayed.

        :returns: True, if the Revealer is currently displayed - False otherwise.
        """
        try:
            return self._revealer.find(wait_timeout=0).is_displayed()
        except TimeoutException:
            return False

    def session_status_modal_is_open(self) -> bool:
        """
        Determine if the Session Status modal is currently open.

        :returns: True, if the Session Status modal is currently open - False otherwise.
        """
        try:
            return self._session_status_modal.find(wait_timeout=0).is_displayed() \
                and "open" in self._session_status_modal.find().get_attribute("class") \
                and self._about_modal_and_session_status_modal_title.get_text() == self._SESSION_STATUS_MODAL_TITLE_TEXT
        except TimeoutException:
            return False

    def sign_in_button_is_displayed(self) -> bool:
        """
        Determine if the Action panel is currently displaying the SIGN IN button.

        :returns: True, if the SIGN IN button is currently displayed in the Action panel - False otherwise.

        :raises AssertionError: If unsuccessful in expanding the Action Panel.
        """
        self._expand_action_panel_if_not_expanded()
        try:
            return self._get_generic_text_button(button_text='SIGN IN').is_displayed()
        except IndexError:
            return False

    def sign_out_button_is_displayed(self) -> bool:
        """
        Determine if the Action panel is currently displaying the SIGN OUT button.

        :returns: True, if the SIGN OUT button is currently displayed in the Action panel - False otherwise.

        :raises AssertionError: If unsuccessful in expanding the Action Panel.
        """
        self._expand_action_panel_if_not_expanded()
        try:
            return self._get_generic_text_button(button_text="SIGN OUT").is_displayed()
        except IndexError:
            return False

    def status_button_is_displayed(self) -> bool:
        """
        Determine if the Action panel is currently displaying the STATUS button.

        :returns: True, if the STATUS button is currently displayed in the Action panel - False otherwise.

        :raises AssertionError: If unsuccessful in expanding the Action Panel.
        """
        self._expand_action_panel_if_not_expanded()
        try:
            return self._status_button.find(wait_timeout=0).is_displayed()
        except TimeoutException:
            return False

    def wait_for_revealer_or_app_bar_to_be_displayed(self, wait_timeout: int = 10) -> None:
        """
        Wait for the Session to display either the Revealer or the expanded App Bar. Useful for waiting for Perspective
        Pages.

        :param wait_timeout: The amount of time (in seconds) you ar wiling to wait for the Revealer to be present
            before allowing code to continue.

        :raises TimeoutException: If neither the Revealer nor the App Bar become visible in the alotted time.
        """
        try:
            WebDriverWait(driver=self.driver, timeout=wait_timeout).until(
                IAec.function_returns_true(custom_function=self._app_bar_or_revealer_is_displayed, function_args={}))
        except TimeoutException as toe:
            raise TimeoutException(msg="Neither the App Bar nor the Revealer ever became visible.") from toe

    def _app_bar_is_fully_collapsed(self) -> bool:
        """
        Determine if the App Bar is completely out of view of the user.

        :returns: True, if the App Bar is not visible to the user - False otherwise.
        """
        return self._app_bar_wrapper.get_origin().Y == self.selenium.get_inner_height()

    def _app_bar_is_fully_expanded(self) -> bool:
        """
        Determine if the App Bar is expanded and visible to the user.

        :returns: True, if the App Bar is expanded and visible to the user - False otherwise.
        """
        return self._app_bar_wrapper.get_termination().Y <= self.selenium.get_inner_height()

    def _app_bar_or_revealer_is_displayed(self) -> bool:
        """
        Determine if either the Revealer or the expanded App Bar is displayed to the user.

        :returns: True, if either the App Bar or Revealer is visible to the user - False otherwise.
        """
        revealer_is_displayed = False
        app_bar_is_displayed = False
        try:
            revealer_is_displayed = self.revealer_is_displayed()
        except TimeoutException:
            pass
        try:
            app_bar_is_displayed = self._app_bar_wrapper.find(wait_timeout=0).is_displayed()
        except TimeoutException:
            pass
        return revealer_is_displayed or app_bar_is_displayed

    def _click_about_button(self) -> None:
        """
        Click the 'About' button. This function performs special handling, as the button slides into view and clicks
        made too soon can result in no effect.
        """
        self._expand_app_bar_if_not_expanded()
        self.wait.until(
            IAec.element_is_fully_in_viewport(
                driver=self.driver, locator=self._ABOUT_IGNITION_ICON_LOCATOR))
        self._about_button.click()
        self._wait_for_animations_to_cease()

    def _click_action_panel_button(self) -> None:
        """
        Click the button which expands and collapses the Action panel. This function performs special handling, as the
        button slides into view and clicks made too soon can result in no effect.
        """
        self._expand_app_bar_if_not_expanded()
        self.wait.until(
            IAec.element_is_fully_in_viewport(
                driver=self.driver, locator=self._ACTION_PANEL_TOGGLE_BUTTON_LOCATOR))
        self._action_panel_toggle_button.click()

    def _close_session_status_modal_if_open(self) -> None:
        """
        Close the Session Status modal if it is open. If the modal is not open, no action is taken.
        """
        if self.session_status_modal_is_open():
            self._session_status_panel_close_icon.click()
            self._wait_for_session_status_modal_to_not_be_displayed()

    def _expand_action_panel_if_not_expanded(self) -> None:
        """
        Expand the App Bar if required before then expanding the Action panel.

        :raises AssertionError: If unsuccessful in expanding the Action Panel.
        """
        self._expand_app_bar_if_not_expanded()
        if not self.action_panel_is_expanded():
            self._action_panel_toggle_button.click()
            self._wait_for_action_panel_to_be_visible()
        IAAssert.is_true(
            value=self.action_panel_is_expanded(),
            failure_msg="Failed to expand the Action panel.")

    def _expand_app_bar_if_not_expanded(self) -> None:
        """
        Expand the App Bar, if it is not already expanded.

        :raises AssertionError: If unsuccessful in expanding the App Bar.
        """
        if not self.is_expanded():
            self._expand_icon.click(wait_timeout=0.5)
            self._wait_for_app_bar_to_be_fully_expanded()
        IAAssert.is_true(
            value=self.is_expanded(),
            failure_msg="Failed to expand the App Bar.")

    def _get_generic_text_button(self, button_text: str) -> WebElement:
        """
        Obtain a button within the Action panel based on its text.

        :returns: The WebElement "button" (<div>) with the specified text.
        """
        return Items(
            items=self._generic_text_button.find_all(
                wait_timeout=1)).filter(
            lambda e: e.text == button_text)[0]

    def _open_about_modal_if_not_open(self) -> None:
        """
        Expand the App Bar if required, and then click the About button.

        :raises AssertionError: If unsuccessful in opening the 'About' modal.
        """
        self._expand_action_panel_if_not_expanded()
        if not self.about_modal_is_displayed():
            self._about_button.click()
            self._wait_for_about_modal_to_be_displayed()
        IAAssert.is_true(
            value=self.about_modal_is_displayed(),
            failure_msg="We failed to open the 'About' modal."
        )

    def _open_session_status_modal_if_not_open(self) -> None:
        """
        Expand the App Bar, open the Action panel, and then click the STATUS button.

        :raises AssertionError: If unsuccessful in opening the Session Status modal.
        """
        self._expand_action_panel_if_not_expanded()
        if self.about_modal_is_displayed():  # About modal can interfere with click of STATUS button.
            self.close_about_modal_via_button()
        if not self.session_status_modal_is_open():
            self.click_status_button()
            self._wait_for_session_status_modal_to_be_displayed()
        IAAssert.is_true(
            value=self.session_status_modal_is_open(),
            failure_msg="We failed to open the Session Status modal."
        )

    def _select_gateway_tab(self) -> None:
        """
        Within the Session Status modal, select the Gateway tab.

        :raises AssertionError: If unsuccessful in opening the Session Status modal.
        """
        self._open_session_status_modal_if_not_open()
        self._gateway_tab.click()

    def _select_project_tab(self) -> None:
        """
        Within the Session Status modal, select the project tab.

        :raises AssertionError: If unsuccessful in opening the Session Status modal.
        """
        self._open_session_status_modal_if_not_open()
        self._project_tab.click()

    def _session_status_modal_is_open(self) -> bool:
        """
        Determine if the Session Status modal is open.

        :returns: True, if the Session Status modal is currently open and visible to the user - False otherwise.
        """
        try:
            return self._session_status_modal.find(wait_timeout=0).is_displayed() \
                and "open" in self._session_status_modal.find().get_attribute("class")
        except TimeoutException:
            return False

    def _wait_for_about_modal_to_be_displayed(self) -> None:
        """
        Wait for the 'About' modal to become visible.
        """
        try:
            self._animation_wait.until(
                IAec.function_returns_true(custom_function=self.about_modal_is_displayed, function_args={}))
        except TimeoutException as toe:
            raise TimeoutException(msg='The About modal never opened.') from toe

    def _wait_for_action_panel_to_be_visible(self) -> None:
        """
        Wait for the Action panel to become visible.
        """
        try:
            self._animation_wait.until(
                IAec.function_returns_true(custom_function=self.action_panel_is_expanded, function_args={}))
        except TimeoutException:
            pass

    def _wait_for_action_panel_to_not_be_visible(self) -> None:
        """
        Wait for the Action panel to become visible.
        """
        try:
            self._animation_wait.until(
                IAec.function_returns_false(custom_function=self.action_panel_is_expanded, function_args={}))
        except TimeoutException:
            pass

    def _wait_for_animations_to_cease(self) -> None:
        """
        Wait a period of time for any animations of the App Bar to complete.
        """
        sleep(self._ANIMATION_DELAY_IN_SECONDS)

    def _wait_for_app_bar_to_be_fully_collapsed(self) -> None:
        """
        Wait for the App Bar to be completely removed from view.
        """
        try:
            self._animation_wait.until(IAec.function_returns_true(
                custom_function=self._app_bar_is_fully_collapsed, function_args={}))
        except TimeoutException:
            pass

    def _wait_for_app_bar_to_be_fully_expanded(self) -> None:
        """
        Wait for the App Bar to be completely expanded and visible.
        """
        try:
            self._animation_wait.until(IAec.function_returns_true(
                custom_function=self._app_bar_is_fully_expanded, function_args={}))
        except TimeoutException:
            pass

    def _wait_for_session_status_modal_to_be_displayed(self) -> None:
        """
        Wait for the Session Status modal to be visible to the user.
        """
        try:
            self._animation_wait.until(
                IAec.function_returns_true(custom_function=self.session_status_modal_is_open, function_args={}))
        except TimeoutException:
            pass

    def _wait_for_session_status_modal_to_not_be_displayed(self) -> None:
        """
        Wait for the Session Status modal to be visible to the user.
        """
        try:
            self._animation_wait.until(
                IAec.function_returns_false(custom_function=self.session_status_modal_is_open, function_args={}))
        except TimeoutException:
            pass
