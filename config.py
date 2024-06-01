"""
/src/config.py
設定を管理するモジュール
"""

import os
import json
from dotenv import load_dotenv
from src.logger_setup import get_logger

# ロガーの取得
logger = get_logger(__name__)

default_config = {
    "ticker_interval": 60,
    "trading_interval": 300,
    "prompt_file": "messages.json",
    "bitflyer_api_key": "",
    "bitflyer_api_secret": "",
    "openai_api_key": "",
    "cryptocompare_api_key": "",
    "log_dir": "logs",
    "cache_file": "price_cache.json",
}


class AppConfig:
    """
    設定を管理するクラス
    """

    def __init__(self):
        # 設定用変数とデフォルト値を設定
        self.ticker_interval = 60
        self.trading_interval = 300
        self.prompt_file = "messages.json"

        self.bitflyer_api_key = ""
        self.bitflyer_api_secret = ""
        self.openai_api_key = ""
        self.criptocompare_api_key = ""

        load_dotenv()

        self.log_dir = "logs"
        self.cache_file = "price_cache.json"

        # プロジェクトのルートディレクトリを取得
        self.project_root = os.path.dirname(os.path.abspath(__file__))

    def load(self, config_file_name="config.json"):
        """
        設定ファイルを読み込む
        """

        # .envファイルから環境変数をロード
        self.bitflyer_api_key = os.getenv("BITFLYER_API_KEY")
        self.bitflyer_api_secret = os.getenv("BITFLYER_API_SECRET")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.criptocompare_api_key = os.getenv("CRYPTOCOMPARE_API_KEY")

        # 設定ファイルを読み込む
        try:
            project_root = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(project_root, config_file_name)

            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as file:
                    config = json.load(file)
            else:
                config = default_config
        except (IOError, json.JSONDecodeError) as e:
            logger.error("Failed to load config file: %s", e)
            config = default_config

        # 設定を読み込む
        self.ticker_interval = config.get(
            "ticker_interval",
        )
        self.trading_interval = config.get(
            "trading_interval", default_config["trading_interval"]
        )
        self.prompt_file = config.get(
            "prompt_file", default_config["prompt_file"]
        )
        self.log_dir = config.get("log_dir", default_config["log_dir"])
        self.cache_file = config.get(
            "cache_file", default_config["cache_file"]
        )
