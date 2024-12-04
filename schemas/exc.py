class InsufficientStockException(Exception):
    def __init__(self):
        super().__init__(f"The chosen amount of product exceeds the amount in stock")
