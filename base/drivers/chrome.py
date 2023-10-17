from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver


class ChromeDriver(WebDriver):
    def __init__(self, settings: dict[str, bool], options: Options = None, service: Service = None, keep_alive=True):
        if settings.get('headless'):
            options: Options = Options() if options is None else options
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--remote-debugging-port=9222')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')

            service: Service = Service(executable_path='./chromedriver')

        super().__init__(options=options, service=service, keep_alive=keep_alive)

    def __delete__(self, instance):
        self.close()
