import logging
from typing import BinaryIO

from utils import xba

logger = logging.getLogger()


class UnknownCompressionType(Exception):
    """Exception raised when the compression type is unknown."""


def decompress_tiles(
    compression_type: int, data: BinaryIO, block_count: int
) -> tuple[bytearray, int]:
    match compression_type:
        case 0:
            return decompress_blocks(data, block_count)
        case 2:
            return decompress_blocks_2(data, block_count)
        case _:
            raise UnknownCompressionType(compression_type)


def decompress_blocks(data: BinaryIO, block_count: int) -> tuple[bytearray, int]:
    y = 0

    decompressed = bytearray()

    for _ in range(0, block_count):
        seed = [0x00, 0x00]
        b0 = decompress_block(data, seed)
        b1 = decompress_block(data, seed)

        seed = [0x00, 0x00]
        b2 = decompress_block(data, seed)
        b3 = decompress_block(data, seed)

        decompressed += b0[0]
        decompressed += b1[0]
        decompressed += b2[0]
        decompressed += b3[0]

        y += b0[1] + b1[1] + b2[1] + b3[1]

    return decompressed, y


def decompress_block(data: BinaryIO, accumulator: list[int]) -> tuple[bytearray, int]:
    chunk = bytearray()

    control_byte = ord(data.read(1))
    size = 1

    for _ in range(8):
        if control_byte & 0x80:
            accumulator[0] = ord(data.read(1))
            size += 1

        chunk.append(accumulator[0])
        xba(accumulator)
        control_byte = (control_byte << 1) & 0xFF

    return chunk, size


def decompress_blocks_2(data: BinaryIO, block_count: int) -> tuple[bytearray, int]:
    y = 0

    decompressed = bytearray()

    for _ in range(0, block_count):
        seed = [0x00, 0x00]
        b0 = decompress_block(data, seed)
        b1 = decompress_block(data, seed)
        b2 = decompress_block_16(data)

        decompressed += b0[0]
        decompressed += b1[0]
        decompressed += b2[0]

        y += b0[1] + b1[1] + b2[1]

    return decompressed, y


def decompress_block_16(data: BinaryIO) -> tuple[bytearray, int]:
    chunk = bytearray()

    control_byte = ord(data.read(1))
    size = 1

    current_byte = 0

    for _ in range(8):
        if control_byte & 0x80:
            current_byte = ord(data.read(1))
            size += 1

        chunk.append(current_byte)
        chunk.append(0)

        control_byte = (control_byte << 1) & 0xFF

    return chunk, size


def decompress_blocks_secret(data: BinaryIO, block_count: int) -> tuple[bytearray, int]:
    y = 0

    decompressed = bytearray()
    accumulator = [0x00, 0x00]

    for current_block in range(0, block_count * 4):
        print(hex(data.tell()))
        # if current_block > 0 and current_block & 3 == 0:
        #     ignore = data.read(0x0025)
        #     print("jump" + hex(data.tell()))
        #
        #     ...

        control_byte = ord(data.read(1))
        if current_block & 1 == 0:
            accumulator = [0x00, 0x00]
        y += 1

        for _ in range(8):
            if control_byte & 0x80:
                accumulator[0] = ord(data.read(1))
                y += 1

            decompressed.append(accumulator[0])
            xba(accumulator)
            control_byte = (control_byte << 1) & 0xFF

    return decompressed, y


def decompress_tile_map(data: BinaryIO, block_count: int) -> tuple[bytearray, int]:
    decompressed = bytearray()
    # print("-" * 80)
    # print("- Decompression Run -")

    y = 0
    current_b1 = 0
    current_b2 = 0

    for _ in range(0, block_count):
        for _ in range(8):
            control_byte = ord(data.read(1))
            # print(f"{control_byte:02x} -> {control_byte:08b}")
            y += 1
            for _ in range(4):
                if control_byte & 0x80:
                    current_b1 = ord(data.read(1))
                    y += 1

                control_byte = (control_byte << 1) & 0xFF

                if control_byte & 0x80:
                    current_b2 = ord(data.read(1))
                    y += 1

                control_byte = (control_byte << 1) & 0xFF

                decompressed.append(current_b1)
                decompressed.append(current_b2)

    return decompressed, y


def decompress_tile_map2(data: BinaryIO, block_count: int) -> tuple[bytearray, int]:
    decompressed = bytearray()

    y = 0
    current_b1 = 0
    current_b2 = 0

    for _ in range(0, block_count):
        control_byte = ord(data.read(1))
        y += 1
        for _ in range(4):
            if control_byte & 0x80:
                current_b1 = ord(data.read(1))
                y += 1

            control_byte = (control_byte << 1) & 0xFF

            if control_byte & 0x80:
                current_b2 = ord(data.read(1))
                y += 1

            control_byte = (control_byte << 1) & 0xFF

            decompressed.append(current_b1)
            decompressed.append(current_b2)

    return decompressed, y
