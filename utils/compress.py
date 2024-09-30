from pathlib import Path

from a816.symbols import low_rom_bus

from utils import xba


def compress_blocks(data: bytes) -> bytes:
    compressed = bytearray()
    block_count = len(data) // 32

    for current_block in range(block_count):
        block_data = data[current_block * 32: (current_block + 1) * 32]
        compressed_block = compress_block(block_data)
        compressed += compressed_block
    return compressed


def compress_block(data: bytes):
    compressed = bytearray()

    seed = [0x00, 0x00]
    k = 0
    control_byte, chunk = _compress(data, k, seed)
    compressed.append(control_byte)
    compressed += chunk

    k = 8
    control_byte, chunk = _compress(data, k, seed)
    compressed.append(control_byte)
    compressed += chunk

    seed = [0x00, 0x00]

    k = 16
    control_byte, chunk = _compress(data, k, seed)
    compressed.append(control_byte)
    compressed += chunk

    k = 24
    control_byte, chunk = _compress(data, k, seed)
    compressed.append(control_byte)
    compressed += chunk

    return compressed


def _compress(data, k, seed):
    control_byte = 0x00
    chunk = bytearray()
    for i in range(0, 8):
        current_data = data[k]

        if current_data != seed[0]:
            control_byte |= 1 << (7 - i)
            chunk.append(current_data)
            seed[0] = current_data
        k += 1
        xba(seed)

    return control_byte, chunk


