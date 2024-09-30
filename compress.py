#!/usr/bin/env python

from pathlib import Path

from a816.cpu.mapping import Bus
from a816.writers import IPSWriter

from utils.assets import CompressedAssets
from utils.compress import compress_blocks

low_rom_bus = Bus("low_rom_default_mapping")

low_rom_bus.map("1", (0x00, 0x6F), (0x8000, 0xFFFF), mask=0x8000, mirror_bank_range=(0x80, 0xCF))
low_rom_bus.map("2", (0x7E, 0x7F), (0, 0xFFFF), mask=0x1_0000, writeable=True)


def file_compress():
    graphics_path = Path("graphics")
    assets_path = Path("build")

    for _, _, name in graphics_path.walk():
        graphics_file = graphics_path / name[0]
        data = graphics_file.read_bytes()
        compressed = compress_blocks(data)
        (assets_path / name[0]).write_bytes(compressed)


def ips_generator():
    graphics_path = Path("graphics")
    graphics_patch = Path("bm.ips").open("wb")
    ips_writer = IPSWriter(graphics_patch)

    relocated_base = low_rom_bus.get_address(0xC08000)

    ips_writer.begin()
    compressed_assets = CompressedAssets()

    for _, _, name in graphics_path.walk():
        graphics_file = graphics_path / name[0]
        asset_id = int(name[0].split(".")[0], 16)
        data = graphics_file.read_bytes()
        compressed = compress_blocks(data)
        compressed_assets.write_address(ips_writer, asset_id, relocated_base)
        ips_writer.write_block(compressed, relocated_base.physical)
        relocated_base += len(compressed)
    ips_writer.end()


if __name__ == "__main__":
    # file_compress()
    ips_generator()
