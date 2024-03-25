import uvicorn
from fastapi import FastAPI, status

from base.parser import REGISTERED_PARSERS
from froza.froza import FrozaParser
from models.models import VendorCode, VC, VC_, VCPair
from settings import DEFAULT_MAKER_VALUE

app: FastAPI = FastAPI()

VENDOR_CODES: list[str] = [
    '10PK1136HD',
    '10PK1475HD',
    '10PK1547HD',
    '10PK1863HD',
    '10PK2475HD',
    '12PK1835HD',
    '12PK2140HD',
    '13A1500HD',
    '13A1925HD',
    '13A2100HD',
    '5PK1025HD',
    '7PK1535HD',
    '8PK1035HD',
    '8PK1190HD',
    '8PK1275HD',
    '8PK1367HD',
    '8PK1375HD',
    '8PK1435HD',
    '8PK1525HD',
    '8PK1550HD',
    '8PK1575HD',
    '8PK1612HD',
    '8PK1685HD',
    '8PK1688HD',
    '8PK1725HD',
    '8PK1790HD',
    '8PK1855HD',
    '8PK1920HD',
    '8PK1940HD',
    '8PK2020HD',
    '8PK2043HD',
    '8PK2085HD',
    '8PK2130HD',
    '8PK2355HD',
    '8PK880HD',
    '9PK1358HD',
    '9PK1380HD',
    '9PK1424HD',
    '9PK1920HD',
    '9PK2080HD',
    '9PK2140HD',
    '9PK2338HD',
    '9PK2642HD',
    '47691',
    '47697',
    '26762',
    '29528',
    '30008',
    '32500',
    '6307 N',
    'VKBA 1319',
    'VKBA 3551',
    'VKBA 5314',
    'VKBA 5377',
    'VKBA 5408',
    'VKBA 5409',
    'VKBA 5415',
    'VKBA 5423',
    'VKBA 5424',
    'VKBA 5425',
    'VKBA 5429',
    'VKBA 5431',
    'VKBA 5437',
    'VKBA 5448',
    'VKBA 5453',
    'VKBA 5455',
    'VKBA 5456',
    'VKBA 5460',
    'VKBA 5552',
    'VKBA 7005',
    'VKBC 20051',
    'VKDCV 01006',
    'VKDCV 01021',
    'VKDCV 01026',
    'VKDCV 01036',
    'VKDCV 06001',
    'VKDCV 06002',
    'VKDCV 09003',
    'VKDCV 09011',
    'VKDCV 09014',
    'VKDCV 10001',
    'VKDCV 10002',
    'VKDCV 10007',
    'VKHB 2003',
    'VKHB 2007',
    'VKHB 2024',
    'VKHB 2036',
    'VKHB 2040',
    'VKHB 2041',
    'VKHB 2072',
    'VKHB 2082',
    'VKHB 2145',
    'VKHB 2146',
    'VKHB 2157',
    'VKHB 2161',
    'VKHB 2162 ',
    'VKHB 2163',
    'VKHB 2165',
    'VKHB 2170',
    'VKHB 2182',
    'VKHB 2216',
    'VKHB 2225',
    'VKHB 2240',
    'VKHB 2279',
    'VKHB 2283',
    'VKHB 2315',
    'VKHB 2334',
    'VKHB 2401 S',
    'VKHB 2403 S',
    'VKHB 2404 S',
    'VKHB 2405 S',
    'VKHB 2407 S',
    'VKHB 9001',
    'VKJP 3074',
    'VKMCV 51008',
    'VKMCV 51025',
    'VKMCV 51026',
    'VKMCV 52005',
    'VKMCV 53001',
    'VKMCV 53002',
    'VKMCV 53005',
    'VKMCV 53006',
    'VKMCV 53011',
    'VKMCV 53015',
    'VKMCV 54003',
    'VKMCV 54004',
    'VKMCV 55003',
    'VKMCV 55004',
    'VKMCV 55007',
    'VKMCV 56002',
    'VKMCV 56003',
    'VKMCV 56007',
    'VKMCV 56008',
    'VKMCV 56010',
    'VKMCV 56011',
    'VKMCV 56012',
    'VKMCV 57002',
    'VKMCV 57003',
    'VKPC 7007',
    'VKPC 7016',
    'VKPC 7019',
    'VKPC 7023',
    'VKPC 7024',
    'VKPC 7029',
    'VKPC 7030',
    'VKPC 7033',
    'VKPC 7036',
    'VKPC 7041',
    'VKPC 7042',
    'VKPC 7044',
    'VKPC 7045',
    'VKPC 7048',
    'VKPC 7050',
    'VKS 6105',
    'VKS 6376',
    'VKS 6377',
    'VKT 8604',
    'VKT 8625',
    'VKT 8627',
    'VKT 8645',
    'VKT 8701',
    'VKT 8721',
    'VKT 8749',
    'VKT 8756',
    'VKT 8757',
    'VKT 8761',
    'VKT 8864',
    'VKT 8871',
    'VKT 8927',
    'VKT 8940',
    'VKT 8956',
]

# fixme delete
REGISTERED_PARSERS.append(FrozaParser(name='froza', address='https://froza.ru'))


@app.get(path='/parsers', status_code=status.HTTP_200_OK)
async def get_list_parsers() -> list[str]:
    return [parser.address for parser in REGISTERED_PARSERS]


@app.get(path='/vendor_codes', status_code=status.HTTP_200_OK)
async def get_list_vendor_codes() -> list[str]:
    return [vendor_code for vendor_code in VENDOR_CODES]


@app.post(path='/vendor_codes', status_code=status.HTTP_201_CREATED)
async def create_new_list_vendor_codes(vendor_codes: VendorCode):
    # fixme check vendor_codes
    VENDOR_CODES.clear()
    VENDOR_CODES.extend(vendor_codes.data)


# fixme name, VC
@app.post(path='/run', status_code=status.HTTP_201_CREATED)
async def run(vendor_code: VC) -> list[str]:
    result: list[str] = []

    for parser in REGISTERED_PARSERS:
        result.extend(parser.run(
            vendor_codes=[vendor_code.vendor_code],
            makers=[vendor_code.maker.lower()],
            only_needful=vendor_code.only_needful_vendor_code,
        ))

    return result


# fixme name, VC
@app.post(path='/run_all', status_code=status.HTTP_201_CREATED)
async def run(filter_: VC_) -> list[str]:
    result: list[str] = []

    for parser in REGISTERED_PARSERS:
        result.extend(parser.run(
            vendor_codes=VENDOR_CODES,
            makers=[DEFAULT_MAKER_VALUE] * len(VENDOR_CODES),
            only_needful=filter_.only_needful_vendor_code,
        ))

    return result


# fixme name, VC
@app.post(path='/run_all_pair_data', status_code=status.HTTP_201_CREATED)
async def run(filter_: VCPair) -> list[str]:
    result: list[str] = []

    for parser in REGISTERED_PARSERS:
        result.extend(parser.run(
            vendor_codes=filter_.vendor_codes,
            makers=filter_.makers,
            only_needful=filter_.only_needful_vendor_code,
        ))

    return result


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
