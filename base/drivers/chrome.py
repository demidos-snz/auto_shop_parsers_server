import typing as t

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver


class ChromeDriver(WebDriver):
    def __init__(
            self,
            settings: dict[str, bool],
            options: t.Optional[Options] = None,
            service: t.Optional[Service] = None,
            keep_alive: bool = True,
            chromedriver_path: str = '/usr/bin/chromedriver',
    ):
        self.chromedriver_path: str = chromedriver_path

        options: Options = self.default_options() if options is None else options

        if settings.get('headless'):
            options.add_argument('--headless')

        service: Service = self.default_service if service is None else service

        super().__init__(options=options, service=service, keep_alive=keep_alive)

    @staticmethod
    def default_options() -> Options:
        options: Options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        return options

    @property
    def default_service(self) -> Service:
        return Service(executable_path=self.chromedriver_path)

    def __delete__(self, instance):
        self.close()
