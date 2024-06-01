"""
Actions
"""

import traceback
from src.logger_setup import get_logger
from src.bitflyer.trading_methods import BitflyerMethods

# from bitflyer_client import BitflyerClient

# ロガーの取得
logger = get_logger(__name__)


class MarketData:
    """
    マーケットデータを取得する
    """

    def __init__(self, bitflyer_client):
        portfolio_info = bitflyer_client.get_balance()
        self.portfolio_data = self.process_currency_data(
            portfolio_info["current_balance"]
        )
        self.portfolio_history = portfolio_info["history"]
        self.execution_data = bitflyer_client.get_execution_history()
        self.open_orders = bitflyer_client.get_open_orders()

    def process_currency_data(self, json_data):
        """
        通貨データを処理する
        """
        for entry in json_data:
            # availableの値を5%減算
            entry["available"] = entry["available"] * 0.95

            # JPYの値を整数値にする
            if entry["currency_code"] == "JPY":
                entry["amount"] = int(entry["amount"])
                entry["available"] = int(entry["available"])

            # BTCのamountとavailableの値を小数点以下8位までにする
            elif entry["currency_code"] == "BTC":
                entry["amount"] = round(entry["amount"], 8)
                entry["available"] = round(entry["available"], 8)

        return json_data


class Actions:
    """
    注文を実行する
    """

    def __init__(self, config):

        self.bitflyer_client = BitflyerMethods(config)

        self.portfolio_info = {}
        self.portfolio_data = []
        self.portfolio_history = []

    def get_market_data(self):
        """
        マーケットデータを取得する
        """
        data = MarketData(self.bitflyer_client)
        return data

    def get_board_state(self):
        """
        板の状態を取得する
        """
        return self.bitflyer_client.get_board_state()

    def execute_order(self, function_call):
        """
        注文を実行する
        """

        try:
            params = function_call.arguments
            side = params["side"]
            price = params.get("price", None)
            size = params["size"]
            order_type = params["order_type"]
            time_in_force = params.get("time_in_force", None)

            # ログに出力
            logger.info(
                "[order] Trading decision: %s / price: %.8f / "
                "size: %.8f / order_type: %s / time_in_force: %s",
                side,
                price,
                size,
                order_type,
                time_in_force,
            )

            # 引数のチェック
            if size < 0.0001:
                logger.info(
                    "Order size %s is below the minimum threshold. "
                    "Order not executed.",
                    size,
                )
                return

            # 数値を通常の小数点表記に変換
            price = float(f"{price:.8f}")
            size = float(f"{size:.8f}")

            self.bitflyer_client.send_order(
                "BTC_JPY", side, size, order_type, time_in_force, price
            )
        except Exception as inner_exception:
            logger.error("Failed to execute order: %s", inner_exception)
            raise

    # 注文のキャンセル
    def cancel_order(self, function_call):
        """
        オーダーをキャンセルする
        """
        try:
            params = function_call.arguments
            order_id = params["order_id"]

            logger.info("[cancel] Cancel order: %s", order_id)

            self.bitflyer_client.cancel_order(order_id)
        except Exception:
            logger.error("Failed to cancel order: %s", traceback.format_exc())
            raise
