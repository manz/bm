import struct
from typing import BinaryIO

from a816.cpu.mapping import Address
from a816.symbols import low_rom_bus
from a816.writers import Writer


class CompressedAssets:
    def __init__(self) -> None:
        self.block_size_table = low_rom_bus.get_address(0x8E8178)
        self.b1_addr = low_rom_bus.get_address(0x8E82F0)
        self.b2_addr = low_rom_bus.get_address(0x8E83AC)
        self.b3_addr = low_rom_bus.get_address(0x8E8468)
        self.assets_flags = low_rom_bus.get_address(0x8E8000)

    def get_block_count(self, rom: BinaryIO, asset_id: int) -> int:
        addr = (self.block_size_table + asset_id).physical
        assert addr is not None
        rom.seek(addr)
        block_count = rom.read(1)
        return ord(block_count)

    def get_flags(self, rom: BinaryIO, asset_id: int) -> int:
        addr = (self.assets_flags + asset_id).physical
        assert addr is not None
        rom.seek(addr)
        return ord(rom.read(1))

    def get_type(self, rom: BinaryIO, asset_id: int) -> int:
        flags = self.get_flags(rom, asset_id)

        return flags & 0x0F

    def get_compression(self, rom: BinaryIO, asset_id: int) -> int:
        flags = self.get_flags(rom, asset_id)

        return (flags >> 3) & 0x06

    def get_address(self, rom: BinaryIO, asset_id: int) -> Address:
        addr = (self.b1_addr + asset_id).physical
        assert addr is not None
        rom.seek(addr)
        b1 = ord(rom.read(1))

        addr = (self.b2_addr + asset_id).physical
        assert addr is not None
        rom.seek(addr)
        b2 = ord(rom.read(1))

        addr = (self.b3_addr + asset_id).physical
        assert addr is not None
        rom.seek(addr)
        b3 = ord(rom.read(1))
        addr = b1 | b2 << 8 | b3 << 16
        return low_rom_bus.get_address(addr)

    def write_address(
        self, writer: Writer, asset_id: int, relocated_address: Address
    ) -> None:
        addr = relocated_address.logical_value
        b1 = addr & 0xFF
        b2 = addr >> 8 & 0xFF
        b3 = addr >> 16 & 0xFF

        addr_1 = (self.b1_addr + asset_id).physical
        assert addr_1 is not None
        writer.write_block(struct.pack("B", b1), addr_1)

        addr_2 = (self.b2_addr + asset_id).physical
        assert addr_2 is not None
        writer.write_block(struct.pack("B", b2), addr_2)

        addr_3 = (self.b3_addr + asset_id).physical
        assert addr_3 is not None
        writer.write_block(struct.pack("B", b3), addr_3)
