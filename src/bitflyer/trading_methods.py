"""
Trading methods for the Bitflyer API.
"""

import os
import json
from datetime import datetime
import pandas as pd
from src.bitflyer.bitflyer_client import BitflyerClient
from src.logger_setup import get_logger

# from bitflyer_client import BitflyerClient

# ロガーの取得
logger = get_logger(__name__)


class BitflyerMethods:
    """
    A class to interact with the Bitflyer API.
    """

    def __init__(self, config):
        self.api_client = BitflyerClient(
            config.bitflyer_api_key, config.bitflyer_api_secret
        )
        self.log_dir = config.log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.cache_file = os.path.join(self.log_dir, config.cache_file)
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r", encoding="utf-8") as file:
                return json.load(file)
        return []

    def _save_cache(self):
        with open(self.cache_file, "w", encoding="utf-8") as file:
            json.dump(self.cache, file, indent=4)

    def _get_ticker_data(self, product_code):
        endpoint = "/v1/getticker"
        params = {"product_code": product_code}
        return self.api_client.make_request("GET", endpoint, params=params)

    def _get_log_file(self):
        current_date = datetime.utcnow().strftime("%Y%m%d")
        return os.path.join(self.log_dir, f"portfolio_{current_date}.json")

    def _rotate_logs(self):
        current_date = datetime.utcnow().strftime("%Y%m%d")
        for filename in os.listdir(self.log_dir):
            if filename.startswith("portfolio_") and not filename.endswith(
                f"{current_date}.json"
            ):
                os.remove(os.path.join(self.log_dir, filename))

    def get_board_state(self, product_code="BTC_JPY"):
        """
        板の状態を取得する
        """
        endpoint = "/v1/getboardstate"
        params = {"product_code": product_code}
        return self.api_client.make_request("GET", endpoint, params=params)

    def get_balance(self):
        """
        残高を取得する
        """
        endpoint = "/v1/me/getbalance"
        balance_data = self.api_client.make_request("GET", endpoint)

        # JPYとBTCのみを抽出
        balance_data = [
            balance
            for balance in balance_data
            if balance["currency_code"] in ["JPY", "BTC"]
        ]

        # 現在の日時を追加
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        for balance in balance_data:
            balance["timestamp"] = timestamp

        # ログファイルに保存
        log_file = self._get_log_file()
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as file:
                history = json.load(file)
        else:
            history = []

        history.extend(balance_data)

        with open(log_file, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=4)

        # ローテーション処理
        self._rotate_logs()

        return {"current_balance": balance_data, "history": history}

    def get_trade_history(self):
        """
        取引履歴を取得する
        """
        endpoint = "/v1/me/getexecutions"
        return self.api_client.make_request("GET", endpoint)

    def get_execution_history(self, count=15):
        """
        約定履歴を取得する
        """
        endpoint = "/v1/me/getexecutions"
        params = {"count": count}

        # APIリクエストを送信
        response = self.api_client.make_request(
            "GET", endpoint, params=params
        )

        # データフレームに変換
        df = pd.DataFrame(response)

        # 必要な項目のみ抽出
        df = df[["id", "side", "price", "size", "exec_date", "commission"]]

        # 日時型に変換
        df["exec_date"] = pd.to_datetime(df["exec_date"])

        # print(df)
        return df

    # 注文を送信する
    def send_order(
        self,
        product_code,
        side,
        size,
        order_type,
        time_in_force="GTC",
        price=None,
    ):
        """
        Send an order.
        """

        # 注文データが不十分の場合処理を中断する
        if not product_code or not side or not size or not order_type:
            logger.warning("Invalid order: missing required parameters")
            return None
        if order_type == "LIMIT" and not price:
            logger.warning(
                "Invalid order: price is required for LIMIT orders"
            )
            return None

        endpoint = "/v1/me/sendchildorder"
        body = {
            "product_code": product_code,
            "child_order_type": order_type,
            "side": side,
            "size": size,
            "minute_to_expire": 30,
            "time_in_force": time_in_force,
        }
        if order_type == "LIMIT":
            body["price"] = price

        try:
            return self.api_client.make_request("POST", endpoint, data=body)
        except Exception as e:
            print(f"Failed to send order: {e}")
            return None

    def get_open_orders(self, product_code="BTC_JPY"):
        """
        未約定の注文を取得する
        """
        endpoint = "/v1/me/getchildorders"
        params = {"product_code": product_code, "child_order_state": "ACTIVE"}
        return self.api_client.make_request("GET", endpoint, params=params)

    def cancel_order(self, order_id, product_code="BTC_JPY"):
        """
        注文をキャンセルする
        """
        endpoint = "/v1/me/cancelchildorder"
        body = {
            "product_code": product_code,
            "child_order_acceptance_id": order_id,
        }
        return self.api_client.make_request("POST", endpoint, data=body)
