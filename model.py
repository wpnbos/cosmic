from dataclasses import dataclass
from datetime import date
from typing import Any, Optional


class OutOfStock(Exception):
    pass


@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    quantity: int


class Batch:
    def __init__(self, reference: str, sku: str, quantity: int, eta: Optional[date]):
        self.reference = reference
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = quantity
        self._allocations: set[OrderLine] = set()

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine) -> None:
        if line in self._allocations:
            self._allocations.remove(line)

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.quantity

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    @property
    def allocated_quantity(self) -> int:
        return sum(line.quantity for line in self._allocations)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Batch):
            return self.reference == other.reference
        return False

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, Batch):
            return NotImplemented
        if other.eta is None:
            return False
        if self.eta is None:
            return False
        return self.eta > other.eta


def allocate(line: OrderLine, batches: list[Batch]) -> str:
    try:
        batch = next(batch for batch in sorted(batches) if batch.can_allocate(line))
    except StopIteration:
        raise OutOfStock(f"{line.sku} is out of stock")

    batch.allocate(line)
    return batch.reference
