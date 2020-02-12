import logging

from scrapy import signals
from scrapy.http import HtmlResponse
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scrapy_ajax_utils.utils import extract_domain_from_url
from scrapy_ajax_utils.selenium.driver import webdriver
from scrapy_ajax_utils.selenium.request import SeleniumRequest

logger = logging.getLogger(__name__)


class SeleniumDownloadMiddleWare(object):
    """For selenium.

    注意：
        缓存cookies需要浏览器User-Agent请求头版本与设置脚本(或Request)中的默认请求头保持一致
        否则某些网站可能会对此做验证 导致cookies无效

    """

    def __init__(self, settings):
        self.settings = settings
        self._driver = None
        self._cached_cookies = {}

    @property
    def driver(self):
        if self._driver is None:
            self._driver = self._get_driver()
        return self._driver

    def _get_driver(self):
        headless = self.settings.getbool('SELENIUM_HEADLESS', True)
        driver_name = self.settings.get('SELENIUM_DRIVER_NAME', 'chrome')
        executable_path = self.settings.get('SELENIUM_DRIVER_PATH')
        return webdriver(driver_name=driver_name,
                         headless=headless,
                         executable_path=executable_path)

    @classmethod
    def from_crawler(cls, crawler):
        dm = cls(crawler.settings)
        crawler.signals.connect(dm.closed, signal=signals.spider_closed)
        return dm

    def process_request(self, request, spider):
        if not isinstance(request, SeleniumRequest):
            return

        if request.cache_cookies:
            for domain in self._cached_cookies:
                if domain in request.url:
                    request.cookies = self._cached_cookies[domain]
                    return

        self.driver.get(request.url)

        # 检查请求是否携带Cookies
        if request.cookies:
            for k, v in request.cookies.items():
                self.driver.add_cookie({'name': k, 'value': v})
            self.driver.get(request.url)

        if request.wait_until:
            condition = EC.presence_of_element_located(request.wait_until)
            WebDriverWait(self.driver, request.wait_time).until(condition)

        # Execute javascript code and save the result to meta.
        if request.script:
            result = self.driver.execute_script(request.script)
            if result is not None:
                request.meta['js_result'] = result

        if request.handler:
            request.handler(self.driver, request, spider)

        for cookie_name, cookie_value in request.cookies.items():
            self.driver.add_cookie(
                {
                    'name': cookie_name,
                    'value': cookie_value
                }
            )
        request.cookies = self.driver.get_cookies()
        request.meta['driver'] = self.driver

        if request.cache_cookies:
            domain = extract_domain_from_url(request.url)
            self._cached_cookies[domain] = request.cookies
        else:
            body = str.encode(self.driver.page_source)
            return HtmlResponse(
                self.driver.current_url,
                body=body,
                encoding='utf-8',
                request=request
            )

    def closed(self):
        if self._driver is not None:
            self._driver.quit()
            logger.debug('Selenium closed')
