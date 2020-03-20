from selenium import webdriver


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
        self.user_agent = user_agent
        self.executable_path = executable_path
        self._options = options

    def driver(self):
        if self.driver_name not in self.DRIVER_CLS:
            raise ValueError(f'not support driver: {self.driver_name}')

        driver_cls = self.DRIVER_CLS[self.driver_name]
        kwargs = {'executable_path': self.executable_path, 'options': self.options()}

        if self.driver_name == 'firefox':
            # Close log file, only work for windows.
            kwargs['service_log_path'] = 'nul'

        driver = driver_cls(**kwargs)
        self._prepare(driver)
        return driver

    def options(self):
        if self._options is not None:
            return self._options
        if self.driver_name == 'firefox':
            return self._firefox_options()
        elif self.driver_name == 'chrome':
            return self._chrome_options()

    def _chrome_options(self):
        options = webdriver.ChromeOptions()
        options.headless = self.headless
        options.add_argument('--disable-gpu')
        if self.user_agent:
            options.add_argument(f"--user-agent={self.user_agent}")
        if self.disable_image:
            options.add_experimental_option('prefs', {'profile.default_content_setting_values': {'images': 2}})
        # 规避检测
        options.add_experimental_option('excludeSwitches', ['enable-automation', ])

    def _firefox_options(self):
        options = webdriver.FirefoxOptions()
        options.headless = self.headless
        if self.disable_image:
            options.set_preference('permissions.default.image', 2)
        if self.user_agent:
            options.set_preference('general.useragent.override', self.user_agent)

    def _prepare(self, driver):
        if isinstance(driver, webdriver.Chrome):
            # Remove `window.navigator.webdriver`.
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                })
              """
            })
