.PHONY: all
all: bm.ips

.PHONY: bm.ips
bm.ips:
	./compress.py

.PHONY: decompress
	./decompress.py
