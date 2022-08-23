from datetime import date, timedelta
from typing import Tuple

from domain.model import Batch, OrderLine

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def make_batch_and_line(
    sku: str, batch_qty: int, line_qty: int
) -> Tuple[Batch, OrderLine]:
    return (
        Batch("batch=001", sku, batch_qty, eta=date.today()),
        OrderLine("order-ref", sku, line_qty),
    )


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch, line = make_batch_and_line("SMALL_TABLE", 20, 2)

    batch.allocate(line)

    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    batch, line = make_batch_and_line("SMALL_TABLE", 2, 1)

    assert batch.can_allocate(line)


def test_cannot_allocate_if_available_smaller_than_required():
    batch, line = make_batch_and_line("SMALL_TABLE", 1, 2)

    assert batch.can_allocate(line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("SMALL_TABLE", 2, 2)

    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_do_no_match():
    batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
    different_sku_line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)
    assert batch.can_allocate(different_sku_line) is False


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("CHOPSTICK-HOLDER", 10, 1)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 10


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("CHOPSTICK-HOLDER", 20, 2)
    batch.allocate(line)
    batch.allocate(line)

    assert batch.available_quantity == 18


def test_batches_with_equal_references_are_equal():
    batch = Batch("batch-001", "CHEESE-GRATER", 4, eta=None)
    equal_batch = Batch("batch-001", "BLACK-BOWL", 2, eta=None)

    assert batch == equal_batch


def test_batches_with_different_references_are_not_equal():
    batch = Batch("batch-001", "CHEESE-GRATER", 4, eta=None)
    equal_batch = Batch("batch-002", "BLACK-BOWL", 2, eta=None)

    assert batch != equal_batch
