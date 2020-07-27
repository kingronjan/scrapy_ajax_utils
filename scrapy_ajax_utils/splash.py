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
        splash_args = kwargs.setdefault('args', {})
        splash_args['wait'] = wait
        endpoint = kwargs.setdefault('endpoint', 'execute')
        if endpoint == 'execute':
            if lua_script:
                splash_args['lua_source'] = lua_script
            else:
                splash_args['lua_source'] = render_lua_script(js_script, keep_cookies)
        super().__init__(url, *args, **kwargs)


class SplashCookiesMiddleware(_SplashCookiesMiddleware):

    def process_response(self, request, response, spider):
        if not isinstance(response, SplashJsonResponse):
            return response

        if 'cookies' in response.data:
            request.cookies = response.data['cookies']

        return super().process_response(request, response, spider)


def splash_support(spider_cls):
    """Spider class decorator to add splash settings to spider"""
    return add_settings_to_spider(spider_cls, SPLASH_SETTINGS)


def render_lua_script(js_script=None, keep_cookies=True):
    """make lua script and return

    :param js_script: javascript to execute
                the result will save to 'js_result'
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
