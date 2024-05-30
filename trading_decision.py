# trading_decision.py
import openai
import json
from datetime import datetime
from logger_setup import get_logger
import logging

# ロガーの取得
logger = get_logger(__name__)

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

class TradingDecision:
    def __init__(self, openai_api_key):
        self.openai_api_key = openai_api_key
        openai.api_key = self.openai_api_key

    def load_messages(self, market_data, portfolio_data, order_data, execution_data, order_book_data, current_time):
        with open('messages.json', 'r', encoding='utf-8') as file:
            messages = json.load(file)
        
        # プレースホルダーを変数で置換
        for message in messages:
            message['content'] = message['content'].format(
                market_data=market_data,
                portfolio_data=portfolio_data,
                order_data=order_data,
                execution_data=execution_data,
                order_book_data=order_book_data,
                current_time=current_time
            )
        return messages

    def get_trading_decision(self, market_data, portfolio_data, order_data, execution_data, order_book_data):
        current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        messages = self.load_messages(market_data, portfolio_data, order_data, execution_data, order_book_data, current_time)

        functions = [
            {
                "name": "order_cancel",
                "description": "Function calling to cancel an open BTC order.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string", "description": "The child_order_acceptance_id of the order to be canceled."}
                    },
                    "required": ["order_id"]
                }
            },
            {
                "name": "order_method",
                "description": "Function calling to place a BTC buy or sell order. The minimum order size is 0.001 BTC.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "side": {
                            "type": "string",
                            "enum": ["BUY", "SELL"],
                            "description": "The direction of the trade. 'BUY' or 'SELL'."
                        },
                        "price": {"type": "number", "description": "The order price in JPY."},
                        "size": {"type": "number", "description": "The order quantity. The minimum order size is 0.001 BTC."},
                        "order_type": {
                            "type": "string",
                            "enum": ["LIMIT", "STOP"],
                            "description": "The type of order. Specify 'LIMIT' for limit order or 'STOP' for stop order."
                        },
                        "trigger_price": {"type": "number", "description": "The trigger price. Only specify for 'STOP' orders."}
                    },
                    "required": ["side", "price", "size", "order_type"]
                }
            }
        ]

        # print(messages)

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            functions=functions,
            function_call="auto"
        )

        #print(response)

        if response.choices[0].message.content:
            logger.debug(f"message content: {response.choices[0].message.content}")

        if response.choices and response.choices[0].message and response.choices[0].message.function_call:
            function_call = response.choices[0].message.function_call
            function_call.arguments = json.loads(function_call.arguments)  # JSON文字列を辞書に変換
            return function_call
        else:
            return None