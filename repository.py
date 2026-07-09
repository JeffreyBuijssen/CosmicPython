## You have to get your data from somewhere

# import all_my_data
# from model import Batch

# def create_a_batch():
#     batch = Batch(...)
#     all_my_data.batches.add(batch)

# def modify_a_batch(batch_id, new_quantity):
#     batch = all_my_data.batches.get(batch_id)
#     batch.chance_initial_quantity(new_quantity)

import abc
import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch:model.Batch):
        raise NotImplementedError
    
    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError
    
class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, reference):
        return self.session.query(model.Batch).filter_by(reference=reference).one()
    
    def list(self):
        return self.session.query(model.Batch).all()

import sqlite3

class ORMlessSqlLit3Repository(AbstractRepository):
    
    def __init__(self):
        self.connection = sqlite3.connect(":memory:")
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS "batches"
            (
                [id] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                [reference] NVARCHAR(255) UNIQUE NOT NULL,
                [sku] NVARCHAR[255] NOT NULL,
                [qty] INTEGER NOT NULL, 
                [eta] DATE
            );
            CREATE INDEX [I_Reference] ON "batches" ([reference]);
            CREATE TABLE IF NOT EXISTS "order_lines"
            (
                [id] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                [order_id] NVARCHAR(255) NOT NULL,
                [sku] NVARCHAR(255) NOT NULL,
                [qty] INTERGER NOT NULL, 
                FOREIGN KEY ([batch_id]) REFERENCES "batches" ([id])
                            ON DELETE NO ACTION ON UPDATE NO ACTION
            );
            CREATE INDEX [IFK_OrderLinesBatchId] ON "order_lines" ([order_id, batch_id])
            """
        )

    def add(self, batch):
        self.cursor.execute(
            f"""
            INSERT INTO "batches" (reference, sku, qty, eta) VALUES
                (
                    {batch.reference},
                    {batch.sku},
                    {batch._purchased_quantity},
                    {batch.eta}
                );
            """
        )

    def get(self, reference):
        result = self.cursor.execute(
            f"""
                SELECT reference, sku, qty, eta
                FROM "batches" WHERE reference = {reference};
            """
        ).one()
        return model.Batch(result["reference"], result["sku"], result["qty"], result["eta"])
        
    def list(self):
        batches = self.cursor.execute(
            """
            SELECT reference, sku, qty, eta
            FROM "batches"
            """
        ).all()
        return list(model.Batch(x["reference"], x["sku"], x["qty"], x["eta"]) for x in batches)


class FakeRepository(AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)
    
    def list(self):
        return list(self._batches)
        