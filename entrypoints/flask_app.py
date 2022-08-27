from datetime import datetime

from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import adapters.orm as orm
import config
import services.services as services
from services import unit_of_work

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    uow = unit_of_work.SqlAlchemyUnitOfWork(get_session)

    try:
        batchref = services.allocate(
            request.json["order_id"],
            request.json["sku"],
            request.json["quantity"],
            uow,
        )
    except services.InvalidSku as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201


@app.route("/add_batch", methods=["POST"])
def add_batch():
    uow = unit_of_work.SqlAlchemyUnitOfWork(get_session)

    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        request.json["reference"],
        request.json["sku"],
        request.json["quantity"],
        eta,
        uow,
    )

    return "OK", 201
