from ast import In
from typing import List
from .instance import Instance


class InstancePortsCollection:

    def __init__(self, key: str) -> None:
        self.key = key
        self.ports = {}

    def __iter__(self) -> str:
        for port in self.ports:
            yield port

    def __getitem__(self, port) -> List[Instance]:
        return self.ports.get(port, [])

    async def append_instance(self, port: str, instance: Instance) -> None:
        instances = self.ports.get(port, {})
        instances[instance.address] = instance

        self.ports[port] = instances

    async def addresses(self, port: str) -> List[str]:
        ports = self.ports.get(port)
        if ports is None:
            return ports

        return ports.keys()

    async def all(self) -> List[str]:
        instances = []
        
        for port in self.ports:
            instance_addresses = self.ports[port].keys()
            instances = [
                *instances,
                *instance_addresses
            ]
        
        return instances