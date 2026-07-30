from service_layer import unit_of_work


def get_allocated_batch_ref(session, order_id:str, sku:str) -> str:
    uow = unit_of_work.SqlAlchemyUnitOfWork(session)
    with uow:
        batches = uow.batches.list() if 

def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    insert_batch(session, "batch1", "HIPSTER-WORKBENCH", 100, None)
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        batch = uow.batches.get(refernece="batch1")
        line = model.OrderLine("o1", "HIPSTER-WORKBENCH", 10)
        batch.allocate(line)
        uow.commit()

    batchref = get_allocatd_batch_ref(session, "o1", "HIPSTER-WORKBENCH")
    assert batchref == "batch1"