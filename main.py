"""
main.py
"""

import time
import traceback

from config import AppConfig
from src.logger_setup import get_logger
from src.custom_errors import APIError
from src.actions import Actions
from src.cryptocompare.trading_signals import TradingSignals
from src.openai.trading_decision import TradingDecision

# ロガーの取得
logger = get_logger(__name__)

# 設定の初期化
config = AppConfig()
config.load("config.json")

# 注文処理の初期化
actions = Actions(config)

signals = TradingSignals(config)

# OpenAI売買判断モジュールの初期化
decision_maker = TradingDecision(config)


def perform_trading_actions(decision):
    """
    売買判断に基づいて注文を実行する
    """
    if hasattr(decision, "type") and decision.type == "function":
        function_name = decision.function.name

        if function_name == "order":
            # 注文を実行
            actions.execute_order(decision)

        elif function_name == "cancel":
            # 注文をキャンセル
            actions.cancel_order(decision)

        elif function_name == "cancel_and_order":
            # 注文をキャンセルしてから再度注文
            actions.cancel_order(decision)
            time.sleep(3)
            actions.execute_order(decision)

        elif function_name == "hold":
            logger.info("[hold] Hold position: %s", function_name)


def handle_trading_decision():
    """
    売買判断を行う
    """

    # マーケットデータを取得
    market_data = actions.get_market_data()

    # 価格とシグナルのデータを取得
    signals.load_data()
    signal_list = signals.get_signals()

    # print(signal_list)

    # OpenAIを使った売買判断
    # decision = None
    decision = decision_maker.get_trading_decision(
        signal_list,
        market_data.ticker_data,
        market_data.portfolio_data,
        market_data.open_orders,
        market_data.execution_data,
    )

    # ログに出力
    logger.info(
        "Balance: JPY %s / BTC %s",
        market_data.portfolio_data[0]["available"],
        market_data.portfolio_data[1]["available"],
    )

    if not decision:
        logger.info("[hold] No decision data returned")
    else:
        perform_trading_actions(decision)


def main():
    """
    メイン関数
    """

    # 変数の初期化
    error_count = 0
    max_errors = 3

    logger.info("Starting trading bot...")
    logger.info(
        "Trading interval: %s minutes", int(config.trading_interval / 60)
    )

    while True:
        try:
            # 最新の板のステータスをチェック
            board_state = actions.get_board_state()["state"]

            if board_state != "RUNNING":
                # 板のステータスがRUNNINGでない場合は売買判断をスキップ
                logger.info("Decision Skiped : %s", board_state)
            else:
                # 一定時間ごとに売買判断を行う
                handle_trading_decision()

            # スリープ
            time.sleep(config.trading_interval)

        except APIError as api_error:
            logger.error("API error occurred: %s", api_error)
            error_count += 1

            if error_count >= max_errors:
                logger.error("Maximum number of consecutive errors reached.")
                break
            else:
                # エラーが発生した場合でも次の試行まで待機
                time.sleep(config.trading_interval)
        except Exception as e:
            logger.error("An error occurred: %s", e)
            logger.error(traceback.format_exc())
            error_count += 1

            if error_count >= max_errors:
                logger.error("Maximum number of consecutive errors reached.")
                break
            else:
                # エラーが発生した場合でも次の試行まで待機
                time.sleep(config.trading_interval)


if __name__ == "__main__":
    main()
