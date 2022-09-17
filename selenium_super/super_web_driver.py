import platform
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities    
from selenium import webdriver
from .file_utils import FileUtils

class SuperWebDriver(webdriver.Firefox, webdriver.Chrome):
    def __init__(self, config_path):
        self.load_browser_config(config_path)
        self.driver = self.get_web_driver(init=True)
        
    def load_browser_config(self, file_path):
        config = FileUtils().load_json_file(file_path=file_path)
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