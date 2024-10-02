#!/usr/bin/env python
import json
from pathlib import Path
from typing import BinaryIO

from utils.assets import CompressedAssets
from utils.decompress import decompress_blocks, decompress_tile_map

def dump_assets_catalog(rom: BinaryIO) -> None:
    assets_catalog_file = Path("./assets_catalog.json")
    assets_catalog = {}
    compressed_assets = CompressedAssets()

    for asset_id in range(0, 188):
        block_count = compressed_assets.get_block_count(rom, asset_id)
        block_addr = compressed_assets.get_address(rom, asset_id)
        compression_type = compressed_assets.get_compression_type(rom, asset_id)

        assets_catalog[asset_id] = {"block_count": block_count,
                                    "block_addr": block_addr.logical_value,
                                    "compression_type": compression_type}

    assets_catalog_file.write_text(json.dumps(assets_catalog, indent=4))



if __name__ == "__main__":
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
            compression_type = compressed_assets.get_compression_type(rom, asset_id)

            decompressed_path = decompressed_dir / f"{asset_id:02x}.bin"
            compressed_path = compressed_dir / f"{asset_id:02x}.bin"
            addr = block_addr.physical
            assert addr is not None
            rom.seek(addr)
            data = rom.read(block_count * 0x32)

            match compression_type:
                case 0:
                    decompressed, compressed_size = decompress_blocks(data, block_count)
                case 1:
                    decompressed, compressed_size = decompress_tile_map(data, block_count)
                case _:
                    print(f"{asset_id:02x}: Unsupported compression_type : {compression_type:02x}")
                    continue

            decompressed_path.write_bytes(decompressed)
            compressed_path.write_bytes(data[:compressed_size])

