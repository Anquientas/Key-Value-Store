import grpc

from kvstore.constants import ServicerErrorMessage
from kvstore.generated import kvstore_pb2, kvstore_pb2_grpc
from kvstore.storage import LRUTTLStore


class KeyValueStoreServicer(kvstore_pb2_grpc.KeyValueStoreServicer):
    def __init__(self, store: LRUTTLStore) -> None:
        self._store = store

    async def Put(
        self,
        request: kvstore_pb2.PutRequest,
        context: grpc.aio.ServicerContext,
    ) -> kvstore_pb2.PutResponse:
        await self._store.put(request.key, request.value, request.ttl_seconds)
        return kvstore_pb2.PutResponse()

    async def Get(
        self,
        request: kvstore_pb2.GetRequest,
        context: grpc.aio.ServicerContext
    ) -> kvstore_pb2.GetResponse:
        value = await self._store.get(request.key)
        if value is None:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                ServicerErrorMessage.key_not_found.format(key=request.key),
            )
        return kvstore_pb2.GetResponse(value=value)

    async def Delete(
        self,
        request: kvstore_pb2.DeleteRequest,
        context: grpc.aio.ServicerContext
    ) -> kvstore_pb2.DeleteResponse:
        await self._store.delete(request.key)
        return kvstore_pb2.DeleteResponse()

    async def List(
        self,
        request: kvstore_pb2.ListRequest,
        context: grpc.aio.ServicerContext
    ) -> kvstore_pb2.ListResponse:
        items = await self._store.list_by_prefix(request.prefix)
        return kvstore_pb2.ListResponse(
            items=[
                kvstore_pb2.KeyValue(key=key, value=value)
                for key, value in items
            ]
        )
