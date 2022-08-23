import re
from datetime import date, timedelta

import pytest

from domain.model import Batch, OrderLine, OutOfStock, allocate

today = date.today()
tomorrow = today + timedelta(days=1)
later = today + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "KEY-CHAIN", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "KEY-CHAIN", 200, eta=tomorrow)
    line = OrderLine("order-ref", "KEY-CHAIN", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 200


def test_prefers_earlier_batches():
    earliest_batch = Batch("speedy-batch", "EXTRAVAGANT-TOASTER", 100, eta=today)
    later_batch = Batch("speedy-batch", "EXTRAVAGANT-TOASTER", 100, eta=tomorrow)
    latest_batch = Batch("speedy-batch", "EXTRAVAGANT-TOASTER", 100, eta=later)
    line = OrderLine("order-ref", "EXTRAVAGANT-TOASTER", 10)

    allocate(line, [earliest_batch, later_batch, latest_batch])

    assert earliest_batch.available_quantity == 90
    assert later_batch.available_quantity == 100
    assert latest_batch.available_quantity == 100


def test_returns_allocated_batch_reference():
    in_stock_batch = Batch("in-stock-batch", "KEY-CHAIN", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "KEY-CHAIN", 200, eta=tomorrow)
    line = OrderLine("order-ref", "KEY-CHAIN", 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("batch-001", "TINY-MELON", 3, eta=today)
    allocate(OrderLine("order-001", "TINY-MELON", 3), [batch])

    with pytest.raises(OutOfStock, match=re.compile(r".*TINY_MELON.*")):
        allocate(OrderLine("order-002", "TINY_MELON", 2), [batch])
