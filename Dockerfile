FROM python:3.13.3 AS builder

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir grpcio grpcio-tools

COPY proto ./proto
COPY scripts ./scripts

RUN mkdir -p kvstore/generated && touch kvstore/generated/__init__.py \
    && bash scripts/generate_proto.sh

FROM python:3.13.3

WORKDIR /app

RUN pip install --no-cache-dir grpcio protobuf

COPY --from=builder /app/kvstore/generated ./kvstore/generated
COPY kvstore ./kvstore

EXPOSE 8000

CMD ["python", "-m", "kvstore.server"]