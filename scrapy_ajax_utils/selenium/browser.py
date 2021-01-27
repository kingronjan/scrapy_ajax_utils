import os

from scrapy.downloadermiddlewares.cookies import CookiesMiddleware
from scrapy.http import HtmlResponse
from selenium import webdriver

_format_cookie = CookiesMiddleware()._format_cookie
_js_fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stealth.min.js')


class Browser(object):
    """Browser to make drivers"""

    support_driver_map = {
        'firefox': webdriver.Firefox,
        'chrome': webdriver.Chrome
    }

    def __init__(self, driver_name='chrome', executable_path=None, options=None, page_load_time_out=30, **opt_kw):
        assert driver_name in self.support_driver_map, f'{driver_name} not be supported!'
        self.driver_name = driver_name
        self.executable_path = executable_path
        self.page_load_time_out = page_load_time_out
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
        driver.set_page_load_timeout(self.page_load_time_out)
        self.prepare_driver(driver)
        return wrap_driver(driver)

    def prepare_driver(self, driver):
        if isinstance(driver, webdriver.Chrome):
            # Remove `window.navigator.webdriver`.
            with open(_js_fp) as f:
                driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": f.read()
                })


def wrap_driver(driver):
    def current_resp(request):
        # cookies = ('%s=%s; Domain=%s' % (c['name'], c['value'], c.get('domain')) for c in driver.get_cookies())
        cookies = filter(None, (_format_cookie(c, request) for c in driver.get_cookies()))
        headers = {'Set-Cookie': cookies}
        return HtmlResponse(driver.current_url,
                            body=str.encode(driver.page_source),
                            encoding='utf-8',
                            request=request,
                            headers=headers)

    driver.current_resp = current_resp
    return driver


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
