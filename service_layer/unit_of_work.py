from abc import ABC


class AbstractUnitOfWork(ABC):
    ...

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    ...