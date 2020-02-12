from selenium import webdriver as _webdriver
from scrapy.utils.project import get_project_settings


def webdriver(driver_name='chrome', executable_path=None,
              headless=True, disable_image=True, user_agent=None, options=None):
    if user_agent is None:
        settings = get_project_settings()
        user_agent = settings['DEFAULT_REQUEST_HEADERS'].get('User-Agent')

    if driver_name == 'firefox':
        if options is None:
            options = _webdriver.FirefoxOptions()
            options.headless = headless
            if disable_image:
                options.set_preference('permissions.default.image', 2)
            options.set_preference('general.useragent.override', user_agent)
        # service_log_path: nul -> close log file, only work for windows.
        return _webdriver.Firefox(options=options, executable_path=executable_path, service_log_path='nul')

    elif driver_name == 'chrome':
        if options is None:
            options = _webdriver.ChromeOptions()
            options.headless = headless
            options.add_argument(f"--user-agent={user_agent}")
            options.add_argument('--disable-gpu')
            if disable_image:
                options.add_experimental_option('prefs', {'profile.default_content_setting_values': {'images': 2}})
            # 规避检测
            options.add_experimental_option('excludeSwitches', ['enable-automation', ])
        return _webdriver.Chrome(options=options, executable_path=executable_path)

    else:
        raise ValueError(f'Not support driver name: {driver_name}')
