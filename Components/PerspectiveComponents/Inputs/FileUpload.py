from typing import List, Optional, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from Components.BasicComponent import BasicPerspectiveComponent, ComponentPiece
from Components.Common.FileUpload import FileUpload as CommonFileUpload
from Components.PerspectiveComponents.Common.ComponentModal import ComponentModal
from Components.PerspectiveComponents.Common.Icon import CommonIcon


class FileUpload(BasicPerspectiveComponent, CommonFileUpload):
    """
    A Perspective File Upload Component.

    The File Upload can render at one of three sizes based on its dimensions: small, medium, and large. Many functions
    in this class will not work while the File Upload is in the small layout because although we are able to expand
    the modal which has the information those functions would need, we are unable to then remove the modal without
    the risk of unintentionally interacting with another component.

    Also, some functions require the File upload component to be in a specific size. Those functions denote the
    required size.
    """
    _SPAN_LOCATOR = (By.CSS_SELECTOR, "span.display-message")
    _PRIMARY_SVG_LOCATOR = (By.CSS_SELECTOR, 'svg[class^="ia_fileUploadComponent--mobile"]')
    _SUPPORTED_FILE_TYPES_WRAPPER_LOCATOR = (By.CSS_SELECTOR, "div.file-types-supported")
    _SUPPORTED_FILE_TYPES_ICON_LOCATOR = (By.CSS_SELECTOR, ".ia_fileUploadComponent__supportedFileTypes__icon")
    _TOOLTIP_LOCATOR = (By.CSS_SELECTOR, "div.component-tooltip")
    _PRIMARY_MESSAGE_LOCATOR = (By.CSS_SELECTOR, "span.primary-message")
    _SECONDARY_MESSAGE_LOCATOR = (By.CSS_SELECTOR, "span.secondary-message")
    _PAGINATION_WRAPPER_LOCATOR = (By.CSS_SELECTOR, "div.pagination-wrapper")
    _FILE_SUMMARY_WRAPPER = (By.CSS_SELECTOR, "div.file-summary")
    _FILE_MESSAGE_LOCATOR = (By.CSS_SELECTOR, "span.file-message")
    _NEXT_PAGE_LINK_LOCATOR = (By.CSS_SELECTOR, "a.next")
    _PREVIOUS_PAGE_LINK_LOCATOR = (By.CSS_SELECTOR, "a.previous")
    _CLEAR_UPLOADS_LINK = (By.CSS_SELECTOR, "div.clear-icon a")
    _FILE_WRAPPER_LOCATOR = (By.CSS_SELECTOR, "div.file-wrapper")
    _FILE_NAME_LOCATOR = (By.CSS_SELECTOR, "div.file-name")
    _FILE_RESULT_LOCATOR = (By.TAG_NAME, "span")
    _SUCCESS_MESSAGE_LOCATOR = (By.CSS_SELECTOR, "div.success-message")
    _ERROR_LOCATOR = (By.CSS_SELECTOR, "div.error")

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
        self._display_message = ComponentPiece(
            locator=self._SPAN_LOCATOR, driver=driver, parent_locator_list=self.locator_list, poll_freq=poll_freq)
        self._primary_icon = CommonIcon(
            locator=self._PRIMARY_SVG_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._supported_file_types_icon = CommonIcon(
            locator=self._SUPPORTED_FILE_TYPES_ICON_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._tooltip = ComponentPiece(
            locator=self._TOOLTIP_LOCATOR,
            driver=driver,
            parent_locator_list=None,
            poll_freq=poll_freq)
        self._supported_file_types_text_wrapper = ComponentPiece(
            locator=self._SUPPORTED_FILE_TYPES_WRAPPER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._primary_message = ComponentPiece(
            locator=self._PRIMARY_MESSAGE_LOCATOR,
            driver=driver,
            parent_locator_list=self._supported_file_types_text_wrapper.locator_list,
            poll_freq=poll_freq)
        self._secondary_message = ComponentPiece(
            locator=self._SECONDARY_MESSAGE_LOCATOR,
            driver=driver,
            parent_locator_list=self._supported_file_types_text_wrapper.locator_list,
            poll_freq=poll_freq)
        self._pagination_wrapper = ComponentPiece(
            locator=self._PAGINATION_WRAPPER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self.__file_summary_wrapper = ComponentPiece(
            locator=self._FILE_SUMMARY_WRAPPER,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._file_message = ComponentPiece(
            locator=self._FILE_MESSAGE_LOCATOR,
            driver=driver,
            parent_locator_list=self._pagination_wrapper.locator_list,
            poll_freq=poll_freq)
        self._next_page_link = ComponentPiece(
            locator=self._NEXT_PAGE_LINK_LOCATOR,
            driver=driver,
            parent_locator_list=self._pagination_wrapper.locator_list,
            poll_freq=poll_freq)
        self._previous_page_link = ComponentPiece(
            locator=self._PREVIOUS_PAGE_LINK_LOCATOR,
            driver=driver,
            parent_locator_list=self._pagination_wrapper.locator_list,
            poll_freq=poll_freq)
        self.__file_wrapper = ComponentPiece(
            locator=self._FILE_WRAPPER_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            poll_freq=poll_freq)
        self._file_name = ComponentPiece(
            locator=self._FILE_NAME_LOCATOR,
            driver=driver,
            parent_locator_list=self.__file_wrapper.locator_list,
            poll_freq=poll_freq)
        self._file_result = ComponentPiece(
            locator=self._FILE_RESULT_LOCATOR,
            driver=driver,
            parent_locator_list=self.__file_wrapper.locator_list,
            poll_freq=poll_freq)
        self._modal = ComponentModal(driver=driver, poll_freq=poll_freq)

    def all_extensions_allowed(self) -> bool:
        """
        Determine if all extensions are currently allowed for the File Upload. Does not work for File Uploads which use
        the "small" layout, because we would need to expand the modal - but there is no good way to then remove the
        modal.

        :returns: True, if there are no file extension restrictions in place for the component. False if any
            restrictions are in place.

        :raises TypeError: If the File Upload is in the "small" layout. This error is raised because there could
            actually be restrictions in place, but we are unable to locate them.
        """
        if self.is_using_small_layout():
            raise ValueError("Unable to verify file restrictions while the File Upload is using the 'small' layout.")
        return not self.is_displaying_hover_info_icon()

    def clear_uploads(self, max_number_of_attempts: int = 10) -> None:
        """
        Reset the File Upload Component back to its default state after having uploaded files.

        :param max_number_of_attempts: How many times you are willing to click the next page arrow in order to reach
            the upload summary before giving up.

        :raises TimeoutException: If there were no uploads to clear, or if we failed to reach the summary of uploads
            after clicking next page arrow as many times as specified in max_number_of_attempts.
        """
        attempts = 0
        while not self.summary_panel_is_visible() and attempts < max_number_of_attempts:
            self.click_next_page()
            attempts += 1
        self._get_clear_uploads_link().click(wait_timeout=1)

    def click_next_page(self) -> None:
        """
        Click the next page arrow in the upload summary pagination area.

        :raises TimeoutException: If already on the last page, or if the summary is not present.
        """
        self._next_page_link.click(binding_wait_time=1)

    def click_previous_page(self) -> None:
        """
        Click the previous page arrow in the upload summary pagination area.

        :raises TimeoutException: If already on the first page, or if the summary is not present.
        """
        self._previous_page_link.click(binding_wait_time=1)

    def _expose_file_input_element(self) -> None:
        """
        While using the small layout, the required <input> element is not actually in the DOM, so we must click the
        component in order to expose the <input>.
        """
        if self.is_using_small_layout():
            self.click()

    def extension_is_allowed(self, extension: str) -> bool:
        """
        Determine if the supplied case-insensitive extension is listed as being restricted.

        :returns: True, if the supplied case-insensitive extension is currently restricted - False otherwise.
        """
        all_extensions_allowed = self.all_extensions_allowed()
        if not all_extensions_allowed:
            extension = extension.replace(".", "").upper()
            if self.is_displaying_hover_info_icon():
                return extension in self.get_information_hover_text()
            else:
                return extension in self._secondary_message.get_text()
        return all_extensions_allowed

    def get_current_page_index(self) -> int:
        """
        Obtain the page index of the upload summary.

        :returns: -1 if on the Summary (last) page, otherwise the current page of the summary pagination.
        """
        try:
            return int(self._file_message.get_text().split(" ")[0])
        except IndexError:
            return -1

    def get_display_message(self) -> str:
        """
        Obtain the message displayed while in the default configuration.

        :raises TimeoutException: If the component is not in the default or reset configuration.
        """
        return self._display_message.get_text()

    def get_filename_for_current_page(self) -> str:
        """
        Obtain the name of the file being summarized on this page of the summary.

        :raises TimeoutException: If on the Summary page or if the summary pagination panel is not present.
        """
        return self._file_name.get_text()

    def get_icon_color(self) -> str:
        """
        Obtain the color of the icon as a string

        :raises TimeoutException: If the component is not in the 'small' layout.
        """
        return self._primary_icon.get_fill_color()

    def get_icon_name(self) -> str:
        """
        Obtain a slash delimited path of the icon (someLibrary/iconId).

        :raises TimeoutException: If the component is not in the 'small' layout.
        """
        return self._primary_icon.get_icon_name()

    def get_information_hover_text(self) -> str:
        """
        Obtain the text a user would see when they hover over the information icon. Requires the File Upload be in the
        'medium' layout.

        :raises TimeoutException: If the File Upload is not in the 'medium' layout, or if no information icon is
            displayed. The information icon is only displayed while in the medium layout AND file extension restrictions
            are in place for the component.
        """
        self.hover_over_info_icon()
        return self._tooltip.get_text()

    def get_result_for_current_page(self) -> str:
        """
        Obtain the result message for the current page within the upload summary pagination area.

        :raises TimeoutException: If on the Summary page or if no pagination area is present.
        """
        return self._file_result.get_text()

    def get_total_count_of_results(self) -> int:
        """
        Obtain a count of how many files were uploaded during the last event.

        :raises TimeoutException: If the component is not currently displaying a summary of the upload.
        """
        on_summary_page = self.get_current_page_index() == -1
        if on_summary_page:
            self.click_previous_page()
            self.wait_on_binding(time_to_wait=0.5)
        count_of_results = int(self._file_message.get_text().split(" ")[-1])
        if on_summary_page:
            self.click_next_page()
        return count_of_results

    def get_warning_text(self) -> str:
        """
        Obtain the warning text displayed as part of the upload event.

        :raises TimeoutException: If no warning is currently displayed.
        """
        try:
            return self._get_file_upload_error().find(wait_timeout=0.5).text
        except TimeoutException:
            return ""

    def hover_over_info_icon(self) -> None:
        """
        Hover over the information icon of the component. Requires the File Upload be in the 'medium' layout, and also
        requires that file extension restrictions be in place.

        :raises TimeoutException: If the component is not in the 'medium' layout, or if no file extension restrictions
        are in place for the component.
        """
        self._supported_file_types_icon.hover()

    def is_using_small_layout(self) -> bool:
        """Determine if the component is currently rendering in the 'small' layout."""
        try:
            return self._primary_icon.find(wait_timeout=0) is not None
        except TimeoutException:
            return False

    def is_displaying_hover_info_icon(self, wait_timeout: int = 1) -> bool:
        """
        Determine if the component is currently displaying the information icon.

        :returns: True, if in the 'medium' layout AND file extension restrictions are in place for the component. False
            if rendering in the 'small' or 'large' layout OR no file extension restrictions are in place.
        """
        try:
            return self._supported_file_types_icon.find(wait_timeout=wait_timeout) is not None
        except TimeoutException:
            return False

    def is_displaying_results(self) -> bool:
        """
        Determine if the upload summary results pagination area is currently displayed.

        :returns: True, if the pagination area is displayed - False otherwise.
        """
        try:
            return self._pagination_wrapper.find() is not None
        except TimeoutException:
            return False

    def navigate_to_file_summary_by_index(self, desired_index: int) -> None:
        """
        Within the upload summary pagination area, navigate to a specific page index. To navigate to the Summary panel,
        supply a value of -1.

        :raises TimeoutException: If the pagination panel is not currently displayed.
        """
        if self.summary_panel_is_visible():
            self.click_previous_page()
        current_index = self.get_current_page_index()
        # stop if we reach the desired page or the summary page
        while current_index != desired_index and current_index != -1:
            self._previous_page_link.click(binding_wait_time=0.5) if current_index > desired_index \
                else self._next_page_link.click(binding_wait_time=0.5)
            current_index = self.get_current_page_index()

    def next_page_link_is_enabled(self) -> bool:
        """
        Determine if the 'next page' arrow (<a>) is enabled.

        :raises TimeoutException: If the pagination panel is not currently present.
        """
        return "disabled" not in self._next_page_link.find().get_attribute("class")

    def previous_page_link_is_enabled(self) -> bool:
        """
        Determine if the 'previous page' arrow (<a>) is enabled.

        :raises TimeoutException: If the pagination panel is not currently present.
        """
        return "disabled" not in self._previous_page_link.find().get_attribute("class")

    def small_layout_modal_is_displayed(self) -> bool:
        """Determine if the 'Browse' button modal is displayed while using the 'small' layout."""
        try:
            return ComponentPiece(
                locator=self._SPAN_LOCATOR,
                driver=self.driver,
                wait_timeout=1,
                parent_locator_list=self._modal.locator_list).find() is not None
        except TimeoutException:
            return False

    def summary_panel_is_visible(self) -> bool:
        """Determine if the Summary panel is visible in the upload summary pagination panel."""
        try:
            return "Summary" in self._file_message.find(wait_timeout=0.5).text
        except TimeoutException:
            return False

    def upload_file_by_path(self, normalized_file_path: str) -> None:
        """
        Upload an individual file by supplying a normalized file path.

        :param normalized_file_path: An OS-agnostic string file path.
        """
        self.upload_files(normalized_file_path_list=[normalized_file_path])

    def upload_files(self, normalized_file_path_list: List[str]) -> None:
        """
        Upload a list of files by supplying normalized file paths.

        :param normalized_file_path_list: A list of OS-agnostic string file paths.
        """
        self.driver.execute_script('arguments[0].style.display="block";', self._find_file_input())
        self._find_file_input().send_keys('\n'.join(normalized_file_path_list))
        self.driver.execute_script('arguments[0].style.display="none";', self._find_file_input())

    def upload_was_successful(self) -> bool:
        """
        Determine if the previous upload attempt was successful.

        :returns: True, if the event was successful. False if ANY file encountered an issue or if the component
            is not displaying an upload summary.
        """
        # small file upload renders success in modal/popover format.
        parent_locator_list = self._modal.locator_list if self.is_using_small_layout() else self.locator_list
        try:
            return ComponentPiece(
                locator=self._SUCCESS_MESSAGE_LOCATOR,
                driver=self.driver,
                parent_locator_list=parent_locator_list,
                poll_freq=self.poll_freq).find(wait_timeout=5).text == 'Upload Successful!'
        except TimeoutException:
            return False

    def warning_is_displayed(self) -> bool:
        """
        Determine if a warning is currently displayed for the component.

        :returns: True, if a warning is currently displayed - False otherwise.
        """
        try:
            return self._get_file_upload_error().find(wait_timeout=0.5) is not None
        except TimeoutException:
            return False

    def _find_file_input(self) -> WebElement:
        """
        Obtain the necessary <input> element so that we can use it to upload files.

        :raises TimeoutException: If unable to locate the required WebElement.
        """
        self._expose_file_input_element()
        # small file upload renders inputs in modal/popover format.
        return ComponentPiece(
            locator=self._INPUT_LOCATOR,
            driver=self.driver,
            parent_locator_list=self._modal.locator_list if self.is_using_small_layout() else self.locator_list,
            poll_freq=self.poll_freq).find(wait_timeout=2)

    def _get_file_upload_error(self) -> ComponentPiece:
        """
        Obtain the error ComponentPiece.
        """
        return ComponentPiece(
            locator=self._ERROR_LOCATOR,
            driver=self.driver,
            parent_locator_list=self._modal.locator_list if self.is_using_small_layout() else self.locator_list,
            poll_freq=self.poll_freq)

    def _get_clear_uploads_link(self) -> ComponentPiece:
        """
        Obtain the clear uploads link (circular refresh icon) as a ComponentPiece.
        """
        return ComponentPiece(
            locator=self._CLEAR_UPLOADS_LINK,
            driver=self.driver,
            parent_locator_list=self._modal.locator_list if self.is_using_small_layout() else self.locator_list,
            poll_freq=self.poll_freq)
