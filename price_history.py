import json
import os
from datetime import datetime
from bitflyer_client import BitflyerClient

class PriceHistory:
    def __init__(self, client, log_dir='logs', cache_file='price_cache.json'):
        self.client = client
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.cache_file = os.path.join(self.log_dir, cache_file)
        self.cache = self._load_cache()
    
    def _load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as file:
                return json.load(file)
        return []
    
    def _save_cache(self):
        with open(self.cache_file, 'w') as file:
            json.dump(self.cache, file, indent=4)
    
    def _get_ticker_data(self, product_code):
        endpoint = '/v1/getticker'
        params = {'product_code': product_code}
        return self.client._make_request('GET', endpoint, params=params)
    
    def get_price_history(self, product_code='BTC_JPY'):
        new_data = self._get_ticker_data(product_code)
        current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        new_data['timestamp'] = current_time
        self.cache.insert(0, new_data)  # 最新のデータをリストの先頭に追加
        if len(self.cache) > 100:
            self.cache.pop()  # 最後の要素を削除
        
        self._save_cache()
        return self.cache
