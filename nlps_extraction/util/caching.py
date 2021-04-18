import os
from loguru import logger
import msgpack


def recover_cache(cache_location):
    if os.path.exists(cache_location):
        logger.info(" (▰˘◡˘▰) Loading cached file (▰˘◡˘▰)")
        with open(cache_location, "rb") as data_file:
            retrieved_values = msgpack.unpack(data_file, encoding="utf-8")
            return retrieved_values
    else:
        logger.info(" (◕︵◕) File is not in cache (◕︵◕)")
        return False


def save_cache(values, cache_location):
    with open(cache_location, "wb") as outfile:
        logger.info("Caching file (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧")
        msgpack.pack(values, outfile)
