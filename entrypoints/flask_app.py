from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import adapters.orm as orm
import config
import domain.model as model
import services.services as services
from adapters.repository import SqlAlchemyRepository

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    repository = SqlAlchemyRepository(session)
    line = model.OrderLine(
        request.json["order_id"], request.json["sku"], request.json["quantity"]
    )

    try:
        batchref = services.allocate(line, repository, session)
    except services.InvalidSku as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201
