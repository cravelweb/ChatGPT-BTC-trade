"""
Trading Signals
"""

import numpy as np
import pandas as pd
import requests


class TradingSignals:
    """
    価格データから売買シグナルを生成する
    """

    def __init__(self, config):
        self.api_key = config.criptocompare_api_key
        self.df = None

    def fetch_data(self, symbol="BTC", currency="JPY", limit=1000):
        """
        指定された通貨ペアの価格データを取得する
        """
        url = "https://min-api.cryptocompare.com/data/v2/histominute"
        params = {
            "fsym": symbol,
            "tsym": currency,
            "limit": limit,
            "api_key": self.api_key,
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data["Response"] != "Success":
            raise Exception(f"Failed to fetch data: {data['Message']}")

        return data["Data"]["Data"]

    def load_data(self, symbol="BTC", currency="JPY", limit=1000):
        """
        データを取得してデータフレームに変換し、5分足にリサンプリングする
        """
        data_list = self.fetch_data(symbol, currency, limit)

        # データフレームに変換
        self.df = pd.DataFrame(data_list)
        self.df["timestamp"] = pd.to_datetime(self.df["time"], unit="s")
        self.df = self.df.set_index("timestamp")
        self.df = self.df.sort_index()

        # 5分足にリサンプリング
        self.df = (
            self.df.resample("5min")
            .agg(
                {
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volumefrom": "sum",
                }
            )
            .dropna()
        )

        # timestampを再設定
        self.df = self.df.reset_index()

    def calculate_signals(self):
        """
        移動平均を計算してシグナルを生成する
        """
        if self.df is None:
            raise ValueError("Data not loaded. Please run load_data() first.")

        # 移動平均の計算
        self.df["Short_MA"] = (
            self.df["close"].rolling(window=5).mean()
        )  # 短期移動平均（5期間）
        self.df["Long_MA"] = (
            self.df["close"].rolling(window=50).mean()
        )  # 長期移動平均（50期間）
        self.df["Signal"] = np.where(
            self.df["Short_MA"] > self.df["Long_MA"], 1, -1
        )  # シグナルの生成

        # RSIの計算
        delta = self.df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.df["RSI"] = 100 - (100 / (1 + rs))

        # MACDの計算
        self.df["EMA12"] = self.df["close"].ewm(span=12, adjust=False).mean()
        self.df["EMA26"] = self.df["close"].ewm(span=26, adjust=False).mean()
        self.df["MACD"] = self.df["EMA12"] - self.df["EMA26"]
        self.df["Signal_Line"] = (
            self.df["MACD"].ewm(span=9, adjust=False).mean()
        )

        # ボリンジャーバンドの計算
        self.df["BB_Mid"] = self.df["close"].rolling(window=20).mean()
        self.df["BB_Upper"] = (
            self.df["BB_Mid"] + 2 * self.df["close"].rolling(window=20).std()
        )
        self.df["BB_Lower"] = (
            self.df["BB_Mid"] - 2 * self.df["close"].rolling(window=20).std()
        )

    def get_signals(self):
        """
        シグナルを返す
        """
        if self.df is None:
            raise ValueError("Data not loaded. Please run load_data() first.")

        self.calculate_signals()
        # 最新の50期間分のデータを返す
        return (
            self.df[
                [
                    "timestamp",
                    "close",
                    "Short_MA",
                    "Long_MA",
                    "Signal",
                    "RSI",
                    "MACD",
                    "Signal_Line",
                    "BB_Upper",
                    "BB_Mid",
                    "BB_Lower",
                ]
            ]
            .dropna()
            .tail(50)
        )
