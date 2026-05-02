# algo-bot/services/strategy-service/strategies/base_strategy.py

import time
import uuid

class BaseStrategy:
    def __init__(self, instrument_token, strategy_id="BASE"):
        self.instrument_token = instrument_token
        self.strategy_id = strategy_id
        self.position = 0

    def on_tick(self, tick_data):
        # To be implemented by child classes (like l99_strategy)
        raise NotImplementedError("Strategies must implement on_tick")

    def create_order_intent(self, side, order_type, product, quantity):
        return {
            "intentId": str(uuid.uuid4()),
            "strategyId": self.strategy_id,
            "instrumentToken": self.instrument_token,
            "side": side,
            "orderType": order_type,
            "product": product,
            "quantity": quantity,
            "timestamp": int(time.time() * 1000)
        }