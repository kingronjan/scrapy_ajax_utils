"""
selenium.
"""
def selenium_support(spider_cls):
    """spider 装饰器

    添加 selenium 相关设置
    使得在 spider 中可使用 SeleniumRequest

    """
    from scrapy_ajax_utils.utils import add_settings_to_spider

    settings = {
        'DOWNLOADER_MIDDLEWARES': {'scrapy_ajax_utils.selenium.SeleniumNoBlockingDownloadMiddleWare': 600}
    }
    return add_settings_to_spider(spider_cls, settings)


# 便于其它文件导入
from .browser import Browser
from .request import SeleniumRequest
from .middleware import SeleniumDownloadMiddleWare, SeleniumNoBlockingDownloadMiddleWare
