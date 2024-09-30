# bm

## Install

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt 
```

## decompress
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
