import platform
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium_super.actions import Actions

from selenium_super.js import Js
import asyncio
import base64
import json
import codecs

from selenium_super.process_multi_tasks import MultiTask, ProcessMultiTasks
from .auth import Auth
from .enums import By, Until, ElementActions
from .file_utils import FileUtils
from .folder_utils import FolderUtils
from .helpers import get_args_for_elements_by_selector
from .time_utils import TimeUtils
from .nordvpn import NordVPN


class SuperWebDriver(webdriver.Firefox, webdriver.Chrome):
    def __init__(self, config_path, selectors_path=None):

        self.default_firefox_options = None
        self.default_chrome_options = None
        self.default_linux_options = None
        self.firefox_binary_location = None
        self.firefox_executable_path = None
        self.chrome_logger = None
        self.chrome_extensions = None
        self.chrome_profile = None
        self.chrome_executable_path = None
        self.download_folder = None
        self.headless = None
        self.options = None
        self.browser = None
        self.profile = None
        self.vpn_countries = None
        self.use_vpn = None
        self.selectors = {}
        ## load utils
        self.file_utils = FileUtils()
        self.folder_utils = FolderUtils()
        self.time_utils = TimeUtils()
        self.js = Js(self)
        self.auth = Auth(self)
        self.actions = Actions(self)
        self.vpn = NordVPN()

        self.load_browser_config(config_path)
        if self.use_vpn and self.vpn_countries:
            self.vpn.set_countries(self.vpn_countries)
            self.vpn.rotate(google_check=True)

        self.get_web_driver(init=True)

        if selectors_path is not None:
            self.load_selectors_file(selectors_path)

    def load_browser_config(self, file_path):
        config = self.file_utils.load_json_file(file_path=file_path)
        if not config:
            print('Could not load browser config file!')
        else:
            self.browser = config.get('use_browser', None)
            self.options = config.get('options', None)
            self.headless = config.get('headless', None)
            self.download_folder = config.get('download_folder', None)
            self.use_vpn = config.get('use_vpn', False)
            self.vpn_countries = config.get('vpn_countries', [])

            self.chrome_executable_path = config.get('chrome_executable_path', None)
            self.chrome_profile = config.get('chrome_profile', None)
            self.chrome_logger = config.get('chrome_logger', None)
            self.chrome_extensions = config.get('extensions', [])

            self.firefox_executable_path = config.get('firefox_executable_path', None)
            self.firefox_binary_location = config.get('firefox_binary_location', None)

            self.default_linux_options = ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage',
                                          '--profile-directory=Default',
                                          '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.101 Safari/537.36',
                                          '--user-data-dir=~/.config/google-chrome']
            self.default_chrome_options = ['--log-level=3', 'window-size=1920,1080',
                                           '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.101 Safari/537.36']
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
            webdriver.Chrome.__init__(self, options=options)
        elif self.browser == 'chrome':
            print('Starting selenium using Chrome - Windows')
            capabilities = DesiredCapabilities.CHROME.copy()
            options = ChromeOptions()
            for option in self.options or self.default_chrome_options:
                options.add_argument(option)

            for extension in self.chrome_extensions:
                options.add_extension(extension)

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

            webdriver.Chrome.__init__(self,
                                      executable_path=self.chrome_executable_path,
                                      options=options, desired_capabilities=capabilities)
        elif self.browser == 'firefox':
            print('Starting selenium using Chrome - Firefox')
            options = Options()
            options.binary_location = self.firefox_binary_location
            for option in self.options or self.default_firefox_options:
                options.add_argument(option)

            options.profile = []
            webdriver.Firefox.__init__(self,
                                       executable_path=self.firefox_executable_path,
                                       options=options)
        else:
            print('Could not start driver, please fix browser_config.json file')

        self.driver = self

    def validate_element(self, element):
        return element is not None \
               and element.get('by') is not None \
               and element.get('value') is not None

    def load_selectors_file(self, path):
        config = FileUtils().load_json_file(path)
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
                                 wait=0, action: ElementActions = None):

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
                element = self.actions.wait.until(wait_element=(by, value), wait=wait, base_element=search_element, method=Until.present)

                if action and element:
                    action(element)

                if attribute is not None and element is not None:
                    return element.get_attribute(
                        attribute) if filter is None else filter(
                        element.get_attribute(attribute))
                return element

            elif multiple:
                elements = self.actions.wait.until(wait_element=(by, value), wait=wait, base_element=search_element,
                                                  method=Until.presents)

                if attribute is not None and elements is not None:
                    attributes_data = []
                    for element in elements:
                        if action and element:
                            action(element)
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


    def get_multiple_elements_by_selectors(self, selectors, return_when=asyncio.ALL_COMPLETED):
        processor = ProcessMultiTasks()
        data = processor.run(tasks=[
            MultiTask(self.get_elements_by_selector, selector_args[0], args=(selector_args)) for selector_args in
            [get_args_for_elements_by_selector(selector) for selector in selectors]
        ], return_when=return_when)

        return data

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
        if type(result) == int:
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
                    if ("Network.responseReceived" in log["method"] and "json" in log["params"]["response"][
                        "mimeType"]):
                        try:
                            body = self.driver.execute_cdp_cmd('Network.getResponseBody',
                                                               {'requestId': log["params"]["requestId"]})
                            log['body'] = json.loads(body['body'])
                            responses.append(log)
                        except Exception as e:
                            responses.append(log)
                except Exception as e:
                    print(e)

        return responses

    def save_responses(self, file_path=None):
        logs = self.record_responses()
        json_object = {
            'logs': logs,
        }
        if file_path: file = FileUtils().write_json_file(file_path=file_path, write_mode='w+', json_object=json_object,
                                                         stringify=True, log=True)
        return logs

    def click_element_by_xpath(self, xpath):
        self.execute_script(
            """document.evaluate({}, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue?.click()""".format(
                xpath))

    def send_devtools(self, cmd, params={}):
        resource = f"/session/{self.driver.session_id}/chromium/send_command_and_get_result"
        url = self.driver.command_executor._url + resource
        body = json.dumps({'cmd': cmd, 'params': params})
        response = self.driver.command_executor._request('POST', url, body)
        if response.get('status'):
            raise Exception(response.get('value'))
        return response.get('value')

    def get_pdf_from_html(self, print_options={}, save_path=None):
        calculated_print_options = {
            'landscape': False,
            'displayHeaderFooter': False,
            'printBackground': True,
            'preferCSSPageSize': True,
        }
        calculated_print_options.update(print_options)
        result = self.send_devtools("Page.printToPDF", calculated_print_options)
        data = base64.b64decode(result['data'])

        if save_path:
            with open(save_path, 'wb') as file:
                file.write(data)
                file.close()
        return data
