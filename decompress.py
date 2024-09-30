#!/usr/bin/env python
from pathlib import Path

from utils.assets import CompressedAssets
from utils.decompress import decompress_blocks

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
            decompressed_path = decompressed_dir / f"{asset_id:02x}.bin"
            compressed_path = compressed_dir / "{asset_id:02x}.bin"
            addr = block_addr.physical
            assert addr is not None
            rom.seek(addr)
            data = rom.read(block_count * 0x25)

            decompressed, compressed_size = decompress_blocks(data, block_count)
            decompressed_path.write_bytes(decompressed)

            compressed_path.write_bytes(data[:compressed_size])
