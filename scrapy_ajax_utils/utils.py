import copy


def add_settings_to_spider(spider_cls, settings: dict):
    """为 spider 添加设置并返回 spider

    注意：
        如果设置中含有字典，且 spider.custom_settings 有同项设置
        则会更新 （即调用 dict 的 `update` 方法）
        否则会覆盖

    """
    s = copy.deepcopy(settings)
    cus_settings = spider_cls.custom_settings
    if cus_settings:
        for k, v in cus_settings.items():
            if isinstance(v, dict) and k in s:
                s[k].update(v)
            else:
                s[k] = v
    spider_cls.custom_settings = s
    return spider_cls


def extract_domain_from_url(url):
    d = url.split('://')[-1]
    d = d.split('/')[0]
    return d