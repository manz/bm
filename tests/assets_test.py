import unittest

from a816.symbols import low_rom_bus
from a816.writers import Writer

from utils.assets import CompressedAssets


class StubWriter(Writer):
    def __init__(self) -> None:
        self.data: list[bytes] = []
        self.data_addresses: list[int] = []

    def begin(self) -> None:
        """not needed by StubWriter"""

    def write_block(self, block: bytes, block_address: int) -> None:
        self.data_addresses.append(block_address)
        self.data.append(block)

    def write_block_header(self, block: bytes, block_address: int) -> None:
        return None

    def end(self) -> None:
        """not needed by StubWriter"""


class AssetsCase(unittest.TestCase):
    def test_write(self) -> None:
        writer = StubWriter()
        assets = CompressedAssets()
        assets.write_address(writer, 0x0A, low_rom_bus.get_address(0xC08000))

        self.assertEqual(writer.data_addresses, [459514, 459702, 459890])
        self.assertEqual(writer.data, [b"\x00", b"\x80", b"\xc0"])
