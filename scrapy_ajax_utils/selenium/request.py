import scrapy


class SeleniumRequest(scrapy.Request):

    def __init__(self,
                 url,
                 callback=None,
                 wait_until=None,
                 wait_time=10,
                 script=None,
                 handler=None,
                 **kwargs):
        """
        :param url: target url to request.
        :param callback: ..
        :param wait_until: see usage in: `WebDriverWait.until`
        :param wait_time:
        :param script: javascript to execute
                    and the result will be save to response.meta
                    which key is 'js_result'

        :param handler: function to handle the driver
                    the function only accept 3 arguments:
                        driver: the instance of `scrapy_ajax_utils.selenium.browser._WebDriver`
                        request: current request
                        spider: current spider

                    and it will execute when:
                        url is got
                        and wait until passed (if exist)
                        and the javascript be executed (if exist)

                    if the function has return value and the value is instance of
                    `scrapy.Request` or `scrapy.Response`, it will be returned in the
                    'process_request' method of downloader middleware immediately

        :param kwargs: keyword arguments to pass to `scrapy.Request`
        """
        self.wait_until = wait_until
        self.wait_time = wait_time
        self.script = script
        self.handler = handler
        super().__init__(url, callback, **kwargs)
