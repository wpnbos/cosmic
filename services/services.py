from datetime import date
from typing import Optional

import domain.model as model
from adapters.repository import AbstractRepository


class InvalidSku(Exception):
    pass


def allocate(order_id: str, sku: str, quantity: int, repo: AbstractRepository, session):
    batches = repo.list()
    if sku not in [batch.sku for batch in batches]:
        raise InvalidSku(f"Invalid sku {sku}")

    batchref = model.allocate(model.OrderLine(order_id, sku, quantity), batches)
    session.commit()

    return batchref


def add_batch(
    reference: str,
    sku: str,
    quantity: int,
    eta: Optional[date],
    repo: AbstractRepository,
    session,
) -> None:
    repo.add(model.Batch(reference, sku, quantity, eta))
    session.commit()
