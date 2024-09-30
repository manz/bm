from utils import xba


def decompress_blocks(data: bytes, block_count: int) -> tuple[bytearray, int]:
    y = 0

    decompressed = bytearray()
    accumulator = [0x00, 0x00]

    for current_block in range(0, block_count * 4):
        control_byte = data[y]
        if current_block & 1 == 0:
            accumulator = [0x00, 0x00]
        y += 1

        for _ in range(8):
            if control_byte & 0x80:
                accumulator[0] = data[y]
                y += 1

            decompressed.append(accumulator[0])
            xba(accumulator)
            control_byte = (control_byte << 1) & 0xFF

    return decompressed, y
