from .broadkast_pb2 import (
    KubeConfigUpdate,
    KubeConfigUpdateResponse,
    ServiceDiscoveryRequest,
    ServiceDiscoveryResponse,
    SelectorQuery,
    DiscoveredService
)


from .broadkast_pb2_grpc import (
    BroadkastServerServicer,
    BroadkastServerStub,
    BroadkastServer,
    add_BroadkastServerServicer_to_server
)