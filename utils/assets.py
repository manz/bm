import struct

from a816.cpu.mapping import Address
from a816.symbols import low_rom_bus
from a816.writers import IPSWriter


class CompressedAssets:
    def __init__(self):
        self.block_size_table = low_rom_bus.get_address(0x8e8178)
        self.b1_addr = low_rom_bus.get_address(0x8e82f0)
        self.b2_addr = low_rom_bus.get_address(0x8e83ac)
        self.b3_addr = low_rom_bus.get_address(0x8e8468)

    def get_block_count(self, rom, asset_id: int) -> int:
        rom.seek((self.block_size_table + asset_id).physical)
        block_count = rom.read(1)
        return ord(block_count)

    def get_address(self, rom, asset_id: int) -> Address:
        rom.seek((self.b1_addr + asset_id).physical)
        b1 = ord(rom.read(1))
        rom.seek((self.b2_addr + asset_id).physical)
        b2 = ord(rom.read(1))
        rom.seek((self.b3_addr + asset_id).physical)
        b3 = ord(rom.read(1))
        addr = b1 | b2 << 8 | b3 << 16
        return low_rom_bus.get_address(addr)


    def write_address(self, ips_writer: IPSWriter, asset_id: int, relocated_address: Address) -> None:
        addr = relocated_address.logical_value
        print(hex(addr))
        b1 = addr & 0xff
        b2 = addr >> 8 & 0xff
        b3 = addr >> 16 & 0xff

        ips_writer.write_block(struct.pack("B", b1), (self.b1_addr + asset_id).physical)
        ips_writer.write_block(struct.pack("B", b2), (self.b2_addr + asset_id).physical)
        ips_writer.write_block(struct.pack("B", b3), (self.b3_addr + asset_id).physical)
