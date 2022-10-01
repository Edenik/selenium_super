from enum import Enum
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement


class Until(Enum):
    clickable = EC.element_to_be_clickable
    visible = EC.visibility_of_element_located
    visibles = EC.visibility_of_all_elements_located
    present = EC.presence_of_element_located
    presents = EC.presence_of_all_elements_located
    invisible = EC.invisibility_of_element_located


class ElementActions(Enum):
    """
    Set of supported web element actions.
    """
    click = WebElement.click
    send_keys = WebElement.send_keys
    submit = WebElement.submit
    clear = WebElement.clear


class By:
    """
    Set of supported locator strategies.
    """

    ID = "id"
    XPATH = "xpath"
    LINK_TEXT = "link text"
    PARTIAL_LINK_TEXT = "partial link text"
    NAME = "name"
    TAG_NAME = "tag name"
    CLASS_NAME = "class name"
    CSS_SELECTOR = "css selector"
