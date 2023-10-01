import os
import random
import time
import typing as t
from abc import ABC, abstractmethod
from datetime import datetime
from operator import methodcaller
from random import randint

import pandas as pd
import requests
import validators
from bs4.element import ResultSet
from pydantic.v1.fields import FieldInfo
from requests import Response
from selenium.webdriver.remote.webdriver import WebDriver

from base.model import BaseParserModel
from base.settings import DOWNLOAD_FOLDER, DEFAULT_DRIVER

REGISTERED_PARSERS: list['Parser'] = []


class ValidationError(Exception):
    pass


class ParserValidator(ABC):
    def __init__(self, parser: 'Parser'):
        self.parser: 'Parser' = parser

    def validate_name(self) -> str:
        name: str = self.parser.name
        len_name: int = self.parser.LENGTH_NAME

        if not isinstance(self.parser.name, str):
            name: str = str(name)

        if len(name) > len_name:
            name: str = f'{name[:len_name]}...'

        return name

    def validate_address(self) -> str:
        address: str = self.parser.address

        if validators.url(address):
            return address
        else:
            # fixme logging
            raise ValidationError(f'Address: "{address}" is not valid!')

    def get_result_data(self, data: pd.DataFrame) -> pd.DataFrame:
        model: t.Type[BaseParserModel] = self.parser.model
        result: list[dict[str, t.Any]] = list()

        for _, row in data.iterrows():

            data_for_df, data_for_model = self.__get_data_for_validation(model=model, series=row)

            if self.__validate_data_with_model(data_for_model=data_for_model, model=model):
                result.append(data_for_df)

        return pd.DataFrame(data=result)

    def __get_data_for_validation(self, model: t.Type[BaseParserModel], series: pd.Series) \
            -> tuple[dict[str, t.Any], dict[str, t.Any]]:

        data_for_model: dict[str, t.Any] = dict()
        data_for_df: dict[str, t.Any] = dict()

        for field_name, field_param in model.__pydantic_fields__.items():

            if field_param.description in series:
                validated_data: t.Any = self.__get_validated_data_after_prepared_methods(
                    field_name=field_name,
                    field_param=field_param,
                    series=series,
                )
                data_for_model[field_name]: t.Any = validated_data
                data_for_df[field_param.description]: t.Any = validated_data

            else:
                # fixme error!
                print('error __get_data_for_validation')

        return data_for_df, data_for_model

    def __get_validated_data_after_prepared_methods(
            self,
            field_name: str,
            field_param: FieldInfo,
            series: pd.Series,
    ) -> t.Optional[t.Any]:

        validated_data = None
        prepare_method: t.Optional[t.Callable] = getattr(self, f'validate_{field_name}', None)

        if prepare_method:
            try:
                validated_data: t.Any = prepare_method(data=series[field_param.description])
            except Exception as exc:
                # fixme logging
                print('__get_validated_data_after_prepared_methods', exc)

        else:
            # fixme warning attribute not validate
            validated_data: t.Any = series[field_param.description]

        return validated_data

    def __validate_data_with_model(self, data_for_model: dict[str, t.Any], model: t.Type[BaseParserModel]) -> bool:
        try:
            if len(data_for_model) == len(self.parser.descriptions_keys_of_model):
                model(**data_for_model)
                return True
            else:
                # fixme logging
                print('__validate_data_with_model')
                return False
        except Exception as exc:
            # fixme logging
            print(exc)
            return False

    @abstractmethod
    def validate_maker(self, data: t.Any) -> str:
        raise NotImplementedError

    @abstractmethod
    def validate_vendor_code(self, data: t.Any) -> str:
        raise NotImplementedError

    @abstractmethod
    def validate_description(self, data: t.Any) -> t.Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def validate_availability(self, data: t.Any) -> int:
        raise NotImplementedError

    @abstractmethod
    def validate_price(self, data: t.Any) -> float | int:
        raise NotImplementedError

    @abstractmethod
    def validate_delivery_time(self, data: t.Any) -> int:
        raise NotImplementedError

    @abstractmethod
    def validate_direction(self, data: t.Any) -> str:
        raise NotImplementedError

    @staticmethod
    def _convert_str_to_int(data: str) -> int:
        try:
            return int(data)
        except Exception as exc:
            # fixme logging warning bad convert str to int
            print(exc, data)
            return 0

    @staticmethod
    def _convert_str_to_float(data: str) -> float:
        try:
            return float(data)
        except Exception as exc:
            # fixme logging warning bad convert str to float
            print(exc, data)
            return 0


