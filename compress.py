#!/usr/bin/env python

from pathlib import Path

from a816.symbols import low_rom_bus
from a816.writers import IPSWriter

from utils.assets import CompressedAssets
from utils.compress import compress_blocks, compress_tile_map


def file_compress() -> None:
    graphics_path = Path("graphics")
    assets_path = Path("build")

    for _, _, name in graphics_path.walk():
        graphics_file = graphics_path / name[0]
        data = graphics_file.read_bytes()
        compressed = compress_blocks(data)
        (assets_path / name[0]).write_bytes(compressed)


def ips_generator() -> None:
    rom_path = Path("bm.sfc")

    graphics_path = Path("graphics")
    graphics_patch = Path("bm.ips").open("wb")
    ips_writer = IPSWriter(graphics_patch)

    relocated_base = low_rom_bus.get_address(0xC08000)

    ips_writer.begin()
    with rom_path.open("rb") as rom:

        compressed_assets = CompressedAssets()
        for graphics_file in list(graphics_path.glob('*.bin')):
            stem = graphics_file.stem
            print(f"compressing {stem}")
            asset_id = int(stem, 16)
            data = graphics_file.read_bytes()

            match compressed_assets.get_compression_type(rom, asset_id):
                case 0:
                    compressed = compress_blocks(data)
                case 1:
                    compressed = compress_tile_map(data)
                case _:
                    continue

            compressed_assets.write_address(ips_writer, asset_id, relocated_base)
            relocated_base_physical = relocated_base.physical
            assert relocated_base_physical is not None
            ips_writer.write_block(compressed, relocated_base_physical)
            relocated_base += len(compressed)
    ips_writer.end()


if __name__ == "__main__":
    # file_compress()
    ips_generator()
