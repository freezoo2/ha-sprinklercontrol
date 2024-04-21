import requests
class SprinklerControl(object):
    def __init__(self, ipaddress: str):
        self.ip = ipaddress

    def start(self, seconds: int):
        url = f"http://{self.ip}/api/v1/sprinkler"
        data = {"seconds": seconds}
        resp = requests.post(url, json=data)
        resp.raise_for_status()

    def current_state(self):
        url = f"http://{self.ip}/api/v1/sprinkler"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()['state']
