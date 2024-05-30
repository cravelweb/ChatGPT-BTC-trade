# trading.py

from bitflyer_client import BitflyerClient

# トレード関連のAPIを呼び出すクラス
class Trading:
    def __init__(self, client):
        self.client = client

    # 注文を送信する
    def send_order(self, product_code, side, price, size, order_type='LIMIT', trigger_price=None):
        """
        Send an order.

        Args:
            product_code (str): The product code.
            side (str): The side of the order ('BUY' or 'SELL').
            price (float): The price of the order.
            size (float): The size of the order.
            order_type (str, optional): The type of the order. Defaults to 'LIMIT'.
            trigger_price (float, optional): The trigger price for 'STOP' orders. Required if order_type is 'STOP'.

        Returns:
            dict: The response from the API.
        """
        if order_type == 'STOP' and trigger_price is None:
            raise ValueError("trigger_price is required for STOP orders")

        endpoint = '/v1/me/sendchildorder'
        body = {
            'product_code': product_code,
            'child_order_type': order_type,
            'side': side,
            'price': price,
            'size': size,
            'minute_to_expire': 10000,
            'time_in_force': 'GTC'
        }
        if order_type == 'STOP':
            body['trigger_price'] = trigger_price
        
        try:
            return self.client._make_request('POST', endpoint, data=body)
        except Exception as e:
            print(f"Failed to send order: {e}")
            return None
    
    # 未約定の注文を取得する
    def get_open_orders(self, product_code='BTC_JPY'):
        endpoint = '/v1/me/getchildorders'
        params = {'product_code': product_code, 'child_order_state': 'ACTIVE'}
        return self.client._make_request('GET', endpoint, params=params)
    
    # 注文をキャンセルする
    def cancel_order(self, order_id, product_code='BTC_JPY'):
        endpoint = '/v1/me/cancelchildorder'
        body = {'product_code': product_code, 'child_order_acceptance_id': order_id}
        return self.client._make_request('POST', endpoint, data=body)
