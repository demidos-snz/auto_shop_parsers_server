from pydantic import BaseModel


class VendorCode(BaseModel):
    data: list[str]


class VC_(BaseModel):
    only_needful_vendor_code: bool


class VC(VC_):
    vendor_code: str
