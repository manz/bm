import io
from typing import BinaryIO

from utils import xba
from utils.decompress import UnknownCompressionType


def compress_tiles(compression_type: int, data: bytes) -> bytes:
    match compression_type:
        case 0:
            return compress_blocks(data)
        case 2:
            return compress_blocks_2(data)
        case _:
            raise UnknownCompressionType(compression_type)


def compress_blocks(data: bytes) -> bytes:
    compressed = bytearray()
    block_count = len(data) // 32
    data_reader = io.BytesIO(data)

    for _ in range(block_count):
        compressed_block = compress_block(data_reader)
        compressed += compressed_block
    return compressed


def compress_block(data: BinaryIO) -> bytes:
    compressed = bytearray()

    seed = [0x00, 0x00]

    control_byte, chunk = _compress(data, seed)
    compressed.append(control_byte)
    compressed += chunk

    control_byte, chunk = _compress(data, seed)
    compressed.append(control_byte)
    compressed += chunk

    seed = [0x00, 0x00]

    control_byte, chunk = _compress(data, seed)
    compressed.append(control_byte)
    compressed += chunk

    control_byte, chunk = _compress(data, seed)
    compressed.append(control_byte)
    compressed += chunk

    return compressed


def _compress(data: BinaryIO, seed: list[int]) -> tuple[int, bytes]:
    control_byte = 0x00
    chunk = bytearray()
    for i in range(0, 8):
        current_data = ord(data.read(1))

        if current_data != seed[0]:
            control_byte |= 1 << (7 - i)
            chunk.append(current_data)
            seed[0] = current_data

        xba(seed)

    return control_byte, chunk


def compress_blocks_2(data: bytes) -> bytes:
    compressed = bytearray()
    block_count = len(data) // 32
    data_reader = io.BytesIO(data)

    for _ in range(block_count):
        compressed_block = compress_block_2(data_reader)
        compressed += compressed_block
    return compressed


def compress_block_2(data: BinaryIO) -> bytes:
    compressed = bytearray()

    seed = [0x00, 0x00]

    control_byte, chunk = _compress(data, seed)
    compressed.append(control_byte)
    compressed += chunk

    control_byte, chunk = _compress(data, seed)
    compressed.append(control_byte)
    compressed += chunk

    control_byte, chunk = _compress_16(data)
    compressed.append(control_byte)
    compressed += chunk

    return compressed


def _compress_16(data: BinaryIO) -> tuple[int, bytes]:
    control_byte = 0x00
    current_byte = 0
    chunk = bytearray()
    for i in range(0, 8):
        current_data = ord(data.read(1))
        _ = data.read(1)
        if current_data != current_byte:
            control_byte |= 1 << (7 - i)
            current_byte = current_data
            chunk.append(current_byte)

    return control_byte, chunk


def compress_tile_map(data: bytes) -> bytearray:
    compressed = bytearray()

    k = 0

    block = 0
    current_b1 = 0
    current_b2 = 0

    while k < len(data):
        if block % 8 == 0:
            current_b1 = 0
            current_b2 = 0
        chunk = bytearray()
        control_byte = 0
        i = 0
        for _ in range(0, 4):
            b1 = data[k]
            if b1 != current_b1:
                control_byte |= 1 << (7 - i)
                chunk.append(b1)
                current_b1 = b1
            k += 1
            i += 1

            b2 = data[k]
            if b2 != current_b2:
                control_byte |= 1 << (7 - i)
                chunk.append(b2)
                current_b2 = b2
            k += 1
            i += 1

        compressed.append(control_byte)
        compressed += chunk

        block += 1

    return compressed
