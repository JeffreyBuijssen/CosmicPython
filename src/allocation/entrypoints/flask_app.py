from datetime import datetime

from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation import config
from allocation.domain import model
from allocation.adapters import orm, repository
from allocation.service_layer import services
from allocation.service_layer import unit_of_work

app = Flask(__name__)

def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


# NEW abstracted flow:
@app.route("/add_batch", methods=["POST"])
def add_batch():
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        eta,
        uow
    )
    return "OK", 201

@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    try:
        batchref = services.allocate(
            request.json["orderid"],
            request.json["sku"],
            request.json["qty"],
            uow)
    except (model.OutOfStock, services.InvalidSku) as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201

@app.route("/deallocate", methods=["POST"])
def deallocate_endpoint():
    uow = unit_of_work.SqlAlchemyUnitOfWork()

    try:
        # batchref = services.deallocate(line, repo, session)
        batchref = services.deallocate(
            request.json["orderid"],
            request.json["sku"],
            request.json["qty"],
            uow
        )
    except (model.LineNotAllocated, services.InvalidSku) as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201