class BaseParserValidator(ParserValidator):
    def validate_maker(self, data: str) -> str:
        return data.strip()

    def validate_vendor_code(self, data: str) -> str:
        return data.strip()

    def validate_description(self, data: str) -> t.Optional[str]:
        return data.strip()

    def validate_availability(self, data: str) -> int:
        if isinstance(data, int):
            return data
        elif isinstance(data, str):
            res: list[str] = [i for i in data if i.isdigit()]
            return self._convert_str_to_int(data=''.join(res))
        else:
            # fixme logging warning unknown type
            print('validate_availability', data)
            return 0

    def validate_price(self, data: str) -> float | int:
        if isinstance(data, int) or isinstance(data, float):
            return data
        elif isinstance(data, str):
            data: str = data.replace(',', '.')
            data: str = data.replace('р.', '')
            res: list[str] = [i for i in data if i.isdigit() or i == '.']
            return self._convert_str_to_float(data=''.join(res))
        else:
            # fixme logging warning unknown type
            print('validate_price', data)
            return 0

    def validate_delivery_time(self, data: str) -> int:
        if isinstance(data, int):
            return data
        elif isinstance(data, str):
            res: int = self.__get_delivery_time(data=data)

            if res == 0:
                return self.__get_delivery_time(data=data, sym=')')
            elif res == -1:
                return 0
            else:
                return res
        else:
            # fixme logging warning unknown type
            print('validate_delivery_time', data)
            return 0

    def __get_delivery_time(self, data: str, sym: str = '(') -> int:
        ind: int = data.find(sym)

        if ind == -1:
            # fixme logging warning unknown format string delivery_time
            print('__get_delivery_time', data)
            return -1
        else:
            res: list[str] = [i for i in data[:ind] if i.isdigit()]
            return self._convert_str_to_int(data=''.join(res))

    def validate_direction(self, data: str) -> str:
        return data.strip()


class ParserWriter(ABC):
    FILE_EXTENSION: str = 'txt'

    def __init__(self, data: pd.DataFrame, source: str):
        self.data: pd.DataFrame = data
        self.source: str = source

    @abstractmethod
    def write(self, *args, **kwargs) -> t.Optional[str]:
        raise NotImplementedError

    @property
    def __filename(self) -> str:
        return f'{datetime.now()}.{self.FILE_EXTENSION}'

    @property
    def filepath(self) -> str:
        return os.path.join(DOWNLOAD_FOLDER, self.__filename)

    def _add_source_column_to_data(self):
        self.data['Источник']: pd.Series = self.source


class ExcelParserWriter(ParserWriter):
    FILE_EXTENSION: str = 'xlsx'

    def write(self, add_source: bool = True) -> str:
        if add_source:
            self._add_source_column_to_data()

        filepath: str = self.filepath
        self.data.to_excel(excel_writer=filepath, index=False)

        return filepath


