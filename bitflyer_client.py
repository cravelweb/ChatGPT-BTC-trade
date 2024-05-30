# bitflyer_client.py
import requests
import json
import hmac
import hashlib
import time

class BitflyerClient:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = 'https://api.bitflyer.jp'

    def _make_request(self, method, endpoint, params=None, data=None):
        url = f"{self.base_url}{endpoint}"
        timestamp = str(int(time.time()))
        if params:
            query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
            endpoint_with_query = f"{endpoint}?{query_string}"
        else:
            query_string = ''
            endpoint_with_query = endpoint
        body = json.dumps(data) if data else ''
        text = timestamp + method + endpoint_with_query + body
        sign = hmac.new(self.api_secret.encode('utf-8'), text.encode('utf-8'), hashlib.sha256).hexdigest()
        
        headers = {
            'ACCESS-KEY': self.api_key,
            'ACCESS-TIMESTAMP': timestamp,
            'ACCESS-SIGN': sign,
            'Content-Type': 'application/json'
        }
        
        response = requests.request(method, url, headers=headers, params=params, data=body)
        
        if response.status_code != 200:
            raise Exception(f"API request error: {response.status_code}, {response.text}")
        
        return response.json()