import pytest
from dataclasses import dataclass
from typing import NewType, NamedTuple
from collections import namedtuple
from numbers import Number
from __future__ import annotations
# If you really want to go to town with type hits,
# you could go as far as wrapping primitive types by using typing.NewType:

Quantity = NewType("Quantity", int)
ProductReference = NewType("ProductReference", str)
OrderReference = NewType("OrderReference", str)


# Whenever we havea business concept that has data but no identity,
# we often choose to represent it using the Value Object pattern.
# A value object is any domain object that is uniquely identified
# by the data it holds; we usually make them immutable

@dataclass(frozen=True)
class OrderLine:
    orderid: OrderReference
    sku: ProductReference
    qty: Quantity

# One of the nice things that dataclasses (or named tuples) give us
# is value equality, which is a fancy way of saying,
# "Two lies wit hte same orderid, sku and qty are equal"

@dataclass(frozen=True)
class Name:
    first_name: str
    surname: str


@dataclass(frozen=True)
class Money:
    currency: str
    value: int

    def __add__(self, other) -> Money:
        if other.currency != self.currency:
            raise ValueError(f"Cannot add {self.currency} to {other.currency}")
        return Money(self.currency, self.value + other.value)
    
    def __sub__(self, other) -> Money:
        if other.currency != self.currency:
            raise ValueError(f"Cannot add {self.currency} to {other.currency}")
        return Money(self.currency, self.value - other.value)
    
    def __mul__(self, other) -> Money:
        if isinstance(other, Money):
            raise TypeError(f"Cannot multiply {self.currency} with {other.currency}. Can only multiply {type(self)}-types with {type(int)}.")
        if not isinstance(other, Number):
            return NotImplemented
        return Money(self.currency, self.value * other)

Line = namedtuple('Line', ['sku', 'qty'])

def test_equality():
    assert Money('gbp', 10) == Money('gbp', 10)
    assert Name('Harry', 'Percival') != Name('Bob', 'Gregory')
    assert Line('RED-CHAIR', 5) == Line('RED-CHAIR', 5)

# It's common to support operations on vlaues; for example,
# Mathmatical operators

fiver = Money('gbp', 5)
tenner = Money('gbp', 10)

def test_can_add_money_values_for_the_same_currency():
    assert fiver + fiver == tenner

def test_can_substract_money_values():
    assert tenner - fiver == fiver

def test_adding_different_currencies_fails():
    with pytest.raises(ValueError):
        Money('usd', 10) + tenner

def test_can_multiply_money_by_a_number():
    assert fiver * 5 == Money('gbp', 25)

def test_multiplying_two_money_values_is_an_error():
    with pytest.raises(TypeError):
        tenner * fiver

'''
Value Objects and Entities
We use the term 'entity' to describe a domain object that has long-lived identity.
On the previous page we introduced a Name class as a value object.
If we take the name Harry Percival and change one letter,
We have a new  Name object Barry Percival

It should be clear that Harry Percival is not equal to Barry Percival:
'''

def test_name_equality():
    assert Name("Harry", "Percival") != Name("Barry",  "Percival")

'''
But what about Harry as a person? People do change their names, and their 
marital status, and even their gender, but we continue to recognize them
as the same individual. That's because humans, unlike names, have a
persitent <u>identity</u>:
'''

class Person:
    def __init__(self, name:Name):
        self.name = name

def test_barry_is_harry():
    harry = Person(Name("Harry", "Percival"))
    barry = harry
    barry.name = Name("Barry", "Percival")
    
    assert harry is barry and barry is harry
