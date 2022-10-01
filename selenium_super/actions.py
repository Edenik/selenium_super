from datetime import time
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait

from selenium_super.enums import Until, ElementActions
import numpy as np
import scipy.interpolate as si


class Actions:
    def __init__(self, driver):
        self.driver = driver
        self.scroll = Scroll(self.driver)
        self.mouse_events = MouseEvents(self.driver)
        self.wait = Wait(self.driver)

    def focus(self, element: WebElement) -> None:
        """ Focuses on an element. """
        self.driver.execute_script('arguments[0].focus();', element)

    def click(self, element: WebElement) -> None:
        """ Clicks on an element. """
        self.driver.execute_script('arguments[0].click();', element)

    def blur(self, element: WebElement) -> None:
        """ Clear the focus from a selected web element. """
        self.driver.execute_script('arguments[0].blur();', element)

    def scroll_into_view(self, element: WebElement) -> None:
        """ Scrolls the element into view.  """
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

    def get_bounding_client_rect(self, element: WebElement) -> dict:
        """ Gets the bounding client rect of an element. """
        return self.driver.execute_script('return arguments[0].getBoundingClientRect();', element)

    def get_attribute(self, element: WebElement, attribute: str):
        """ Gets an element's attribute. """
        return self.driver.execute_script('return arguments[0].getAttribute(arguments[1]);', element, attribute)

    def set_attribute(self, element: WebElement, attribute: str, value):
        """ Sets an element's attribute. """
        return self.driver.execute_script(
            'return arguments[0].setAttribute(arguments[1], arguments[2]);', element, attribute, value
        )

    def remove_attribute(self, element: WebElement, attribute: str):
        """ Removes an element's attribute. """
        return self.driver.execute_script('return arguments[0].removeAttribute(arguments[1]);', element, attribute)

    def get_timezone_offset(self) -> int:
        """ Gets the timezone offset of the browser in minutes. """
        return self.execute_script('return new Date().getTimezoneOffset();')

    def set_coordinates(self, coordinates: tuple) -> None:
        """ Sets the geolocation for location services. """
        script = '''var latitude = arguments[0];
                    var longitude = arguments[1];
                    window.navigator.geolocation.getCurrentPosition = function(success) {
                        var position = {
                            "coords" : {
                                "latitude": latitude,
                                "longitude": longitude
                            }
                        };
                        success(position);
                }'''
        self.driver.execute_script(
            script,
            *coordinates,
        )

    def get_coordinates(self) -> tuple:
        script = '''var latitude = ''
                    var longitude = ''
                    window.navigator.geolocation.getCurrentPosition(function(pos) {
                        latitude = pos.coords.latitude;
                        longitude = pos.coords.longitude;
                    });
                    return [latitude, longitude];'''
        return self.driver.execute_script(script)


class Scroll:
    def __init__(self, driver):
        self.driver = driver

    def scroll_to_bottom(self, scroll_steps=250, bottom_crop_height=1000):
        verical_ordinate = scroll_steps
        page_height = self.driver.execute_script(
            "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight)"
        )
        total_jumps = int((page_height - bottom_crop_height) / scroll_steps)
        for i in range(0, total_jumps):
            self.driver.execute_script(
                "window.scrollTo(window.scrollY, {});".format(
                    verical_ordinate))
            verical_ordinate += scroll_steps
            time.sleep(0.20)

    def infinite_scroll_to_bottom(self, scroll_steps=250):
        verical_ordinate = scroll_steps
        last_height = None

        while True:
            self.driver.execute_script(f"window.scrollTo(window.scrollY, {verical_ordinate});")
            verical_ordinate += scroll_steps
            height = self.driver.execute_script("return (window.innerHeight + window.scrollY)")
            if last_height != height:
                last_height = height
                time.sleep(0.20)
            else:
                break

    def infinite(self, loading_selector, xpath):
        # Get scroll height after first time page load
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        # scroll_element = self.driver.execute_script(f'return document.evaluate("{xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue')
        scroll_element = f'document.evaluate("{xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue'
        while scroll_element:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait until element dissapear
            self.wait_until_element_disappear(loading_selector)
            print(last_height)
            # Calculate new scroll height and compare with last scroll height
            # new_height = self.driver.execute_script("return document.body.scrollHeight")
            elementProps = self.driver.execute_script(f'return {scroll_element}.getBoundingClientRect()')
            print(elementProps)
            new_height = self.driver.execute_script(
                f"return ({elementProps.get('height')} + {scroll_element}.scrollTop)")

            if new_height == last_height:
                break
            last_height = new_height

    def infinite_scroll_to_bottom_by_xpath(self, xpath=None, scroll_steps=250, data_append_function=None,
                                           loading_selector=None):
        try:
            data = []

            verical_ordinate = scroll_steps
            last_height = None
            scroll_element = f'document.evaluate("{xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue'
            # print(scroll_element)
            while scroll_element:
                print(f"{scroll_element}.scrollTo({scroll_element}.scrollTop, {verical_ordinate});")

                verical_ordinate += scroll_steps

                self.driver.execute_script(
                    f"{scroll_element}.scrollTo({scroll_element}.scrollTop, {verical_ordinate});")
                # self.driver.execute_script(f"window.scrollTo(0, {verical_ordinate});")
                if loading_selector:
                    self.wait_until_element_disappear(loading_selector)

                elementProps = self.driver.execute_script(f'return {scroll_element}.getBoundingClientRect()')
                height = self.driver.execute_script(
                    f"return ({elementProps.get('height')} + {scroll_element}.scrollTop)") if elementProps else 500

                if last_height != height:
                    last_height = height
                    if data_append_function:
                        data = data + (data_append_function() or [])
                    else:
                        time.sleep(0.20)
                else:
                    break

            if data_append_function: return list(data)
        except Exception as e:
            print(f'Error while trying to do infinite scroll on XPATH - {xpath}\nError: {e}')


