from bitflyer_client import BitflyerClient

class OrderBook:
    def __init__(self, client):
        self.client = client

    def get_order_book(self, product_code='BTC_JPY'):
        endpoint = '/v1/getboard'
        params = {'product_code': product_code}
        return self.client._make_request('GET', endpoint, params=params)
