from bitflyer_client import BitflyerClient

class ExecutionHistory:
    def __init__(self, client):
        self.client = client
    
    def get_execution_history(self, count=15):
        endpoint = '/v1/me/getexecutions'
        params = {'count': count}
        return self.client._make_request('GET', endpoint, params=params)
