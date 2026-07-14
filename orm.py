from sqlalchemy import Column, Date, ForeignKey, Integer, String, MetaData, Table
from sqlalchemy.orm import mapper, relationship

import model

metadata = MetaData()

order_lines = Table(
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255)),
)


batches = Table(
    "batches",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255)),
    Column("_purchased", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)



allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)

# This doesn't work anymore in the current version of sqlAlchemy.
# However figuring out how it exactly does work is outside the scope of this repo.
def start_mappers():
    lines_mapper = mapper(model.OrderLine, order_lines)
    mapper(
        model.Batch,
        batches,
        properties={
            "_allocations":relationship(
                lines_mapper, secondary=allocations, colleciton_class=set,
            )
        },
    )