set -euo pipefail

cd "$(dirname "$0")/.."

python -m grpc_tools.protoc \
  -I proto \
  --python_out=kvstore/generated \
  --grpc_python_out=kvstore/generated \
  --pyi_out=kvstore/generated \
  proto/kvstore.proto

sed -i 's/^import kvstore_pb2 as kvstore__pb2$/from . import kvstore_pb2 as kvstore__pb2/' \
  kvstore/generated/kvstore_pb2_grpc.py

echo "Готово: kvstore/generated/kvstore_pb2.py, kvstore_pb2_grpc.py, kvstore_pb2.pyi"