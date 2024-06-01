"""
API Client for bitFlyer
"""

import json
import hmac
import hashlib
import time
import requests
from src.custom_errors import APIError


class BitflyerClient:
    """
    bitFlyerのAPIクライアント
    """

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.bitflyer.jp"

    def make_request(self, method, endpoint, params=None, data=None):
        """
        APIリクエストを送信する
        """
        url = f"{self.base_url}{endpoint}"
        timestamp = str(int(time.time()))
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint_with_query = f"{endpoint}?{query_string}"
        else:
            query_string = ""
            endpoint_with_query = endpoint
        body = json.dumps(data) if data else ""
        text = timestamp + method + endpoint_with_query + body
        sign = hmac.new(
            self.api_secret.encode("utf-8"),
            text.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "ACCESS-KEY": self.api_key,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-SIGN": sign,
            "Content-Type": "application/json",
        }

        response = requests.request(
            method, url, headers=headers, params=params, data=body, timeout=10
        )

        if response.status_code != 200:
            raise APIError(
                "API request error: "
                f"method={method}, "
                f"endpoint={endpoint}, "
                f"params={params}, "
                f"data={data}, "
                f"status_code={response.status_code}, "
                f"reason={response.reason}, "
                f"content={response.text}"
            )

        if response.text:
            return response.json()
        else:
            return None
