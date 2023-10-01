import typing as t

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import WebDriver


class FirefoxDriver(WebDriver):
    def __init__(self, settings: dict[str, bool], options: Options = None, service: Service = None, keep_alive=True):
        headless_driver: t.Optional[bool] = settings.get('headless')
        if headless_driver is not None:
            options: Options = Options() if options is None else options
            options.headless = headless_driver

        super().__init__(options=options, service=service, keep_alive=keep_alive)

    def __delete__(self, instance):
        self.close()
