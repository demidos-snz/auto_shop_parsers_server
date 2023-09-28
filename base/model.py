import typing as t

from pydantic import Field
from pydantic.dataclasses import dataclass

# fixme delete
data = {
    'maker': 'SKF',
    'vendor_code': 'VKBA5314',
    'description': 'Комплект подшипника ступицы колеса',
    'availability': '100',
    'price': '16635.07',
    'delivery_time': '24',
    'direction': 'MSC AFL33',
    'source': 'https://froza.ru',
}


@dataclass
class BaseParserModel:
    maker: str = Field(
        default='',
        description='Производитель',
        max_length=31,
    )
    vendor_code: str = Field(
        default='',
        description='Артикул',
        max_length=31,
    )
    description: t.Optional[str] = Field(
        default=None,
        description='Описание',
        max_length=127,
    )
    availability: int = Field(
        default=0,
        description='Наличие',
    )
    price: float = Field(
        default=0,
        description='Цена',
    )
    delivery_time: int = Field(
        default=0,
        description='Срок доставки в днях',
    )
    direction: str = Field(
        default='',
        max_length=31,
        description='Направление',
    )
    # fixme
    # searched_vendor_code: str = Field(
    #     description='Искомый артикул',
    #     max_length=31,
    # )


#     fixme
class VendorCode:
    pass


#     fixme
# BaseParserModel(**data)
# print(BaseParserModel.__pydantic_fields__)
