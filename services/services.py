from datetime import date
from typing import Optional

import domain.model as model
from adapters.repository import AbstractRepository
from services import unit_of_work


class InvalidSku(Exception):
    pass


def allocate(
    order_id: str, sku: str, quantity: int, uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        batches = uow.batches.list()
        if sku not in [batch.sku for batch in batches]:
            raise InvalidSku(f"Invalid sku {sku}")

        batchref = model.allocate(model.OrderLine(order_id, sku, quantity), batches)
        uow.commit()

    return batchref


def add_batch(
    reference: str,
    sku: str,
    quantity: int,
    eta: Optional[date],
    uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    with uow:
        uow.batches.add(model.Batch(reference, sku, quantity, eta))
        uow.commit()
