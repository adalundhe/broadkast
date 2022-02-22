from .discovered_instance import ServiceInstance


class DiscoveredService:

    def __init__(self, service_name) -> None:
        self.service_name = service_name
        self.instances = {}

    def __iter__(self):
        for instance in self.instances.values():
            yield instance
        
    async def register_instance(self, instance_address):

        if instance_address not in self.instances:
            self.instances[instance_address] = ServiceInstance(instance_address)