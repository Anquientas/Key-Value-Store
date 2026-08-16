from enum import StrEnum


class ServerLogMessage(StrEnum):
    started = 'KeyValueStore gRPC-сервер запущен на %s (LRU capacity=%d)'
    shutdown_requested = (
        'Получен сигнал остановки, завершаем текущие запросы...'
    )
    stopped = 'Сервер остановлен'


class ServicerErrorMessage(StrEnum):
    key_not_found = 'Ключ {key!r} не найден или срок его действия истек'


class StorageErrorMessage(StrEnum):
    invalid_capacity = (
        'Емкость должна быть положительным целым числом,'
        ' получено {capacity!r}'
    )