class Parser(ABC):
    LENGTH_NAME: int = 20
    TIMEOUT: int = 5
    SECONDS_SLEEP_MIN: int = 5
    SECONDS_SLEEP_MAX: int = 10

    def __init__(
            self,
            name: str,
            address: str,
            validator: ParserValidator = None,
            writers_handlers: list[ParserWriter] = None,
            driver: WebDriver = DEFAULT_DRIVER,
            model: t.Type[BaseParserModel] = BaseParserModel,
    ):
        self.name: str = name
        self.address: str = address
        self._driver: WebDriver = driver
        self.model: t.Type[BaseParserModel] = model

        self.__is_active: bool = True
        self.__add_to_registered_parsers()

        self.__validator: t.Optional[ParserValidator] = validator
        self.__validate_params()

        self.__writers_handlers: t.Optional[list[ParserWriter]] = writers_handlers

        self.__init_driver()

        self.descriptions_keys_of_model: list[str] = [
            field_param.description for field_param in self.model.__pydantic_fields__.values()
        ]
        #     fixme check HEADER_EXCEL in self.keys_model exclude(Запрашиваемый артикул, Источник)

        self._html_of_result_page: str = ''
        self._resultsets: tuple[ResultSet, ...] = tuple()
        self._df: pd.DataFrame = pd.DataFrame()

    def __validate_params(self):
        for name in self.__dict__.keys():
            if name.startswith(f'_{Parser.__name__}'):
                continue

            prepare_method: t.Optional[t.Callable] = getattr(self.validator, f'validate_{name}', None)

            if prepare_method:
                self.__dict__[name] = prepare_method()
            else:
                # fixme warning attribute not validate
                pass

    def __init_driver(self):
        if self.ping():
            self._driver.get(url=self.address)
        else:
            # fixme
            exit()

    @property
    def validator(self) -> ParserValidator:
        return BaseParserValidator(self) if self.__validator is None else self.__validator

    @property
    def writers_handlers(self) -> list[t.Type[ParserWriter]]:
        return [ExcelParserWriter] if self.__writers_handlers is None else self.__writers_handlers

    def ping(self) -> bool:
        try:
            response: Response = requests.get(
                url=self.address,
                headers=random.choice(self.__headers),
                timeout=self.TIMEOUT,
                proxies=self.__proxies,
            )
        except Exception as e:
            print('ping', e)
            # fixme logging
            return False

        return response.ok

    @property
    def __headers(self) -> list[dict[str, str]]:
        # fixme
        return [
            {},
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            },
            {
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0',
            },
        ]

    @property
    def __proxies(self) -> dict[str, str]:
        # fixme
        return {}

    @property
    def is_active(self) -> bool:
        return self.__is_active

    @abstractmethod
    def _auth(self, *args, **kwargs) -> t.Optional[t.Any]:
        raise NotImplementedError

    @abstractmethod
    def html_of_result_page(self, *args, **kwargs) -> str:
        raise NotImplementedError

    @abstractmethod
    def _parse_data(self, *args, **kwargs) -> tuple[ResultSet, ...]:
        raise NotImplementedError

    def _get_data_vendor_code(self) -> list[list[t.Any]]:
        self.__check_len_get_data_params()

        data: list[list[str]] = list()

        for f, r in zip(self._funcs, self._resultsets):
            mc: methodcaller = methodcaller(f.__name__, r)
            data.append(mc(self))

        return data

    # fixme
    def __check_len_get_data_params(self):
        if len(self._funcs) == len(self._resultsets) == len(self.descriptions_keys_of_model):
            print('ok - __check_len_get_data_params')
        else:
            print('bad', len(self._funcs), len(self._resultsets))

    @staticmethod
    def sleep(seconds: int = SECONDS_SLEEP_MIN):
        time.sleep(seconds)

    def random_sleep(self):
        time.sleep(randint(a=self.SECONDS_SLEEP_MIN, b=self.SECONDS_SLEEP_MAX))

    # fixme name
    @property
    @abstractmethod
    def _funcs(self) -> tuple[t.Callable, ...]:
        raise NotImplementedError

    # fixme
    def __check_len_resultsets_from_parse_data(self):
        set_len_resultsets: set[int] = set(map(len, self._resultsets))

        if len(set_len_resultsets) == 1 and 0 not in set_len_resultsets:
            print('ok - __check_len_resultsets_from_parse_data')
        else:
            print('bad', set_len_resultsets)

    def run(self, vendor_codes: list[str], only_needful: bool = False) -> list[str]:
        self._df: pd.DataFrame = pd.DataFrame()
        random.shuffle(vendor_codes)

        for vendor_code in vendor_codes:
            vendor_code_data: list[list[t.Any]] = self.__run(vendor_code=vendor_code)

            df: pd.DataFrame = pd.DataFrame.from_dict(data=dict(zip(self.descriptions_keys_of_model, vendor_code_data)))

            validated_data: pd.DataFrame = self.validator.get_result_data(data=df)

            if validated_data.empty:
                continue
            else:
                validated_data['Искомый артикул']: pd.Series = vendor_code

            if only_needful:
                # fixme temp
                vendor_code: str = vendor_code.replace(' ', '').upper()
                validated_data: pd.DataFrame = validated_data[validated_data['Артикул'] == vendor_code]

            self._df: pd.DataFrame = pd.concat(objs=[validated_data, self._df])

        return self._write(data=self._df)

        # self._driver.close()

    def _write(self, data: pd.DataFrame) -> list[str]:
        filenames: list[str] = []

        if not data.empty:
            self.__write(data=data, filenames=filenames)

        return filenames

    def __write(self, data: pd.DataFrame, filenames: list[str]):
        for writer_class in self.writers_handlers:
            writer: ParserWriter = writer_class(data=data, source=self.address)
            # fixme
            filename: str = writer.write()

            if filename:
                filenames.append(filename)

    def __run(self, vendor_code: str) -> list[list[t.Any]]:
        self._html_of_result_page: str = self.html_of_result_page(vendor_code=vendor_code)

        self._resultsets: tuple[ResultSet, ...] = self._parse_data()
        self.__check_len_resultsets_from_parse_data()

        data_vendor_code: list[list[t.Any]] = self._get_data_vendor_code()

        return data_vendor_code

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name!r}, {self.address!r})'

    # fixme
    def __add_to_registered_parsers(self):
        pass
        # REGISTERED_PARSERS.append(self)
