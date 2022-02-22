from .discovered_service import DiscoveredService


class DiscoveredRegistry:

    def __init__(self) -> None:
        self.discovered = {}

    def __iter__(self):
        for service in self.discovered.values():
            yield service
            
    def __getitem__(self, service_name):
        return self.discovered.get(service_name)

    async def register_instance(self, service_name, instance_address):
        
        if service_name not in self.discovered:
            self.discovered[service_name] = DiscoveredService(service_name)   

        await self.discovered[service_name].register_instance(instance_address) 
            
