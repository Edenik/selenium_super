import base64
import json
import codecs
from pathlib import Path
import platform
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities    
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver

from .file_utils import load_json_file, write_json_file
from .localstorage import LocalStorage

class SuperWebDriver(webdriver.Firefox, webdriver.Chrome):
    def __init__(self, config_path):
        self.load_browser_config(config_path)
        self.driver = self.get_web_driver(init=True)
        self.local_storage = LocalStorage(self.driver)
        self.selectors = {}
        
    def load_browser_config(self, file_path):
        config = load_json_file(file_path=file_path)
        if not config:
            print('Could not load browser config file!')
        else:
            self.browser = config.get('use_browser', None)
            self.options = config.get('options', None) 
            self.headless = config.get('headless', None)
            self.download_folder = config.get('download_folder', None)
            
            self.chrome_executable_path = config.get('chrome_executable_path', None)        
            self.chrome_profile = config.get('chrome_profile', None)
            self.chrome_logger = config.get('chrome_logger', None)

            self.firefox_executable_path = config.get('firefox_executable_path', None) 
            self.firefox_binary_location = config.get('firefox_binary_location', None)       
            
            self.default_linux_options = ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--profile-directory=Default', '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.101 Safari/537.36', '--user-data-dir=~/.config/google-chrome']
            self.default_chrome_options = ['--log-level=3', 'window-size=1920,1080', '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.101 Safari/537.36']
            self.default_firefox_options = []
            
    def get_web_driver(self, init=False) -> webdriver:
        if init is False and self.driver is not None:
            return self.driver
        elif platform.system() == 'Linux':
            print('Starting selenium using Chrome - Linux')
            options = ChromeOptions()
            if self.headless is not None:
               options.headless = self.headless
            for option in self.options or self.default_linux_options:
                options.add_argument(option)
            driver = webdriver.Chrome.__init__(self, options=options)
            return driver
        elif self.browser == 'chrome':
            print('Starting selenium using Chrome - Windows')
            capabilities = DesiredCapabilities.CHROME.copy()
            options = ChromeOptions()
            for option in self.options or self.default_chrome_options:
                options.add_argument(option)
            
            if self.chrome_logger:
                capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
            if self.headless is not None:
               options.headless = self.headless
            if self.chrome_profile:
                options.add_argument(f"--user-data-dir={self.chrome_profile}")
            if self.download_folder:
                options.add_experimental_option(
                "prefs", {
                    "download.default_directory":
                    self.download_folder,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True
                })
            
            driver = webdriver.Chrome.__init__(self,
                executable_path=self.chrome_executable_path,
                options=options, desired_capabilities=capabilities)

            return driver
        elif self.browser == 'firefox':
            print('Starting selenium using Chrome - Firefox')
            options = Options()
            options.binary_location = self.firefox_binary_location
            for option in self.options or self.default_firefox_options:
                options.add_argument(option)
            driver = webdriver.Firefox(
                executable_path=self.firefox_executable_path,
                options=options)
            return driver
        else:
            print('Could not start driver, please fix browser_config.json file')

    def validate_element(self, element):
        return element is not None \
                and element.get('by') is not None \
                and element.get('value') is not None

    def load_cookies(self, cookies): 
        try:
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        except Exception as e:
            print('Error loading cookies, {}'.format(e))
        
    def load_auth_data(self, folder_path):
        has_auth_data = Path(folder_path + 'auth.json').is_file()

        if (has_auth_data):
            auth_file = load_json_file(folder_path + './auth.json')
            local_storage = auth_file.get('localstorage', [])
            
            try:
                for key, value in local_storage.items():
                    self.local_storage.set(key, value)
            except Exception as e:
                print('Error loading local storage items, {}'.format(e))

            self.load_cookies(auth_file.get('cookies', []))

        return has_auth_data

    def save_auth_data(self, folder_path):
        obj = {}
        local_storage_items = self.local_storage.items().items()

        for key, value in local_storage_items:
            obj[key] = value

        write_json_file(folder_path + 'auth.json',
                        "w+", {
                            'cookies': self.driver.get_cookies(),
                            'localstorage': obj
                        },
                        stringify=True)

    def do_login(self, login_url, username, password, elements, fetch_url=True):
        """
        Args:
            login_url (str): login url of the service
            username (str): username / email of the user
            password (str): user password
            elements (dict(dict("by", "value"))): 
                        dict with 3 keys:
                        "user_input"
                        "pass_input"
                        "login_button:
                        
                        each key should contain a dict 
                        with the following keys: (example)
                        {
                            "user_input" : {"by": By.NAME, "value" : "username"},
                            "pass_input" : {"by": By.NAME, "value" : "Password"},
                            "login_button" : {"by": By.ID, "value" : "submitbut"}
                        }

        Returns:
            if success -
                driver
            else:
                None
        """
        validated_user_input = self.validate_element(
            elements.get('user_input', {}))
        validate_pass_input = self.validate_element(
            elements.get('pass_input', {}))
        validated_login_button = self.validate_element(
            elements.get('login_button', {}))

        if validate_pass_input is False or validated_user_input is False or validated_login_button is False:
            print('properties are not valid')
            return None

        try:
            driver = self.get_web_driver()
            if fetch_url: driver.get(login_url)

            user_input = driver.find_element(
                by=elements['user_input']['by'], value=elements['user_input']['value'])
            user_input.send_keys(username)
            user_input.send_keys('\ue00c')
            pass_input = driver.find_element(
                by=elements['pass_input']['by'], value=elements['pass_input']['value'])
            pass_input.send_keys(password)
            pass_input.send_keys('\ue00c')
            button = driver.find_element(
                by=elements['login_button']['by'], value=elements['login_button']['value'])
            button.click()

            return driver
        except Exception as e:
            print('Error while trying login to -\n{}\n[Error] - {}'.format(
                login_url, e))

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
            
    def wait_until_element_disappear(self, selector):
        self.driver.implicitly_wait(0)
        WebDriverWait(self.driver, 30).until(EC.invisibility_of_element_located((selector.get('by'), selector.get('value'))))
        
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
            new_height =  self.driver.execute_script(f"return ({elementProps.get('height')} + {scroll_element}.scrollTop)") 

            if new_height == last_height:
                break
            last_height = new_height
                    
    def infinite_scroll_to_bottom_by_xpath(self, xpath=None, scroll_steps=250, data_append_function=None, loading_selector=None):
        try:
            data = []
            
            verical_ordinate = scroll_steps
            last_height = None 
            scroll_element = f'document.evaluate("{xpath}", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue'
            # print(scroll_element)
            while scroll_element:
                print(f"{scroll_element}.scrollTo({scroll_element}.scrollTop, {verical_ordinate});")
                
                verical_ordinate += scroll_steps

                self.driver.execute_script(f"{scroll_element}.scrollTo({scroll_element}.scrollTop, {verical_ordinate});")
                # self.driver.execute_script(f"window.scrollTo(0, {verical_ordinate});")
                if loading_selector:
                    self.wait_until_element_disappear(loading_selector)
                    
                elementProps = self.driver.execute_script(f'return {scroll_element}.getBoundingClientRect()')
                height =  self.driver.execute_script(f"return ({elementProps.get('height')} + {scroll_element}.scrollTop)") if elementProps else 500
                
                if last_height != height:
                    last_height = height
                    if data_append_function:
                        data = data + (data_append_function() or [])
                    else: time.sleep(0.20)
                else:
                    break
            
            if data_append_function: return list(data)
        except Exception as e:
            print(f'Error while trying to do infinite scroll on XPATH - {xpath}\nError: {e}')
            
    def load_selectors_file(self, path):
        config = load_json_file(path)
        by_options = {
            "By.XPATH": By.XPATH,
            "By.NAME": By.NAME,
            "By.CLASS_NAME": By.CLASS_NAME,
            "By.CSS_SELECTOR": By.CSS_SELECTOR,
            "By.ID": By.ID,
            "By.LINK_TEXT": By.LINK_TEXT,
            "By.TAG_NAME": By.TAG_NAME
        }

        loaded_config = {}
        for key, val in config.items():
            by = by_options[val.get('by')]
            value = val.get('value')
            loaded_config[key] = {"by": by, "value": value}

        self.selectors = loaded_config
        return loaded_config

    def get_selectors(self):
        return self.selectors
    
    def get_selector_value(self, selector):
        return self.selectors.get(selector, {}).get('value', None)

    def get_elements_by_selector(self,
                                 selector_name=None,
                                 base_element=None,
                                 multiple=False,
                                 attribute=None,
                                 filter=None,
                                 xpath=None,
                                 wait=0):

        try:
            
            if xpath is None:
                by = self.selectors.get(selector_name)
                value = self.selectors.get(selector_name)

                if by is None or value is None:
                    print('No selector {} found in configuration file'.format(
                        selector_name))
                    return None
                
                by = by.get('by', None)
                value = value.get('value', None)

            else:
                by = By.XPATH
                value = xpath
                
            search_element = self.driver if base_element is None else base_element

            if not multiple:
                element = WebDriverWait(search_element, wait).until(
                    EC.presence_of_element_located((by, value)))

                if attribute is not None and element is not None:
                    return element.get_attribute(
                        attribute) if filter is None else filter(
                            element.get_attribute(attribute))
                return element

            elif multiple:
                elements = WebDriverWait(search_element, wait).until(
                    EC.presence_of_all_elements_located((by, value)))
                if attribute is not None and elements is not None:
                    attributes_data = []
                    for element in elements:
                        if filter is None:
                            attributes_data.append(
                                element.get_attribute(attribute))
                        else:
                            attributes_data.append(
                                filter(element.get_attribute(attribute)))
                    return attributes_data
                return elements
        except Exception as e:
            print(e)
            return None

    def wait_for_clickable_element(self,
                                   clickable_element,
                                   base_element=None,
                                   wait=5):
        if base_element is not None:
            WebDriverWait(base_element, wait).until(
                EC.element_to_be_clickable(clickable_element))
        else:
            WebDriverWait(self.driver, wait).until(
                EC.element_to_be_clickable(clickable_element))

    def get_file_content_chrome(self, uri):
        result = self.driver.execute_async_script("""
            var uri = arguments[0];
            var callback = arguments[1];
            var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
            var xhr = new XMLHttpRequest();
            xhr.responseType = 'arraybuffer';
            xhr.onload = function(){ callback(toBase64(xhr.response)) };
            xhr.onerror = function(){ callback(xhr.status) };
            xhr.open('GET', uri);
            xhr.send();
            """, uri)
        if type(result) == int :
            raise Exception("Request failed with status %s" % result)
        return base64.b64decode(result)

    def save_screenshot(self, name, path, element):
        full_path = f"{path}{name}.png"
        print("Saving image in - {}".format(full_path))
        element.screenshot(full_path)
        return full_path
            
    def save_html(self, name, path):
        with codecs.open(f"{path}{name}.html", "w", "utf-8") as html:
            full_path = f"{path}{name}.html"
            print("Saving HTML in - {}".format(full_path))
            html.write(self.driver.page_source)
            return full_path
        
    def record_responses(self):
        logs = self.driver.get_log('performance')
        responses = []
        for log in logs:
            if log['message']:
                log = json.loads(log['message'])['message']
                try:
                    if ("Network.responseReceived" in log["method"] and "json" in log["params"]["response"]["mimeType"]):
                        try:
                            body = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': log["params"]["requestId"]})
                            log['body'] = json.loads(body['body'])
                            responses.append(log)
                        except Exception as e:
                            responses.append(log)
                except Exception as e:
                    print(e)   
                    
        return responses
                
    def save_responses(self, file_path=None):
        logs  = self.record_responses()
        json_object = {
            'logs' : logs,
        }
        if file_path: file = write_json_file(file_path=file_path, write_mode='w+', json_object=json_object, stringify=True, log=True)   
        return logs
    
    def click_element_by_xpath(self, xpath):
        self.driver.execute_script("""document.evaluate({}, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue?.click()""".format(xpath))