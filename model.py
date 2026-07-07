from dataclasses import dataclass
from datetime import date


@dataclass


class Product:
    sku:str
    _available_quantity:int


    def __init__(self, sku:str, available_quatity:int):
        self.sku = sku
        self._available_quantity = available_quatity


class OrderLine:
    sku:str
    amount:int

    def __init__(self, sku, amount):
        self.sku = sku
        self.amount = amount

# class Order:
#     reference:str
#     order_lines:list[OrderLine]

#     def __init__(self, reference:str, order_lines:list[OrderLine]):
#         self.reference = reference
#         self.order_lines = order_lines

class Batch:
    reference:str
    sku:str
    amount:int
    ETA:date
    _orderlines:list[OrderLine]


    def __init__(self, reference, sku, amount, eta:date):
        self.reference = reference
        self.sku = sku
        self.amount = amount
        self.ETA = eta

    @staticmethod
    def allocate(orderlines):
       print("allocating")

    



