import copy


def add_settings_to_spider(spider_cls, settings: dict):
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
