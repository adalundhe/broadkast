import grpc
import uvloop
uvloop.install()
from easy_logger import Logger
from .service import BroadkastServicer
from .proto import(
    add_BroadkastServerServicer_to_server
)


class BroadkastServer:

    def __init__(self, config: dict={}) -> None:
        logger = Logger()
        logger.setup('info')
        self.session_logger = logger.generate_logger()

        self.replicas = config.get('broadkast_server_replicas', 1) 

        self.server = grpc.aio.server()
        self.service = BroadkastServicer(config)
        add_BroadkastServerServicer_to_server(
            self.service,
            self.server
        )

        self.port = self.service.broadkast_server_port
        
        server_address = f'[::]:{self.port}'
        self.server.add_insecure_port(server_address)
        self.running = False

    async def start(self):
        self.session_logger.info(f'\nStarting Broadkast server on port - {self.port}.\n')
        await self.server.start()
        self.running = True

        if self.replicas > 1:
            await self.service.discover_replicas()

    async def wait(self):
        self.session_logger.info(f'Starting Broadkast running on port - {self.port}.\n')
        await self.server.wait_for_termination()
            

    async def stop(self):
        self.session_logger.info('Shutting down Broadkast server..')
        if self.running:
            self.running = False
            await self.server.stop(0)

            self.session_logger.info('Shutdown complete, goodbye!')
    