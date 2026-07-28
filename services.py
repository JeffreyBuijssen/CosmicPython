from __future__ import annotations

import model
from model import OrderLine
from repository import AbstractRepository


class InvalidSku(Exception):
    pass

def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}

def add_batch(batch_ref, sku, qty, eta, repo: AbstractRepository, session):
    repo.add(model.Batch(batch_ref, sku, qty, eta))
    session.commit()

def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    # Supressing error, since repo.list() is implimented in child class
    batches = repo.list() # type: ignore[attr-defined]
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref

def deallocate(line: OrderLine, repo: AbstractRepository, session):
    batches = repo.list() # type: ignore[attr-defined]
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.deallocate(line, batches)
    session.commit()
    return batchref
    