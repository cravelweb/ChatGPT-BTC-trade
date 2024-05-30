import os
import json
from datetime import datetime
from bitflyer_client import BitflyerClient

class Portfolio:
    def __init__(self, client, log_dir='logs'):
        self.client = client
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _get_log_file(self):
        current_date = datetime.utcnow().strftime('%Y%m%d')
        return os.path.join(self.log_dir, f'portfolio_{current_date}.json')

    def _rotate_logs(self):
        current_date = datetime.utcnow().strftime('%Y%m%d')
        for filename in os.listdir(self.log_dir):
            if filename.startswith('portfolio_') and not filename.endswith(f'{current_date}.json'):
                os.remove(os.path.join(self.log_dir, filename))

    def get_balance(self):
        endpoint = '/v1/me/getbalance'
        balance_data = self.client._make_request('GET', endpoint)

        # JPYとBTCのみを抽出
        balance_data = [balance for balance in balance_data if balance['currency_code'] in ['JPY', 'BTC']]

        # 現在の日時を追加
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        for balance in balance_data:
            balance['timestamp'] = timestamp

        # ログファイルに保存
        log_file = self._get_log_file()
        if os.path.exists(log_file):
            with open(log_file, 'r') as file:
                history = json.load(file)
        else:
            history = []

        history.extend(balance_data)

        with open(log_file, 'w') as file:
            json.dump(history, file, indent=4)

        # ローテーション処理
        self._rotate_logs()

        return {
            "current_balance": balance_data,
            "history": history
        }
    
    def get_trade_history(self):
        endpoint = '/v1/me/getexecutions'
        return self.client._make_request('GET', endpoint)
