from selenium import webdriver
from scrapy.utils.project import get_project_settings


class Webdriver(object):
    """Selenium drivers"""
    DRIVER_CLS = {
        'firefox': webdriver.Firefox,
        'chrome': webdriver.Chrome
    }

    def __init__(self, driver_name='chrome', executable_path=None,
                 headless=True, disable_image=True, user_agent=None, options=None):
        self.driver_name = driver_name
        self.headless = headless
        self.disable_image = disable_image
        if user_agent is None:
            settings = get_project_settings()
            self.user_agent = settings['DEFAULT_REQUEST_HEADERS'].get('User-Agent')
        else:
           self.user_agent = user_agent

        cls = self.DRIVER_CLS[self.driver_name]
        self.driver = cls(**self._init_kwargs(executable_path, options))

    def __enter__(self):
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def quit(self):
        self.driver.quit()

    def _init_kwargs(self, executable_path, options):
        if self.driver_name == 'firefox':
            if options is None:
                options = webdriver.FirefoxOptions()
                options.headless = self.headless
                if self.disable_image:
                    options.set_preference('permissions.default.image', 2)
                options.set_preference('general.useragent.override', self.user_agent)
            return {
                'executable_path': executable_path,
                'service_log_path': 'nul',  # Close log file, only work for windows.
                'options': options
            }

        elif self.driver_name == 'chrome':
            if options is None:
                options = webdriver.ChromeOptions()
                options.headless = self.headless
                options.add_argument(f"--user-agent={self.user_agent}")
                options.add_argument('--disable-gpu')
                if self.disable_image:
                    options.add_experimental_option('prefs', {'profile.default_content_setting_values': {'images': 2}})
                # 规避检测
                options.add_experimental_option('excludeSwitches', ['enable-automation', ])
            return {
                'executable_path': executable_path,
                'options': options
            }

        else:
            return {
                'options': options,
                'executable_path': executable_path
            }
