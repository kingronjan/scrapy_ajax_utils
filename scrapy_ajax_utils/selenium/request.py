import logging

import scrapy

logger = logging.getLogger(__name__)


class SeleniumRequest(scrapy.Request):
    """用于selenium的请求类

    需要开启selenium下载中间件

    """
    def __init__(self, url, callback=None,
                 wait_until=None, wait_time=10,
                 script=None, cache_cookies=True,
                 handler=None, **kwargs):

        # 等待条件 参考 Selenium 用法
        self.wait_until = wait_until
        # `wait_until` 的等待时间
        self.wait_time = wait_time

        # js 脚本
        self.script = script

        # 是否缓存 cookies
        self.cache_cookies = cache_cookies

        # webdriver 处理函数
        # 该函数接收三个参数：
        #   1. `driver`，即 `webdriver.Chrome` 的实例
        #   2. `request`，当前 `SeleniumRequest` 的实例
        #   3. `spider`，当前 `Spider` 的实例
        #
        # 该函数将会在以下操作完成后调用：
        #   1. 成功请求目标地址
        #   2. 等待直到期望条件出现（如果有）
        #   3. 执行传入的 js 脚本（如果有）
        self.handler = handler

        super().__init__(url, callback, **kwargs)