class Wait:
    def __init__(self, driver):
        self.driver = driver

    def until(self, wait_element, method: Until, wait: int, base_element=None, action: ElementActions = None):
        base_element = base_element or self.driver
        element = WebDriverWait(base_element, wait).until(method(wait_element))
        if action and element:
            action(element)
        return element

    def until_not(self, wait_element, method: Until, wait: int, base_element=None, action: ElementActions = None):
        base_element = base_element or self.driver
        element = WebDriverWait(base_element, wait).until_not(method(wait_element))
        if action and element:
            action(element)
        return element

    def until_clickable_element(self, wait_element, wait, base_element=None, click=True):
        self.until(wait_element, Until.clickable, wait, base_element, action=ElementActions.click if click else None)

    def until_element_invisible(self, wait_element, wait, base_element=None):
        self.driver.implicitly_wait(0)
        return self.until(wait_element, Until.invisible, wait, base_element)


class MouseEvents:
    def __init__(self, driver):
        self.driver = driver

    def _trigger_mouse_event(self, element, click_event):
        script = '''var clickEvent = document.createEvent('MouseEvents');
                    clickEvent.initEvent(arguments[1], true, true);
                    arguments[0].dispatchEvent(clickEvent);'''
        self.driver.execute_script(script, element, click_event)

    def click(self, element):
        self._trigger_mouse_event(element, 'click')

    def mouse_up(self, element):
        self._trigger_mouse_event(element, 'mouseup')

    def mouse_down(self, element):
        self._trigger_mouse_event(element, 'mousedown')

    def mouse_over(self, element):
        self._trigger_mouse_event(element, 'mouseover')

    def human_like_mouse_move(self, base_element, click=False):
        action = ActionChains(self.driver)

        points = [[6, 2], [3, 2], [0, 0], [0, 2]]
        points = np.array(points)
        x = points[:, 0]
        y = points[:, 1]

        t = range(len(points))
        ipl_t = np.linspace(0.0, len(points) - 1, 100)

        x_tup = si.splrep(t, x, k=1)
        y_tup = si.splrep(t, y, k=1)

        x_list = list(x_tup)
        xl = x.tolist()
        x_list[1] = xl + [0.0, 0.0, 0.0, 0.0]

        y_list = list(y_tup)
        yl = y.tolist()
        y_list[1] = yl + [0.0, 0.0, 0.0, 0.0]

        x_i = si.splev(ipl_t, x_list)
        y_i = si.splev(ipl_t, y_list)

        action.move_to_element(base_element)

        if click:
            action.click().perform()
        else:
            action.perform()

        c = 5
        i = 0
        for mouse_x, mouse_y in zip(x_i, y_i):
            action.move_by_offset(mouse_x, mouse_y)
            action.perform()
            i += 1
            if i == c:
                break



class Other:
    def __init__(self, driver):
        self.driver = driver

