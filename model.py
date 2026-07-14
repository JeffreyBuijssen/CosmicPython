from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Set


class OutOfStock(Exception):
    pass


def allocate(line:OrderLine, batches:List[Batch]) -> str:
    try:
        batch = next(batch for batch in sorted(batches) if batch.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration as exc:
        raise OutOfStock(f"Out of stock for sku{line.sku}") from exc


# @dataclase(frozen=True) makes OrderLine immutable
@dataclass(unsafe_hash=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int

class Batch:
    def __init__(self, ref:str, sku:str, qty:int, eta:Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations:set[OrderLine] = set()

    def __repr__(self):
        return f"<Batch {self.reference}>"
    # We usually make identity equality explicit in code by implementing equality operators on entities:
    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other) -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta
    
    def allocate(self, line:OrderLine) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line:OrderLine) -> None:
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line:OrderLine) -> bool:
        return (
            self.sku == line.sku and
            self.available_quantity >= line.qty
        )
