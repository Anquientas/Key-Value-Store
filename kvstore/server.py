import asyncio
import logging
import signal

import grpc

from kvstore.constants import ServerLogMessage
from kvstore.generated import kvstore_pb2_grpc
from kvstore.servicer import KeyValueStoreServicer
from kvstore.settings import settings
from kvstore.storage import LRUTTLStore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)


async def serve() -> None:
    store = LRUTTLStore(capacity=settings.LRU_CAPACITY)
    server = grpc.aio.server()
    kvstore_pb2_grpc.add_KeyValueStoreServicer_to_server(
        KeyValueStoreServicer(store), server
    )
    listen_address = f'{settings.HOST}:{settings.PORT}'
    server.add_insecure_port(listen_address)

    await server.start()
    logger.info(
        ServerLogMessage.started, listen_address, settings.LRU_CAPACITY
    )

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()
    logger.info(ServerLogMessage.shutdown_requested)
    await server.stop(grace=settings.SHUTDOWN_GRACE_SECONDS)
    logger.info(ServerLogMessage.stopped)


if __name__ == '__main__':
    asyncio.run(serve())
