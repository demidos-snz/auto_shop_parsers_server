from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver


class ChromeDriver(WebDriver):
    # fixme /usr/bin/chromedriver
    def __init__(
            self,
            settings: dict[str, bool],
            options: Options = None,
            service: Service = None,
            keep_alive=True,
    ):
        options: Options = self.default_options() if options is None else options

        if settings.get('headless'):
            options.add_argument('--headless')

        service: Service = self.default_service() if service is None else service

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

    @staticmethod
    def default_service() -> Service:
        return Service(executable_path='/usr/bin/chromedriver')

    def __delete__(self, instance):
        self.close()
