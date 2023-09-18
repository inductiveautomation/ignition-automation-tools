from typing import Union, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from Components.BasicComponent import ComponentPiece


class ComponentModal(ComponentPiece):
    """
    A Perspective Component Modal, unique from the modal in use by Perspective Popups. The Component Modal is often
    used by Dropdowns and interactive menus to display available options.
    """
    _LOCATOR = (By.CSS_SELECTOR, 'div.ia_componentModal')

    def __init__(
            self,
            driver: WebDriver,
            wait_timeout: Union[float, int] = 2,
            description: Optional[str] = None,
            poll_freq: float = 0.5):
        super().__init__(
            locator=self._LOCATOR,
            driver=driver,
            wait_timeout=wait_timeout,
            description=description,
            poll_freq=poll_freq)
