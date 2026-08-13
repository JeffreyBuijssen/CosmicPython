# pylint: disable=missing-module-docstring, missing-function-docstring, invalid-name

from typing import Final
from datetime import date, timedelta

import pytest

from src.allocation.domain.model import Batch, OrderLine, OutOfStock, allocate

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)

def test_prefers_current_stock_batches_to_shipments():
    SKU="RETRO-CLOCK"
    in_stock_batch = Batch("in-stock-batch", SKU, 100, eta=None)
    shipment_batch = Batch("shipment-batch", SKU, 100, eta=tomorrow)
    line = OrderLine("oref", SKU, 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100

def test_prefers_earlier_batches():
    SKU = "MINIMALIST-SPOON"
    earliest = Batch("speedy-batch", SKU, 100, eta=today)
    medium = Batch("normal-batch", SKU, 100, eta=tomorrow)
    latest = Batch("slow-batch", SKU, 100, eta=later)
    line = OrderLine("order1", SKU, 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert latest.available_quantity == 100
    assert medium.available_quantity == 100


def test_returns_allocated_batch_ref():
    SKU:Final[str]="HIGHBROW-POSTER"
    in_stock_batch = Batch("in-stock-batch-ref", SKU, 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref", SKU, 100, eta=tomorrow)
    line = OrderLine("oref", SKU, 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.reference

def test_raises_out_of_stock_exception_if_cannot_allocate():
    SKU="SMALL-FORK"
    batch = Batch("batch1", SKU, 10, eta=today)
    allocate(OrderLine("order-1", SKU, 10), [batch])

    with pytest.raises(OutOfStock, match=SKU):
        allocate(OrderLine("ordere2", SKU, 1), [batch])
