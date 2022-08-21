import model
from repository import AbstractRepository


class InvalidSku(Exception):
    pass


def allocate(line: model.OrderLine, repo: AbstractRepository, session):
    batches = repo.list()
    if line.sku not in [batch.sku for batch in batches]:
        raise InvalidSku(f"Invalid sku {line.sku}")

    batchref = model.allocate(line, batches)
    session.commit()

    return batchref
