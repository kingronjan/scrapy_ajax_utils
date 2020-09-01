import logging
import threading

from scrapy import signals
from scrapy.http import Request, Response
from selenium.webdriver.support.ui import WebDriverWait
from twisted.internet import threads, reactor
from twisted.python.threadpool import ThreadPool

from scrapy_ajax_utils.selenium.browser import Browser
from scrapy_ajax_utils.selenium.request import SeleniumRequest

logger = logging.getLogger(__name__)


class SeleniumDownloaderMiddleware(object):

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        min_drivers = settings.get('SELENIUM_MIN_DRIVERS', 3)
        max_drivers = settings.get('SELENIUM_MAX_DRIVERS', 5)
        browser = _make_browser_from_settings(settings)
        dm = cls(browser, min_drivers, max_drivers)
        crawler.signals.connect(dm.spider_closed, signal=signals.spider_closed)
        return dm

    def __init__(self, browser, min_drivers, max_drivers):
        self._browser = browser
        self._drivers = set()
        self._data = threading.local()
        self._threadpool = ThreadPool(min_drivers, max_drivers)

    def process_request(self, request, spider):
        if not isinstance(request, SeleniumRequest):
            return

        if not self._threadpool.started:
            self._threadpool.start()

        return threads.deferToThreadPool(
            reactor, self._threadpool, self.download_by_driver, request, spider
        )

    def download_by_driver(self, request, spider):
        driver = self.get_driver()
        driver.get(request.url)

        # XXX: Check cookies.
        # if request.cookies:
        #     if isinstance(request.cookies, list):
        #         for cookie in request.cookies:
        #             driver.add_cookie(cookie)
        #     else:
        #         for k, v in request.cookies.items():
        #             driver.add_cookie({'name': k, 'value': v})
        #     driver.get(request.url)

        if request.wait_until:
            WebDriverWait(driver, request.wait_time).until(request.wait_until)

        # Execute javascript code and put the result to meta.
        if request.script:
            request.meta['js_result'] = driver.execute_script(request.script)

        if request.handler:
            result = request.handler(driver, request, spider)
            if isinstance(result, (Request, Response)):
                return result

        return driver.current_response(request)

    def get_driver(self):
        try:
            driver = self._data.driver
        except AttributeError:
            driver = self._browser.driver()
            self._drivers.add(driver)
            self._data.driver = driver
        return driver

    def spider_closed(self):
        for driver in self._drivers:
            driver.quit()
        logger.debug('all webdriver closed.')
        self._threadpool.stop()


def _make_browser_from_settings(settings):
    headless = settings.getbool('SELENIUM_HEADLESS', True)
    disable_image = settings.get('SELENIUM_DISABLE_IMAGE', True)
    driver_name = settings.get('SELENIUM_DRIVER_NAME', 'chrome')
    executable_path = settings.get('SELENIUM_DRIVER_PATH')
    user_agent = settings.get('USER_AGENT')
    page_load_time_out = settings.get('SELENIUM_DRIVER_PAGE_LOAD_TIMEOUT', 30)
    return Browser(headless=headless,
                   disable_image=disable_image,
                   driver_name=driver_name,
                   executable_path=executable_path,
                   user_agent=user_agent,
                   page_load_time_out=page_load_time_out)
