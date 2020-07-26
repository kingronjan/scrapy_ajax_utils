from scrapy_ajax_utils.utils import add_settings_to_spider


def selenium_support(spider_cls):
    """Spider class decorator"""
    settings = {
        'DOWNLOADER_MIDDLEWARES': {'scrapy_ajax_utils.selenium.SeleniumDownloaderMiddleware': 600}
    }
    return add_settings_to_spider(spider_cls, settings)


# top import.
from .browser import Browser
from .request import SeleniumRequest
from .middleware import SeleniumDownloaderMiddleware
