"""
売買判断
"""

import os
import json
import logging
from datetime import datetime
import openai
from src.logger_setup import get_logger

# ロガーの取得
logger = get_logger(__name__)

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)


class TradingDecision:
    """
    売買判断を行うクラス
    """

    def __init__(self, config):
        self.openai_api_key = config.openai_api_key
        self.prompt_file_name = config.prompt_file
        self.project_root = config.project_root
        self.trading_interval = config.trading_interval
        openai.api_key = self.openai_api_key

    def load_messages(
        self,
        market_data,
        ticker_data,
        portfolio_data,
        order_data,
        execution_data,
        current_time,
    ):
        """
        メッセージを読み込む
        """
        messages = []

        prompt_file = os.path.join(self.project_root, self.prompt_file_name)

        # メッセージを読み込む
        if os.path.exists(prompt_file):
            with open(prompt_file, "r", encoding="utf-8") as file:
                messages = json.load(file)

        # print(prompt_file)

        # プレースホルダーを変数で置換
        for message in messages:
            message["content"] = message["content"].format(
                market_data=market_data,
                ticker_data=ticker_data,
                portfolio_data=portfolio_data,
                order_data=order_data,
                execution_data=execution_data,
                current_time=current_time,
                trading_interval=str(int(self.trading_interval / 60)),
            )
        return messages

    def get_trading_decision(
        self,
        market_data,
        ticker_data,
        portfolio_data,
        order_data,
        execution_data,
    ):
        """
        売買判断を行う
        """
        current_time = (
            datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        )

        messages = self.load_messages(
            market_data,
            ticker_data,
            portfolio_data,
            order_data,
            execution_data,
            current_time,
        )

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "order",
                    "description": "Function calling to place a BTC buy or"
                    "sell order. The minimum order size is 0.001 BTC."
                    "The order price should be entered in units of 1 JPY."
                    "This order will automatically expire"
                    " if it is not executed within 10 minutes.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "side": {
                                "type": "string",
                                "enum": ["BUY", "SELL"],
                                "description": "The direction of the"
                                "trade. 'BUY' or 'SELL'. ",
                            },
                            "price": {
                                "type": "integer",
                                "description": "The order price in JPY."
                                "Enter the price in units of 1 JPY."
                                "If you specify 'LIMIT' for the order_type,"
                                "you need to specify the price.",
                            },
                            "size": {
                                "type": "number",
                                "description": "The order quantity in BTC."
                                "The minimum value is 0.001 BTC, "
                                "specified in increments of 0.0001 BTC.",
                            },
                            "order_type": {
                                "type": "string",
                                "enum": ["LIMIT", "MARKET"],
                                "description": "The type of order."
                                "Specify 'LIMIT' for limit order or"
                                "'MARKET' for market order.",
                            },
                            "time_in_force": {
                                "type": "string",
                                "enum": ["GTC", "IOC", "FOK"],
                                "description": "The time in force of the "
                                "order. Specify 'GTC' for Good-Til-Canceled,"
                                "'IOC' for Immediate-Or-Cancel,"
                                "or 'FOK' for Fill-Or-Kill.",
                            },
                        },
                        "required": [
                            "side",
                            "price",
                            "size",
                            "order_type",
                            "time_in_force",
                        ],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "cancel",
                    "description": "Function calling to cancel an"
                    "open BTC order."
                    "This action does not allow new orders to be placed "
                    "until the next decision cycle, so if you want to place "
                    "new orders at the same time, "
                    "use the cancel_and_order function.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "The child_order_acceptance_id"
                                " of the order to be canceled.",
                            }
                        },
                        "required": ["order_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "cancel_and_order",
                    "description": "Function calling to cancel an open"
                    "BTC order and place a new order."
                    "The minimum order size is 0.001 BTC."
                    "The order price should be entered in units of 1 JPY."
                    "This order will automatically expire"
                    "if it is not executed within 10 minutes.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "The child_order_acceptance_id"
                                " of the order to be canceled.",
                            },
                            "side": {
                                "type": "string",
                                "enum": ["BUY", "SELL"],
                                "description": "The direction of the"
                                "trade. 'BUY' or 'SELL'. ",
                            },
                            "price": {
                                "type": "integer",
                                "description": "The order price in JPY."
                                "Enter the price in units of 1 JPY."
                                "If you specify 'LIMIT' for the order_type,"
                                "you need to specify the price.",
                            },
                            "size": {
                                "type": "number",
                                "description": "The order quantity in BTC."
                                "The minimum value is 0.001 BTC, "
                                "specified in increments of 0.0001 BTC.",
                            },
                            "order_type": {
                                "type": "string",
                                "enum": ["LIMIT", "MARKET"],
                                "description": "The type of order."
                                "Specify 'LIMIT' for limit order or"
                                "'MARKET' for market order.",
                            },
                            "time_in_force": {
                                "type": "string",
                                "enum": ["GTC", "IOC", "FOK"],
                                "description": "The time in force of the "
                                "order. Specify 'GTC' for Good-Til-Canceled,"
                                "'IOC' for Immediate-Or-Cancel,"
                                "or 'FOK' for Fill-Or-Kill.",
                            },
                        },
                        "required": [
                            "order_id",
                            "side",
                            "price",
                            "size",
                            "order_type",
                        ],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "hold",
                    "description": "Function calling to hold the current"
                    " position without taking any action.",
                },
            },
        ]

        # print(messages)

        # OpenAIにリクエストを送信
        # response = None
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="required",
        )

        # logger.debug("Response: %s", response)
        if response.choices[0].message.tool_calls:
            tool_calls = response.choices[0].message.tool_calls

            if tool_calls is None:
                return None

            tool_call = tool_calls[0]
            tool_call.arguments = json.loads(tool_call.function.arguments)
            return tool_call

        else:
            return None
