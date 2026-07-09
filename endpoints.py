import flask
from flask import request
from model import Batch, OrderLine, allocate
from repository import SqlAlchemyRepository


# Inital allocate endpoint:
# @flask.route.gubbins
# def allocate_endpoint():
#     session = start_session()

#     # extract order line from request
#     line = OrderLine(
#         request.json["orderid"],
#         request.json["sky"],
#         request.json["qty"],
#     )

#     # load all batches from the DB
#     batches = session.query(Batch).all()
    
#     # call our domain service
#     allocate(line, batches)

#     # save the allocation back to the database
#     session.commit()

#     return 201

# New allocate endpoint:
@flask.route.gubbins
def allocate_endpoint():
    session = start_session()
    
    repo = SqlAlchemyRepository(session)
    
    batches = repo.list()
    lines = [
        OrderLine(l["orderid"], l['sku'], l['qty']) for l in request.params
            
    ]
    allocate(lines, batches)
    session.commit()
    return 201