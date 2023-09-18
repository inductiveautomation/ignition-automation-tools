from typing import List, Optional, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import BasicComponent, ComponentPiece


class FileUpload(BasicComponent):
    """
    A Common/shared implementation of a File upload, used both within Perspective and the gateway.
    """
    _BUTTON_LOCATOR = (By.TAG_NAME, f"button.primary")
    _INPUT_LOCATOR = (By.CSS_SELECTOR, "input")

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
        self._button = ComponentPiece(
            locator=self._BUTTON_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            description="The button within the File Upload which actually opens the OS dialog.",
            poll_freq=poll_freq)
        self._input = ComponentPiece(
            locator=self._INPUT_LOCATOR,
            driver=driver,
            parent_locator_list=self.locator_list,
            description="The hidden input within the File Upload which can be used to specify file paths.")

    def get_button_text(self) -> str:
        """
        Obtain the text displayed within the button of the File Upload.

        :returns: The text displayed to the user within the button of the File Upload.

        :raises TimeoutException: If the File Upload is rendering in a manner which does not include a button.
        """
        return self._button.get_text()

    def is_enabled(self) -> bool:
        """
        Determine if the File Upload is enabled.

        :returns: True, if the File Upload is currently enabled - False otherwise.

        :raises TimeoutException: If the File Upload is rendering in a manner which does not include a button.
        """
        return "disabled" not in self._button.find().get_attribute("class")

    def upload_file_by_path(self, normalized_file_path: str) -> None:
        """
        Supply the location of a file to be uploaded.

        :param normalized_file_path: The normalized (OS-agnostic) path to the file to be uploaded.
        """
        self._input.find().send_keys(normalized_file_path)
