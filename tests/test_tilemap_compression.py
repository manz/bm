import io
import unittest

from utils.compress import compress_tile_map
from utils.decompress import decompress_tile_map


class TileMapCompressionTestCase(unittest.TestCase):
    def test_decompression_empty(self) -> None:
        data = io.BytesIO(bytearray([0x00] * 8))

        decompressed, _ = decompress_tile_map(data, 1)
        self.assertEqual(len(decompressed), 64)

    def test_decompression_not_empty(self) -> None:
        data = io.BytesIO(bytearray([0x80, 0x12] + ([0] * 7)))

        decompressed, _ = decompress_tile_map(data, 1)
        self.assertEqual(len(decompressed), 64)

    def test_compression(self) -> None:
        data = bytearray([0b11000000, 0x12, 0x13] + ([0] * 7))

        decompressed, _ = decompress_tile_map(io.BytesIO(data), 1)
        self.assertEqual(64, len(decompressed))

        compressed = compress_tile_map(decompressed)

        self.assertEqual(data, compressed)
