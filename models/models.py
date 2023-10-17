from pydantic import BaseModel

from base.settings import DEFAULT_MAKER_VALUE


class VendorCode(BaseModel):
    data: list[str]


class VC_(BaseModel):
    only_needful_vendor_code: bool


class VC(VC_):
    vendor_code: str
    maker: str = DEFAULT_MAKER_VALUE


class VCPair(VC_):
    vendor_codes: list[str]
    makers: list[str]
