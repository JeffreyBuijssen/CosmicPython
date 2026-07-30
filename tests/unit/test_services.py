
import pytest

from domain import model
from service_layer import services
from adapters import repository


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

    def commit(self):
        self.comitted = True

def test_allocate_returns_allocation():
    sku:str = "COMPLICATED-LAMP"
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("batch1", sku, 100, None, repo, session)
    result = services.allocate("o1", sku, 10, repo, FakeSession())
    assert result == "batch1"

def test_allocate_errors_for_invalid_sku():
    bad_sku:str = "NONEXISTENTSKU"
    real_sku:str = "AREALSKU"
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", real_sku, 100, None, repo, session)
    with pytest.raises(services.InvalidSku, match=f"Invalid sku {bad_sku}"):
        services.allocate("o1", bad_sku, 10, repo, FakeSession())

def test_commits():
    sku:str = "OMINOUS-MIRROR"
    repo = FakeRepository([])
    session = FakeSession ()
    services.add_batch("b1", sku, 100, None, repo, session)
    services.allocate("o1", sku, 10, repo, session)
    assert session.comitted is True

def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)
    assert repo.get("b1") is not None
    assert session.comitted


def test_deallocate_decrements_available_quantity():
    sku:str = "BLUE-PLINTH"
    repo, session = FakeRepository([]), FakeSession()

    services.add_batch("b1", sku, 100, None, repo, session)


    reference:str = services.allocate("o1", sku, 10, repo, session)
    assert reference == "b1"
    assert repo.get(reference).available_quantity == 90

    reference = services.deallocate("o1", sku, 10, repo, session)
    assert reference == "b1"
    assert repo.get(reference).available_quantity == 100

    
def test_deallocate_decrements_correct_quantity(): # Bad naming ... _correct_sku instead?
    sku:str = "allocated-SKU"
    other_sku:str = "other-sku"
    bad_sku:str = "incorrect-SKU"

    repo, session = FakeRepository([]), FakeSession()

    services.add_batch("b1", sku, 100, None, repo, session)
    services.add_batch("b2", other_sku, 100, None, repo, session)

    services.allocate("o1", sku, 12, repo, session) # allocated quantity = 10
    services.allocate("o2", sku, 10, repo, session) # allocated quantity = 22

    assert repo.get("b1").allocated_quantity == 22

    services.deallocate("o1", sku, 12, repo, session) # allocated quantity = 10

    with pytest.raises(services.InvalidSku, match=f"Invalid sku {bad_sku}"):
        # Invalid deallocation, allocated quantity = 10
        services.deallocate("o3", bad_sku, 10, repo, FakeSession())


    batch_result = repo.get("b1")
    assert batch_result.allocated_quantity == 10
    assert batch_result.sku == sku
    

def test_trying_to_deallocate_unallocated_batch():
    sku:str = "SKU-1"
    repo, session = FakeRepository([]), FakeSession()

    services.add_batch("b1", sku, 100, None, repo, session)
    services.allocate("o1", sku, 10, repo, session) # allocated quantity = 10
    services.deallocate("o1", sku, 10, repo, session) # allocated quantity = 0

    with pytest.raises(model.LineNotAllocated, match=f"Line not allocated for sku {sku}"):
        # Invalid deallocation, allocated quantity = 10
        services.deallocate("o1", sku, 10, repo, FakeSession())


    batch_result = repo.get("b1")
    assert batch_result.allocated_quantity == 0
    assert batch_result.sku == sku