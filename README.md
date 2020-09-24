scrapy_ajax_utils
-----------------


utils for ajax in scrapy project. includes selenium, splash.


## Usage
### For selenium
Define the selenium webdriver name, executable path and is headless in `settings.py`
```python
# Default: chrome
# Only support chrome & firefox.
SELENIUM_DRIVER_NAME = 'chrome'

# Default: None
SELENIUM_DRIVER_PATH = None

# Default: True
SELENIUM_HEADLESS = True

# Default: 30
SELENIUM_DRIVER_PAGE_LOAD_TIMEOUT = 30

# Set the min/max concurrent drivers to download page.
# Default: 3
# SELENIUM_MIN_DRIVERS = 5

# Default: 5
# SELENIUM_MAX_DRIVERS = 10
```
Use in your spider:
```python
import scrapy

from scrapy_ajax_utils import selenium_support, SeleniumRequest


@selenium_support
class MySpider(scrapy.Spider):

    start_urls = ['https://www.baidu.com']

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(url)
```

### For splash
The default splash url is http://127.0.0.1:8050, if not right, DO NOT use the `splash_support` function.
```python
import scrapy

from scrapy_ajax_utils import splash_support, SplashRequest


@splash_support
class MySpider(scrapy.Spider):

    start_urls = ['https://www.baidu.com']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url)
```
