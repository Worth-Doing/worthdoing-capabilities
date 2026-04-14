"""Embeddings generation capability handler."""

import hashlib
import struct


async def execute(input_data: dict) -> dict:
    text = input_data["text"]
    dimensions = 128

    # Placeholder: generate a deterministic pseudo-embedding from a hash.
    # Replace with a real embeddings API (OpenAI, Cohere, etc.) for production.
    hash_bytes = hashlib.sha512(text.encode("utf-8")).digest()
    # Extend hash to fill the required dimensions
    extended = hash_bytes
    while len(extended) < dimensions * 4:
        extended += hashlib.sha512(extended).digest()

    # Convert bytes to floats in [-1, 1] range
    vector = []
    for i in range(dimensions):
        # Take 4 bytes, convert to unsigned int, normalize to [-1, 1]
        chunk = extended[i * 4 : (i + 1) * 4]
        value = struct.unpack(">I", chunk)[0]
        normalized = (value / (2**32 - 1)) * 2 - 1
        vector.append(round(normalized, 6))

    return {
        "text": text,
        "model": "placeholder-v1",
        "dimensions": dimensions,
        "vector": vector,
    }
