#!/usr/bin/env python
import logging
from pathlib import Path

from a816.symbols import low_rom_bus
from a816.writers import IPSWriter

from utils.assets import CompressedAssets
from utils.compress import compress_tile_map, compress_tiles
from utils.decompress import UnknownCompressionType

logger = logging.getLogger("bm")


def ips_generator() -> None:
    rom_path = Path("bm.sfc")

    graphics_path = Path("graphics")
    graphics_patch = Path("bm.ips").open("wb")
    ips_writer = IPSWriter(graphics_patch)

    relocated_base = low_rom_bus.get_address(0xC08000)

    ips_writer.begin()
    with rom_path.open("rb") as rom:
        compressed_assets = CompressedAssets()
        files = (
            list(graphics_path.glob("*.bin"))
            + list(graphics_path.glob("*.chr"))
            + list(graphics_path.glob("*.map"))
        )

        for graphics_file in files:
            stem = graphics_file.stem
            logger.debug(f"Compressing {stem}")
            asset_id = int(stem, 16)
            data = graphics_file.read_bytes()

            match compressed_assets.get_type(rom, asset_id):
                case 0:
                    compression_type = compressed_assets.get_compression(rom, asset_id)
                    try:
                        compressed = compress_tiles(compression_type, data)
                    except UnknownCompressionType as e:
                        logger.error(
                            f"{asset_id:02x} unsupported compression type {str(e)}"
                        )

                case 1:
                    compressed = compress_tile_map(data)

                case _:
                    continue

            compressed_assets.write_address(ips_writer, asset_id, relocated_base)
            relocated_base_physical = relocated_base.physical
            logger.debug(f"relocated address {relocated_base.logical_value:02x}")

            assert relocated_base_physical is not None
            ips_writer.write_block(compressed, relocated_base_physical)
            relocated_base += len(compressed) + (0x20 * 8)
    ips_writer.end()


if __name__ == "__main__":
    ips_generator()
