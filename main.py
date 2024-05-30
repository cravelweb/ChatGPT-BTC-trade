# main.py
import time
import os
import traceback
import json
from dotenv import load_dotenv
from bitflyer_client import BitflyerClient
from price_history import PriceHistory
from trading import Trading
from portfolio import Portfolio
from order_book import OrderBook
from trading_decision import TradingDecision
from execution_history import ExecutionHistory
from logger_setup import get_logger

# ロガーの取得
logger = get_logger(__name__)

# .envファイルから環境変数をロード
load_dotenv()

# APIキーとシークレットキーを環境変数から取得
bitflyer_api_key = os.getenv('BITFLYER_API_KEY')
bitflyer_api_secret = os.getenv('BITFLYER_API_SECRET')
openai_api_key = os.getenv('OPENAI_API_KEY')

# クライアントの初期化
client = BitflyerClient(bitflyer_api_key, bitflyer_api_secret)

# 各モジュールの初期化
price_history = PriceHistory(client)
trading = Trading(client)
portfolio = Portfolio(client)
execution_history = ExecutionHistory(client)
order_book = OrderBook(client)
decision_maker = TradingDecision(openai_api_key)



# 注文の実行
def execute_order(function_call):
    try:
        params = function_call.arguments
        side = params['side']
        price = params['price']
        size = params['size']
        order_type = params['order_type']
        trigger_price = params.get('trigger_price')

        # 引数のチェック
        if size < 0.0001:
            logger.info(f"Order size {size} is below the minimum threshold. Order not executed.")
            return

        # 数値を通常の小数点表記に変換
        price = float(f"{price:.8f}")
        size = float(f"{size:.8f}")

        if order_type == 'LIMIT':
            trading.send_order('BTC_JPY', side, price, size, order_type)
        elif order_type == 'STOP':
            trading.send_order('BTC_JPY', side, price, size, order_type, trigger_price)
    except Exception as e:
        logger.error(f"Failed to execute order: {e}")
        raise



# 注文のキャンセル
def cancel_order(function_call):
    try:
        params = function_call.arguments
        order_id = params['order_id']

        trading.cancel_order(order_id)
    except Exception as e:
        logger.error(f"Failed to cancel order: {e}")
        raise


# エラーカウントの初期化
error_count = 0
max_errors = 3


# メインループ
ticker_interval = 60  # ティッカーの取得間隔（秒）
trading_interval = 300  # 売買判断の間隔（秒）
last_trading_time = 0
while True:
    try:
        current_time = time.time()
        
        # 価格履歴の取得（ティッカー）
        market_data = price_history.get_price_history()
        
        # 1分ごとにティッカーを取得
        logger.info(f"Market Data Updated")

        # 最新の板のステータスをチェック
        latest_state = market_data[0].get('state') if market_data else None
        if latest_state != 'RUNNING':
            logger.info(f"Market state is {latest_state}. Skipping trading decision.")
        else:
            # 5分ごとに売買判断を実行
            if current_time - last_trading_time >= trading_interval:
                last_trading_time = current_time

                # ポートフォリオの取得
                portfolio_info = portfolio.get_balance()
                portfolio_data = portfolio_info["current_balance"]
                portfolio_history = portfolio_info["history"]

                # 約定履歴の取得
                execution_data = execution_history.get_execution_history()

                # 注文データの取得
                open_orders_pre = trading.get_open_orders()
                order_data = {"open_orders": open_orders_pre}

                # 板情報の取得
                order_book_data = order_book.get_order_book()

                # OpenAIを使った売買判断
                decision = decision_maker.get_trading_decision(market_data, portfolio_data, order_data, execution_data, order_book_data)

                # ログに出力
                logger.info(f"Balance: JPY {portfolio_data[0]['available']} / BTC {portfolio_data[1]['available']}")
                if open_orders_pre:
                    order_ids = [order['child_order_id'] for order in open_orders_pre]
                    logger.info(f"Open Orders: {order_ids}")

                if decision is None:
                    logger.info("Trading decision: HOLD / WAIT")
                else:
                    # 関数呼び出しが含まれている場合の処理
                    if hasattr(decision, 'type') and decision.type == 'function':
                        function_name = decision.function.name
                        arguments = json.loads(decision.function.arguments)

                        if function_name == 'order_method':
                            logger.info(f"Trading decision: {arguments['side']} / price: {arguments['price']:.8f} / size: {arguments['size']:.8f} / order_type: {arguments['order_type']}")
                            execute_order(decision)
                        elif function_name == 'order_cancel':
                            logger.info(f"Cancel order: {arguments['order_id']}")
                            cancel_order(decision)

                # 注文状況の確認
                open_orders_after = trading.get_open_orders()
                if open_orders_after != open_orders_pre:
                    logger.info(f"Open Orders: {open_orders_after}")

                # エラーカウントをリセット
                error_count = 0

        # 1分間スリープ
        time.sleep(ticker_interval)
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.error(traceback.format_exc())
        error_count += 1
        
        if error_count >= max_errors:
            logger.error("Maximum number of consecutive errors reached. Exiting program.")
            break
        else:
            # エラーが発生した場合でも次の試行まで待機
            time.sleep(ticker_interval)