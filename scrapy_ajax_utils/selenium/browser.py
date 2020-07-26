from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver


class Browser(object):
    """Browser to make drivers"""

    support_driver_map = {
        'firefox': webdriver.Firefox,
        'chrome': webdriver.Chrome
    }

    def __init__(self, driver_name='chrome', executable_path=None, options=None, **opt_kw):
        assert driver_name in self.support_driver_map, f'{driver_name} not be supported!'
        self.driver_name = driver_name
        self.executable_path = executable_path
        if options is not None:
            self.options = options
        else:
            self.options = make_options(self.driver_name, **opt_kw)

    def driver(self):
        kwargs = {'executable_path': self.executable_path, 'options': self.options}
        # Close log file, only works for windows.
        if self.driver_name == 'firefox':
            kwargs['service_log_path'] = 'nul'
        driver = self.support_driver_map[self.driver_name](**kwargs)
        self.prepare_driver(driver)
        return _WebDriver(driver)

    def prepare_driver(self, driver):
        if isinstance(driver, webdriver.Chrome):
            # Remove `window.navigator.webdriver`.
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                })
              """
            })


class _WebDriver(object):
    """As agent of the webdriver.WebDriver"""
    def __init__(self, driver: RemoteWebDriver):
        self._driver = driver
        self._is_idle = False

    def __getattr__(self, item):
        return getattr(self._driver, item)

    def current_response(self, request):
        return HtmlResponse(self.current_url,
                            body=str.encode(self.page_source),
                            encoding='utf-8',
                            request=request)


def make_options(driver_name, headless=True, disable_image=True, user_agent=None):
    if driver_name == 'chrome':
        options = webdriver.ChromeOptions()
        options.headless = headless
        options.add_argument('--disable-gpu')
        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")
        if disable_image:
            options.add_experimental_option('prefs', {'profile.default_content_setting_values': {'images': 2}})
        options.add_experimental_option('excludeSwitches', ['enable-automation', ])
        return options

    elif driver_name == 'firefox':
        options = webdriver.FirefoxOptions()
        options.headless = headless
        if disable_image:
            options.set_preference('permissions.default.image', 2)
        if user_agent:
            options.set_preference('general.useragent.override', user_agent)
        return options
