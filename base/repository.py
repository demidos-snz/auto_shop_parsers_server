import abc

from base.model import VendorCode


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, vendor_code: VendorCode):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, name: str) -> VendorCode:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, vendor_code: VendorCode):
        self.session.add(vendor_code)

    def get(self, name: str) -> VendorCode:
        return self.session.query(VendorCode).filter_by(name=name).first()
