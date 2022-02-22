class Instance:

    def __init__(self, key: str, ip: str, port: str) -> None:
        self.key = key
        self.ip = ip
        self.port = port
        self.address = f'{ip}:{port}'

    def __dict__(self) -> dict:
        return {
            'app': self.app,
            'ip': self.ip,
            'port': self.port,
            'address': self.address
        }
