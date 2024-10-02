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


def decompress_tile_map(data: bytes, block_count: int) -> tuple[bytearray, int]:
    decompressed = bytearray()

    y = 0
    current_b1 = 0
    current_b2 = 0

    for _ in range(0, block_count):
        for _ in range(8):
            control_byte = data[y]
            y += 1
            for _ in range(4):
                if control_byte & 0x80:
                    current_b1 = data[y]
                    y += 1

                control_byte = (control_byte << 1 ) & 0xFF

                if control_byte & 0x80:
                    current_b2 = data[y]
                    y +=1

                control_byte = (control_byte << 1 ) & 0xFF


                decompressed.append(current_b1)
                decompressed.append(current_b2)

    return decompressed, y
