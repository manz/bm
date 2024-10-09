#!/usr/bin/env python
import json
import logging
from pathlib import Path
from typing import BinaryIO

from utils.assets import CompressedAssets
from utils.decompress import (
    decompress_tile_map,
    decompress_tile_map2,
    decompress_tiles,
    UnknownCompressionType,
)

logger = logging.getLogger("bm")


def dump_assets_catalog(rom: BinaryIO) -> None:
    assets_catalog_file = Path("./assets_catalog.json")
    assets_catalog = {}
    compressed_assets = CompressedAssets()

    for asset_id in range(0, 188):
        block_count = compressed_assets.get_block_count(rom, asset_id)
        block_addr = compressed_assets.get_address(rom, asset_id)
        asset_type = compressed_assets.get_type(rom, asset_id)
        compression_kind = compressed_assets.get_compression(rom, asset_id)
        assets_catalog[asset_id] = {
            "block_count": block_count,
            "block_addr": block_addr.logical_value,
            "asset_type": asset_type,
            "compression_kind": compression_kind,
        }

    assets_catalog_file.write_text(json.dumps(assets_catalog, indent=4))


def decompress() -> None:
    rom_path = Path("bm.sfc")

    decompressed_dir = Path("./decompressed")
    compressed_dir = Path("./compressed")

    compressed_dir.mkdir(exist_ok=True)
    decompressed_dir.mkdir(exist_ok=True)

    with rom_path.open("rb") as rom:
        compressed_assets = CompressedAssets()

        for asset_id in range(0, 188):
            block_count = compressed_assets.get_block_count(rom, asset_id)
            block_addr = compressed_assets.get_address(rom, asset_id)
            asset_type = compressed_assets.get_type(rom, asset_id)
            compression_type = compressed_assets.get_compression(rom, asset_id)

            compressed_path = compressed_dir / f"{asset_id:02x}.bin"
            addr = block_addr.physical
            assert addr is not None
            rom.seek(addr)

            logger.debug(
                f"{asset_type:02x}({compression_type:02x}):: {asset_id:02x}: {block_count:02x}"
            )

            if block_count == 0:
                continue

            match asset_type:
                case 0:
                    try:
                        decompressed, compressed_size = decompress_tiles(
                            compression_type, rom, block_count
                        )
                    except UnknownCompressionType as e:
                        logger.error(
                            f"{asset_id:02x} unsupported compression type : {str(e)}."
                        )
                        continue

                    decompressed_path = decompressed_dir / f"{asset_id:02x}.chr"
                case 1:
                    decompressed, compressed_size = decompress_tile_map(
                        rom, block_count
                    )
                    decompressed_path = decompressed_dir / f"{asset_id:02x}.map"
                case 2:
                    decompressed, compressed_size = decompress_tile_map2(rom, 0x40)
                case _:
                    logger.error(
                        f"{asset_id:02x}: Unsupported asset_type : {asset_type:02x}"
                    )
                    continue

            decompressed_path.write_bytes(decompressed)

            rom.seek(addr)
            compressed_path.write_bytes(rom.read(compressed_size))


if __name__ == "__main__":
    decompress()
