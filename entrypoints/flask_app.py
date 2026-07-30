from datetime import datetime

from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
from domain import model
from adapters import orm, repository
from service_layer import services
# import services

# orm.start_mappers()
# get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
# app = Flask(__name__)

# @app.route("/allocate", methods=["POST"])
# def allocate_endpoint():
#     session = get_session()
#     repo = repository.SqlAlchemyRepository(session)
#     line = model.OrderLine(
#         request.json["orderid"],
#         request.json["sku"],
#         request.json["qty"],
#     )

#     try:
#         batchref = services.allocate(line, repo, session)
#     except (model.OutOfStock, services.InvalidSku) as e:
#         return {"message": str(e)}, 400
    
#     return {"batchref": batchref}, 201

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)

def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}

# OLD:
# @app.route("/allocate", methods=["POST"])
# def allocate_endpoint():
#     session = get_session()
#     batches = repository.SqlAlchemyRepository(session).list()
#     line = model.OrderLine(
#         request.json["orderid"],
#         request.json["sku"],
#         request.json["qty"],
#     )
#     if not is_valid_sku(line.sku, batches):
#         return {"message": f"Invalid sku {line.sku}"}, 400
#     try:
#         batchref = model.allocate(line, batches)
#     except model.OutOfStock as e:
#         return {"message": str(e)}, 400
    

#     session.commit()
#     return {"batchref": batchref}, 201

# NEW abstracted flow:
@app.route("/add_batch", methods=["POST"])
def add_batch():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        eta,
        repo,
        session
    )
    return "OK", 201

@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    line = model.OrderLine(
        request.json["orderid"],
        request.json["sku"],
        request.json["qty"],
    )

    try:
        batchref = services.allocate(line, repo, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201

@app.route("/deallocate", methods=["POST"])
def deallocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    line = model.OrderLine(
        request.json["orderid"],
        request.json["sku"],
        request.json["qty"],
    )

    try:
        batchref = services.deallocate(line, repo, session)
    except (model.LineNotAllocated, services.InvalidSku) as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201


        