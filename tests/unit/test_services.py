
import pytest

from domain import model
from service_layer import services
from adapters.repository import AbstractRepository


class FakeRepository(AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference) -> model.Batch:
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)

class FakeSession:
    comitted = False

    def commit(self):
        self.comitted = True

def test_returns_allocation():
    sku:str = "COMPLICATED-LAMP"
    line = model.OrderLine("o1", sku, 10)
    batch = model.Batch("b1", sku, 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())
    assert result == "b1"

def test_error_for_invalid_sku():
    bad_sku:str = "NONEXISTENTSKU"
    real_sku:str = "AREALSKU"
    line = model.OrderLine("o1", bad_sku, 10)
    batch = model.Batch("b1", real_sku, 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match=f"Invalid sku {bad_sku}"):
        services.allocate(line, repo, FakeSession())

def test_commits():
    sku:str = "OMINOUS-MIRROR"
    line = model.OrderLine("o1", sku, 10)
    batch = model.Batch("b1", sku, 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession ()

    services.allocate(line, repo, session)
    assert session.comitted is True

# Sanity check:
def test_add_batch_is_idempotent():
    # This should be enforced by the repository
    # checking if this is the case
    sku = "identical sku"
    repo = FakeRepository([])
    services.add_batch("b1", sku, 100, None, repo, FakeSession())
    batch = model.Batch("b1", sku, 100, None)
    
    assert batch == repo.get("b1")
    assert [batch] == repo.list()
    services.add_batch("b1", sku, 100, None, repo, FakeSession())

    assert batch == repo.get("b1")
    assert [batch] == repo.list()

#region stub
# def test_deallocate_decrements_available_quantity():
#     repo, session = FakeRepository([]), FakeSession()
#     # TODO: you'll need to implement the services.add_batch method
#     services.add_batch("b1", "BLUE-PLINTH", 100, None, repo, session)
#     line = model.OrderLine("o1", "BLUE-PLINTH", 10)
#     services.allocate(line, repo, session)
#     batch = repo.get(reference="b1")
#     assert batch.available_quantity == 90
#     # services.deallocate(...
#     ...
#     assert batch.available_quantity == 100
#endregion

def test_deallocate_decrements_available_quantity():
    # TODO: you'll need to implement the services.add_batch method
    # services.deallocate(...
    sku:str = "BLUE-PLINTH"
    repo, session = FakeRepository([]), FakeSession()

    services.add_batch("b1", sku, 100, None, repo, session)
    line = model.OrderLine("o1", sku, 10)


    reference:str = services.allocate(line, repo, session)
    assert reference == "b1"
    assert repo.get(reference).available_quantity == 90

    reference = services.deallocate(line, repo, session)
    assert reference == "b1"
    assert repo.get(reference).available_quantity == 100
    




def test_deallocate_decrements_correct_quantity(): # Bad naming ... _correct_sku instead?
    sku:str = "allocated-SKU"
    other_sku:str = "other-sku"
    bad_sku:str = "incorrect-SKU"

    repo = FakeRepository([])
    session = FakeSession()

    services.add_batch("b1", sku, 100, None, repo, session)
    services.add_batch("b2", other_sku, 100, None, repo, session)
    # services.add_batch("b2", incorrect_sku, 100, None, repo, session)

    line = model.OrderLine("o1", sku, 12)
    line2 = model.OrderLine("o2", sku, 10)
    line3 = model.OrderLine("o3", bad_sku, 10)

    services.allocate(line, repo, session) # allocated quantity = 10
    services.allocate(line2, repo, session) # allocated quantity = 22
    # services.allocate(line3, repo, session) <- invalid allocation

    assert repo.get("b1").allocated_quantity == 22

    services.deallocate(line, repo, session) # allocated quantity = 10

    with pytest.raises(services.InvalidSku, match=f"Invalid sku {bad_sku}"):
            # Invalid deallocation, allocated quantity = 10
            services.deallocate(line3, repo, FakeSession())


    batch_result = repo.get("b1")
    assert batch_result.allocated_quantity == 10
    assert batch_result.sku == sku
    

def test_trying_to_deallocate_unallocated_batch():
    
    sku:str = "SKU-1"

    repo = FakeRepository([])
    session = FakeSession()

    services.add_batch("b1", sku, 100, None, repo, session)
    line = model.OrderLine("o1", sku, 12)
    services.allocate(line, repo, session) # allocated quantity = 10
    services.deallocate(line, repo, session) # allocated quantity = 0

    with pytest.raises(model.LineNotAllocated, match=f"Line not allocated for sku {sku}"):
            # Invalid deallocation, allocated quantity = 10
            services.deallocate(line, repo, FakeSession())


    batch_result = repo.get("b1")
    assert batch_result.allocated_quantity == 0
    assert batch_result.sku == sku