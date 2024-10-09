from io import BytesIO
from unittest import TestCase

from utils.compress import compress_block, compress_blocks, compress_blocks_2
from utils.decompress import decompress_blocks, decompress_blocks_2


class BMTestCase(TestCase):
    def test_empty(self) -> None:
        test_decompressed, _ = decompress_blocks(BytesIO(bytearray([0, 0, 0, 0])), 1)
        self.assertEqual(test_decompressed, b"\x00" * 32)

    def test_set_value(self) -> None:
        test_decompressed, _ = decompress_blocks(
            BytesIO(bytearray([0b10000000, 1, 0, 0, 0])), 1
        )
        self.assertEqual(test_decompressed, b"\x01\x00" * 8 + b"\x00" * 16)

    def test_set_value_twice(self) -> None:
        test_decompressed, _ = decompress_blocks(
            BytesIO(bytearray([0b11000000, 1, 2, 0, 0, 0])), 1
        )
        self.assertEqual(test_decompressed, b"\x01\x02" * 8 + b"\x00" * 16)

    def test_not_compressed_block(self) -> None:
        test_decompressed, _ = decompress_blocks(
            BytesIO(
                bytearray(
                    [
                        0b11111111,
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7,
                        8,
                        0b11111111,
                        9,
                        10,
                        11,
                        12,
                        13,
                        14,
                        15,
                        16,
                        0,
                        0,
                    ]
                )
            ),
            1,
        )
        self.assertEqual(
            test_decompressed, bytearray([b for b in range(1, 17)]) + b"\x00" * 16
        )

    def test_compress_block(self) -> None:
        data = [
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
        ] + [
            0x00,
            0x00,
            0x7E,
            0x02,
            0xFF,
            0x01,
            0xFF,
            0x39,
            0xE7,
            0x21,
            0xE7,
            0x21,
            0xE7,
            0x21,
            0xE7,
            0x21,
        ]
        test_compressed = compress_block(BytesIO(bytes(data)))
        compressed = [
            0b0,
            0b0,
            0b00111101,
            0x7E,
            0x02,
            0xFF,
            0x1,
            0x39,
            0b11000000,
            0xE7,
            0x21,
        ]

        self.assertEqual(test_compressed, bytearray(compressed))
        test_decompressed, _ = decompress_blocks(BytesIO(bytearray(compressed)), 1)

        self.assertEqual(test_decompressed, bytearray(data))

    def test_compress_blocks(self) -> None:
        data = [
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
        ] + [
            0x00,
            0x00,
            0x7E,
            0x02,
            0xFF,
            0x01,
            0xFF,
            0x39,
            0xE7,
            0x21,
            0xE7,
            0x21,
            0xE7,
            0x21,
            0xE7,
            0x21,
        ]
        test_compressed = compress_blocks(bytes(data))
        compressed = [
            0b0,
            0b0,
            0b00111101,
            0x7E,
            0x02,
            0xFF,
            0x1,
            0x39,
            0b11000000,
            0xE7,
            0x21,
        ]

        self.assertEqual(test_compressed, bytearray(compressed))

    def test_decompress_block_2(self):
        decompressed, _ = decompress_blocks_2(BytesIO(bytearray([0b0, 0b0, 0b0])), 1)
        self.assertEqual(decompressed, bytearray([0] * 0x20))

        decompressed, _ = decompress_blocks_2(
            BytesIO(bytearray([0b0, 0b0, 0b11100000, 1, 2, 0])), 1
        )
        self.assertEqual(
            decompressed, bytearray([0] * 0x10) + bytearray([1, 0, 2, 0] + [0] * 12)
        )

        recompressed = compress_blocks_2(decompressed)
        print(recompressed)
        ...
