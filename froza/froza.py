import typing as t

from bs4 import BeautifulSoup
from bs4.element import ResultSet
from selenium.webdriver.common.by import By

from base.parser import Parser


class FrozaParser(Parser):
    MASK: str = '\n        '

    def _auth(self, *args, **kwargs):
        pass

    def html_of_result_page(self, vendor_code: str) -> str:
        self._driver.find_element(value='search-field').clear()
        self._driver.find_element(value='search-field').send_keys(vendor_code)
        self.random_sleep()

        self._driver.find_element(value='search_submit_button').click()
        self.random_sleep()

        try:
            self._driver.find_element(by=By.XPATH, value="//td[@data-make_name='SKF']").click()
            self.random_sleep()
        except Exception as exc:
            # fixme
            print('nothing')

        return self._driver.page_source

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


# fixme
# REGISTERED_PARSERS.append(FrozaParser(name='froza', address='https://froza.ru'))


if __name__ == '__main__':
    froza: FrozaParser = FrozaParser(name='froza', address='https://froza.ru')
    froza.run(vendor_codes=[
        'Vkba 5314',
        'Vkba 5549',
        'Vkba 5423',
        'Vkhb 2404 s',
        'Vkt 8956',
        'Vkhb 2401 s',
        'Vkba 5377',
        'Vkpc 7045',
        'Vkpc 7043',
        'Vkhb 2041',
        '47691',
        '47697',
        '35058',
        'Vkmcv 55007',
    ])
