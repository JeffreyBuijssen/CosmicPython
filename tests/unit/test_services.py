
import pytest

from allocation.domain import model
from allocation.service_layer import services
from allocation.adapters import repository

class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference) -> model.Batch:
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)

    @staticmethod
    def for_batch(ref, sku, qty, eta=None):
        return FakeRepository([
            model.Batch(ref, sku, qty, eta),
        ])

class FakeSession:
    comitted = False

class FakeUnitOfWork:
    ...

def test_add_batch():
    uow = FakeUnitOfWork()
    # repo, session = FakeRepository([]), FakeSession()
    # fake_uow_starter = FakeUoWContextManger(uow) ?
    # fake_uow_starter = contextlib.nullcontext(uow) ?
    # services.add_batch("b1", "CRUNCY-ARMCHAIR", 100, None, fake_uow_starter)
    assert uow.batches.get("b1") is not None
    assert uow.comitted

@pytest.mark.skip("unskip and fix when ready")
def test_allocate_returns_allocation():
    sku:str = "COMPLICATED-LAMP"
    uow = FakeUnitOfWork()
    services.add_batch("batch1", sku, 100, None, uow)
    result = services.allocate("o1", sku, 10, uow)
    assert result == "batch1"

@pytest.mark.skip("unskip and fix when ready")
def test_allocate_errors_for_invalid_sku():
    bad_sku:str = "NONEXISTENTSKU"
    real_sku:str = "AREALSKU"
    uow = FakeUnitOfWork()
    services.add_batch("b1", real_sku, 100, None, uow)
    with pytest.raises(services.InvalidSku, match=f"Invalid sku {bad_sku}"):
        services.allocate("o1", bad_sku, 10, uow)

@pytest.mark.skip("unskip and fix when ready")
def test_commits():
    sku:str = "OMINOUS-MIRROR"
    uow = FakeUnitOfWork()
    services.add_batch("b1", sku, 100, None, uow)
    services.allocate("o1", sku, 10, uow)
    assert uow.comitted



@pytest.mark.skip("unskip and fix when ready")
def test_deallocate_decrements_available_quantity():
    sku:str = "BLUE-PLINTH"
    uow = FakeUnitOfWork()

    services.add_batch("b1", sku, 100, None, uow)


    reference:str = services.allocate("o1", sku, 10, uow)
    assert reference == "b1"
    assert uow.batches.get(reference).available_quantity == 90

    reference = services.deallocate("o1", sku, 10, uow)
    assert reference == "b1"
    assert uow.batches.get(reference).available_quantity == 100

    
@pytest.mark.skip("unskip and fix when ready")
def test_deallocate_decrements_correct_quantity(): # Bad naming ... _correct_sku instead?
    sku:str = "allocated-SKU"
    other_sku:str = "other-sku"
    bad_sku:str = "incorrect-SKU"

    uow = FakeUnitOfWork()
    
    services.add_batch("b1", sku, 100, None, uow)
    services.add_batch("b2", other_sku, 100, None, uow)

    services.allocate("o1", sku, 12, uow) # allocated quantity = 10
    services.allocate("o2", sku, 10, uow) # allocated quantity = 22

    assert uow.batches.get("b1").allocated_quantity == 22

    services.deallocate("o1", sku, 12, uow) # allocated quantity = 10

    with pytest.raises(services.InvalidSku, match=f"Invalid sku {bad_sku}"):
        # Invalid deallocation, allocated quantity = 10
        services.deallocate("o3", bad_sku, 10, uow)


    batch_result = uow.batches.get("b1")
    assert batch_result.allocated_quantity == 10
    assert batch_result.sku == sku
    

@pytest.mark.skip("unskip and fix when ready")
def test_trying_to_deallocate_unallocated_batch():
    sku:str = "SKU-1"
    uow = FakeUnitOfWork()

    services.add_batch("b1", sku, 100, None, uow)
    services.allocate("o1", sku, 10, uow) # allocated quantity = 10
    services.deallocate("o1", sku, 10, uow) # allocated quantity = 0

    
    with pytest.raises(model.LineNotAllocated, match=f"Line not allocated for sku {sku}") as exc_info:
        # Invalid deallocation, allocated quantity = 10
        
        try:
            services.deallocate("o1", sku, 10, uow)
        except Exception as exc:
            print(f"Expected: {(model.LineNotAllocated)}")
            print(f"found: {type(exc)}")
            print(f"Is instance of type: {isinstance(exc, model.LineNotAllocated)}")
            print(f"Exc msg: {exc.args[0]}")
            raise exc


    batch_result = uow.batches.get("b1")
    assert batch_result.allocated_quantity == 0
    assert batch_result.sku == sku
