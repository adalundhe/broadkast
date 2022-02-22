import uuid


class ServiceInstance:

    def __init__(self, instance_address) -> None:
        self.instance_address = instance_address
        self.instance_id = uuid.uuid4()
