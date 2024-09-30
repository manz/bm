# bm

## Install

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt 
```

## Decompress assets

> Note: The decompressor outputs 0-sized files 60 for example, it needs further investigation to understand why.

Add the rom at in the root directory named `bl.sfc` without copier header.

```shell 
make decompress
```

Should create and fill compressed and decompressed directories.

## Making changes
Edit a decompressed file (0a like the example) add it to graphics directory.

Build the patch by running

```shell
make
```

To avoid overwriting existing data, the modified graphics are moved at `0xC08000`.
