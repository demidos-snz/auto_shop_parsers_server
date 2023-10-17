import typing as t

from bs4 import BeautifulSoup
from bs4.element import ResultSet
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from base.parser import Parser
from base.settings import DEFAULT_MAKER_VALUE


class FrozaParser(Parser):
    MASK: str = '\n        '

    def _auth(self, *args, **kwargs):
        pass

    def html_of_result_page(self, vendor_code: str, maker: str) -> str:
        page_source: str = ''

        self._driver.find_element(value='search-field').clear()
        self._driver.find_element(value='search-field').send_keys(vendor_code)
        self.random_sleep()

        self._driver.find_element(value='search_submit_button').click()
        self.random_sleep()

        try:
            if maker == DEFAULT_MAKER_VALUE:
                page_source: str = self.__get_all_pages_source() or self._driver.page_source

            else:
                webelements_result_table: list[WebElement] = self._driver.find_elements(
                    by=By.CLASS_NAME,
                    value='speed_search',
                )
                elements_table: list[str] = [el.text.lower() for el in webelements_result_table]

                if maker in elements_table:
                    maker_web: WebElement = webelements_result_table[elements_table.index(maker)]
                    self._driver.find_element(
                        by=By.XPATH,
                        value=f"//td[@data-make_name='{maker_web.text}']",
                    ).click()
                    self.random_sleep()

                    page_source: str = self._driver.page_source

                else:
                    page_source: str = self.__get_all_pages_source() or self._driver.page_source

        except Exception as exc:
            # fixme
            print('nothing')

        return page_source

    def __get_all_pages_source(self) -> str:
        all_pages_source: list[str] = []

        for row in self._driver.find_elements(
                by=By.CLASS_NAME,
                value='row_detail_number',
        ):
            row.click()
            self.random_sleep()

            all_pages_source.append(self._driver.page_source)

            self._driver.back()
            self.random_sleep()

        return ''.join(all_pages_source)

    def _parse_data(self) -> tuple[ResultSet, ...]:
        soup: BeautifulSoup = BeautifulSoup(markup=self._html_of_result_page, features='html.parser')

        def producers_without_header(td):
            return '\n' in td.text

        makers: ResultSet = soup.find_all(producers_without_header, attrs={'class': 'proizvod'})
        vendor_codes: ResultSet = soup.find_all(name='td', attrs={'class': 'left_cont articles'})
        descriptions: ResultSet = soup.find_all(name='td', attrs={'class': 'left_cont opisanie'})
        quantity_available_for_order: ResultSet = soup.find_all(name='td', attrs={'class': 'nalichie'})
        prices: ResultSet = soup.find_all(name='td', attrs={'class': 'stoimost'})
        delivery_times: ResultSet = soup.find_all(name='td', attrs={'class': 'srok'})
        directions: ResultSet = soup.find_all(name='td', attrs={'class': 'napravlen'})

        return (
            makers, vendor_codes, descriptions,
            quantity_available_for_order, prices, delivery_times,
            directions,
        )

    @property
    def _funcs(self) -> tuple[t.Callable, ...]:
        return (
            self._get_result_from_resultset,
            self._get_result_from_vendor_code_resultset,
            self._get_result_from_resultset,
            self._get_result_from_resultset,
            self._get_result_from_resultset,
            self._get_result_from_resultset,
            self._get_result_from_resultset,
        )

    def _get_result_from_resultset(self, resultset: ResultSet) -> list[str]:
        res: list[str] = list()

        for i in range(len(resultset)):
            text: str = resultset[i - 1].text.strip(self.MASK) if resultset[i].text == '\n' \
                else resultset[i].text.strip(self.MASK)
            res.append(text)

        return res

    def _get_result_from_vendor_code_resultset(self, resultset: ResultSet) -> list[str]:
        res: list[str] = list()

        for i in range(len(resultset)):
            text: str = resultset[i - 1].contents[3].text.strip(self.MASK) if len(resultset[i].contents) == 1 \
                else resultset[i].contents[3].text.strip(self.MASK)
            res.append(text)

        return res
