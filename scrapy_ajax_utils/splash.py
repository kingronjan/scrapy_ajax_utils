from scrapy_splash import (
    SplashCookiesMiddleware as _SplashCookiesMiddleware,
    SplashRequest as _SplashRequest,
    SplashJsonResponse
)

from scrapy_ajax_utils.utils import add_settings_to_spider

SPLASH_SETTINGS = {
    'SPLASH_URL': 'http://127.0.0.1:8050/',
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy_ajax_utils.splash.SplashCookiesMiddleware': 700,
        'scrapy_splash.SplashMiddleware': 723,
        'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    },
    'SPIDER_MIDDLEWARES': {
        'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    },
    'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter'
}


class SplashRequest(_SplashRequest):

    def __init__(self, url, *args, lua_script=None, js_script=None, keep_cookies=True, wait=2,
                 **kwargs):
        kwargs.setdefault('dont_send_headers', False)
        _args = kwargs.setdefault('args', {})
        _args['wait'] = wait
        is_exec = kwargs.setdefault('endpoint', 'execute')
        if is_exec == 'execute':
            if lua_script:
                _args['lua_source'] = lua_script
            else:
                _args['lua_source'] = render_lua_script(js_script, keep_cookies)
        super().__init__(url, *args, **kwargs)


class SplashCookiesMiddleware(_SplashCookiesMiddleware):
    """
    传递 cookies 给 request 交由 scrapy 处理
    """

    def process_response(self, request, response, spider):
        if not isinstance(response, SplashJsonResponse):
            return response

        if 'cookies' in response.data:
            request.cookies = response.data['cookies']

        return super().process_response(request, response, spider)


def splash_support(spider_cls):
    """spider 装饰器

    为 spider 添加 splash 相关设置

    """
    return add_settings_to_spider(spider_cls, SPLASH_SETTINGS)


def render_lua_script(js_script=None, keep_cookies=True):
    """生成lua脚本
    js脚本不支持传参，如果需要传参可参考下面的重写lua脚本
    如果有执行结果，返回字段为 js_result
    渲染的结果可能会有多余的空行，但不影响使用

    如果参数均为默认值，则完整脚本如下：
    `
        function main(splash, args)
            splash:init_cookies(splash.args.cookies)
            splash:go({
                splash.args.url,
                headers=splash.args.headers,
                http_method=splash.args.http_method,
                body=splash.args.body,
                })
            assert(splash:wait(args.wait))
            return {
                cookies = splash:get_cookies(),
                html = splash:html(),
            }
            end
    `
    :param js_script: js脚本
    :param keep_cookies: 是否传递cookies
    """
    if js_script:
        js_script = js_script.strip('\n')
        js_script = f"""
        local test = splash:jsfunc([[
        {js_script}
        ]])
        js_result = test()
        """
        js_result = 'js_result = js_result,'
    else:
        js_result = ''
    return f"""
    function main(splash, args)
        {'' if not keep_cookies else 'splash:init_cookies(splash.args.cookies)'}
        splash.images_enabled = false
        splash:go({{
            splash.args.url,
            headers=splash.args.headers,
            http_method=splash.args.http_method,
            body=splash.args.body,
            }})
        assert(splash:wait(args.wait))
        {js_script or ''}
        return {{
            {'' if not keep_cookies else 'cookies = splash:get_cookies(),'}
            html = splash:html(),
            {js_result}
        }}
    end
    """
