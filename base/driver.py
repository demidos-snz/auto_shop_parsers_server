from selenium.webdriver.firefox.webdriver import WebDriver


class FirefoxDriver(WebDriver):
    def __delete__(self, instance):
        self.close()
