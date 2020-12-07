from scrapy.http import HtmlResponse
from scrapy.downloadermiddlewares.cookies import CookiesMiddleware

from selenium import webdriver

_format_cookie = CookiesMiddleware()._format_cookie


class Browser(object):
    """Browser to make drivers"""

    support_names = {
        'firefox': webdriver.Firefox,
        'chrome': webdriver.Chrome
    }

    def __init__(self, name='chrome', executable_path=None, options=None, page_load_time_out=30, **opt_kw):
        assert name in self.support_names, f'{name} not be supported!'
        self.name = name
        self.executable_path = executable_path
        self.page_load_time_out = page_load_time_out
        if options is not None:
            self.options = options
        else:
            self.options = make_options(self.name, **opt_kw)

    def driver(self):
        kwargs = {'executable_path': self.executable_path, 'options': self.options}
        # Close log file, only works for windows.
        if self.name == 'firefox':
            kwargs['service_log_path'] = 'nul'
        driver = self.support_names[self.name](**kwargs)
        driver.set_page_load_timeout(self.page_load_time_out)
        self.prepare_driver(driver)
        return wrap_driver(driver)

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


def wrap_driver(driver):
    def current_resp(request):
        cookies = filter(None, (_format_cookie(c, request) for c in driver.get_cookies()))
        headers = {'Set-Cookie': cookies}
        return HtmlResponse(driver.current_url,
                            body=str.encode(driver.page_source),
                            encoding='utf-8',
                            request=request,
                            headers=headers)
    driver.current_resp = current_resp
    return driver


def make_options(name, headless=True, disable_image=True, user_agent=None):
    if name == 'chrome':
        options = webdriver.ChromeOptions()
        options.headless = headless
        options.add_argument('--disable-gpu')
        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")
        if disable_image:
            options.add_experimental_option('prefs', {'profile.default_content_setting_values': {'images': 2}})
        options.add_experimental_option('excludeSwitches', ['enable-automation', ])
        return options

    elif name == 'firefox':
        options = webdriver.FirefoxOptions()
        options.headless = headless
        if disable_image:
            options.set_preference('permissions.default.image', 2)
        if user_agent:
            options.set_preference('general.useragent.override', user_agent)
        return options
