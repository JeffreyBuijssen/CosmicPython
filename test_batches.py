# pylint: disable=missing-module-docstring, missing-function-docstring
from datetime import date, timedelta

from model import Batch, OrderLine

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)

BATCH_SIZE = 20
LINE_SIZE = 2

def make_batch_and_line(sku, batch_qty, line_qty):
    return(
        Batch("batch-001", sku, batch_qty, eta=today),
        OrderLine("order-123", sku, line_qty)
    )

def test_allocating_to_a_batch_reduces_the_available_quantity():
    expected_amount = BATCH_SIZE - LINE_SIZE

    batch = Batch("batch-001", "SMALL-TABLE", qty=BATCH_SIZE, eta=today)
    line = OrderLine("order-ref","SMALL-TABLE", LINE_SIZE)
    batch.allocate(line)

    assert batch.available_quantity == expected_amount

def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    assert large_batch.can_allocate(small_line) is True


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)
    assert small_batch.can_allocate(large_line) is False

def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)
    assert batch.can_allocate(line)

def test_cannot_alocate_if_skus_do_not_match():
    batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 100, eta =None)
    different_sku_line = OrderLine("order-123", "EXPENASIVE-TOASTER", 10)

    assert batch.can_allocate(different_sku_line) is False

def test_allocate_is_idempotent():
    expected_amount = BATCH_SIZE - LINE_SIZE - 0

    batch, line = make_batch_and_line("BLUE-VASE", BATCH_SIZE, LINE_SIZE)
    batch.allocate(line)
    batch.allocate(line)

    assert batch.available_quantity == expected_amount

def test_deallocate():
    expected_amount = BATCH_SIZE - LINE_SIZE + LINE_SIZE

    batch, line = make_batch_and_line("EXPENSIVE-FOOTSTOOL", BATCH_SIZE, LINE_SIZE)
    batch.allocate(line)
    batch.deallocate(line)
    assert batch.available_quantity == expected_amount

def test_can_only_deallocate_allocated_lines():
    expected_amount = BATCH_SIZE + 0

    batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET", BATCH_SIZE, LINE_SIZE)
    batch.deallocate(unallocated_line)

    assert batch.available_quantity == expected_amount
