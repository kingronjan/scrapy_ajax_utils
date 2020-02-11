import os.path

from selenium import webdriver
from scrapy.utils.project import get_project_settings

driver_path = os.path.join(os.path.dirname(__file__), '_drivers')


class Webdriver(object):
    """Selenium drivers"""
    KWARGS = {
        'firefox': {
            'executable_path': os.path.join(driver_path, 'geckodriver.exe'),
            'service_log_path': 'nul',  # Close log file, only work for windows.
        },
        'chrome': {
            'executable_path': os.path.join(driver_path, 'chromedriver.exe'),
        }
    }
    DRIVER_CLS = {
        'firefox': webdriver.Firefox,
        'chrome': webdriver.Chrome
    }

    def __init__(self, driver_name='firefox', headless=True, disable_image=True, user_agent=None):
        self.driver_name = driver_name
        self.headless = headless
        self.disable_image = disable_image
        if user_agent is None:
            settings = get_project_settings()
            self.user_agent = settings['DEFAULT_REQUEST_HEADERS'].get('User-Agent')
        else:
           self.user_agent = user_agent

        kw = self.KWARGS[self.driver_name]
        cls = self.DRIVER_CLS[self.driver_name]
        self.driver = cls(options=self._options(), **kw)

    def __enter__(self):
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def quit(self):
        self.driver.quit()

    def _options(self):
        if self.driver_name == 'firefox':
            opts = webdriver.FirefoxOptions()
            opts.headless = self.headless
            if self.disable_image:
                opts.set_preference('permissions.default.image', 2)
            opts.set_preference('general.useragent.override', self.user_agent)

        elif self.driver_name == 'chrome':
            opts = webdriver.ChromeOptions()
            opts.headless = self.headless
            opts.add_argument(f"--user-agent={self.user_agent}")
            opts.add_argument('--disable-gpu')
            if self.disable_image:
                opts.add_experimental_option('prefs', {'profile.default_content_setting_values': {'images': 2}})
            # 规避检测
            opts.add_experimental_option('excludeSwitches', ['enable-automation', ])

        else:
            opts = None

        return opts
