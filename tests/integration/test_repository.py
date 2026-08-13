# pylint: disable=missing-module-docstring, missing-function-docstring, protected-access
import pytest
from sqlalchemy import text
import sqlalchemy
from sqlalchemy.exc import IntegrityError

from allocation.domain import model
from allocation.adapters import repository

def test_repository_can_save_a_batch(session):
    batch = model.Batch("batch1", "RUSTY-SOUPDISH", 100, eta=None)

    repo = repository.SqlAlchemyRepository(session)
    repo.add(batch)
    session.commit()

    rows = session.execute(text(
        'SELECT reference, sku, _purchased_quantity, eta FROM "batches"'
    ))
    assert list(rows) == [("batch1", "RUSTY-SOUPDISH", 100, None)]

# SANITY CHECK
def test_repository_only_saves_unique_batch(session):
    insert_batch(session, "batch1")
    rows = session.execute(text(
        'SELECT reference, sku, _purchased_quantity, eta FROM "batches"'
    ))
    assert list(rows) == [("batch1", "GENERIC-SOFA", 100, None)]

    with pytest.raises(sqlalchemy.exc.IntegrityError):
        insert_batch(session, "batch1")
        
def insert_order_line(session):
    session.execute(text(
        "INSERT INTO order_lines (orderid, sku, qty)"
        ' VALUES ("order1", "GENERIC-SOFA", 12)'
    ))
    [[orderline_id]] = session.execute(text(
        "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"),
        dict(orderid="order1", sku="GENERIC-SOFA"),
    )
    return orderline_id

def insert_batch(session, batch_id):
    session.execute(text(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        ' VALUES (:batch_id, "GENERIC-SOFA", 100, null)'),
        dict(batch_id=batch_id),
    )
    [[batch_id]] = session.execute(text(
        'SELECT id FROM batches WHERE reference=:batch_id AND sku="GENERIC-SOFA"'),
        dict(batch_id=batch_id),
    )
    return batch_id

def insert_allocation(session, orderline_id, batch_id):
    session.execute(text(
        "INSERT INTO allocations (orderline_id, batch_id)"
        " VALUES(:orderline_id, :batch_id)"),
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )

def test_repository_can_retreive_batch_with_allocations(session):
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, "batch1")
    insert_batch(session, "batch2")
    insert_allocation(session, orderline_id, batch1_id)

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get("batch1")

    expected = model.Batch("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected # Batch.__eq__ only compares reference
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {
        model.OrderLine("order1", "GENERIC-SOFA", 12),
    }

def test_repository_can_only_add_batch_once(session):
    batch_id = "batch_idempotence"
    insert_batch(session, batch_id)
    # insert_batch(session, "batch1")
    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.list()
    expected = [model.Batch(batch_id, "GENERIC-SOFA", 100, eta=None)]
    # assert retrieved == expected
    assert len(retrieved) == len(expected) # repo should only contain batch
    # Commented out since testing ability to save batch
    # is outside of scope for this test
    # assert retrieved[0] == expected[0]
    # assert retrieved[0].sku == expected[0].sku
    # assert retrieved[0]._purchased_quantity == expected[0]._purchased_quantity
    
    
    with pytest.raises(IntegrityError, match=batch_id):
        session.execute(text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
            ' VALUES (:batch_id, "GENERIC-SOFA", 100, null)'),
        dict(batch_id=batch_id),
        )