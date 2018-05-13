"""
Bismuth
Common variables and helpers for PoS

Serves as config file for POC and tests
"""

import os
import shutil
import requests
import tarfile
# from collections import OrderedDict
from hashlib import blake2b

__version__ = '0.0.12'

# POC - Will be taken from config - Always 10 chars
# TODO: enforce 10 chars
POSNET = 'posnet0001'
POSNET_ALLOW = 'posnet0001,posnet0002'

# Network Byte ID - 0x19 = Main PoS Net 'B' - 0x55 Test PoS Net 'b'
NETWORK_ID = b'\x19'
# NETWORK_ID = b'\x55'

# How long to wait in the main client loop
WAIT = 10

# limit, so nodes won't want to play with that.
FUTURE_ALLOWED = 5

VERBOSE = True

# POC prefix is for POC only, will use real data later.

# The reference list of active Masternodes for the round
# address, ip, port, weight
POC_MASTER_NODES_LIST = [
    ('BLYkQwGZmwjsh7DY6HmuNBpTbqoRqX14ne', '127.0.0.1', 6969, 1),  # mn 0
    ('BHbbLpbTAVKrJ1XDLMM48Qa6xJuCGofCuH', '127.0.0.1', 6970, 2),
    ('B8stX39s5NBFx746ZX5dcqzpuUGjQPJViC', '127.0.0.1', 6971, 1),
    ('BMSMNNzB9qdDp1vudRZoge4BUZ1gCUC3CV', '127.0.0.1', 6972, 1),
    ('BNJp77d1BdoaQu9HEpGjKCsGcKqsxkJ7FD', '127.0.0.1', 6973, 1)
    ]

# The broadhash of the previous round determines the shuffle.
# block hashes and broad hashes are 20 bytes
POC_LAST_BROADHASH = b"123456789abcdef12345"

"""
Here comes tuneable algorithm variables 
"""

# Duration of a PoS slot in minute - each slot can be filled by a block (or stay empty)
POS_SLOT_TIME_MIN = 5
POS_SLOT_TIME_SEC = POS_SLOT_TIME_MIN * 60

# How many slots in a round? Better keep them an odd number.
MAX_ROUND_SLOTS = 3

# How many block times to wait at the end of a round to reach consensus?
END_ROUND_SLOTS = 1

# How many tests should the whole Net perform per slot?
# each test will issue 2 messages, one from the tester, the other from the testee
TESTS_PER_SLOT = 5

# We can run several type of tests. They are indexed by a byte. This can evolve with time.
TESTS_TYPE = [0, 1, 2, 3, 4]

# Block validation Criteria

# Should be less than TESTS_PER_SLOT*2
REQUIRED_MESSAGES_PER_BLOCK = 4
REQUIRED_SOURCES_PER_BLOCK = 3

# This is a constant. Time for block 0, slot 0 of the PoS chain. Can't change once launched.
ORIGIN_OF_TIME = 1522419000


# Round time in seconds
ROUND_TIME_SEC = POS_SLOT_TIME_SEC * (MAX_ROUND_SLOTS + END_ROUND_SLOTS)


GENESIS_SEED = 'BIG_BANG_HASH'
GENESIS_HASH = blake2b(GENESIS_SEED.encode('utf-8'), digest_size=20)
GENESIS_ADDRESS = 'BLYkQwGZmwjsh7DY6HmuNBpTbqoRqX14ne'
GENESIS_SIGNATURE = ''


# GENERIC HELPERS


def download_file(url, filename):
    """
    Fetch a file from an URL with progres indicator
    :param url:
    :param filename:
    :return:
    """
    try:
        r = requests.get(url, stream=True)
        total_size = int(r.headers.get('content-length')) / 1024
        with open(filename, 'wb') as filename:
            chunkno = 0
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    chunkno = chunkno + 1
                    if chunkno % 10000 == 0:  # every x chunks
                        print("Downloaded {} %".format(int(100 * ((chunkno) / total_size))))

                    filename.write(chunk)
                    filename.flush()
            print("Downloaded 100 %")

        return filename
    except:
        raise


def update_source(url, app_log=None):
    """
    Update source file from an url
    :param url: url of the tgz archive
    :param app_log: optional log handler
    :return:
    """
    try:
        archive_path = "./mnd.tgz"
        download_file(url, archive_path)
        tar = tarfile.open(archive_path)
        tar.extractall("./")
        tar.close()
        # move to current dir
        from_dir = "./mnd_zip/"
        files = os.listdir(from_dir)
        for f in files:
            shutil.move(from_dir + f, './' + f)
    except:
        if app_log:
            app_log.warning("Something went wrong while update_source, aborted")
        raise


def same_height(peer_status, our_status):
    for key in ("height", "round", "sir", "block_hash"):
        if peer_status[key] != our_status[key]:
            return False
    return True


if __name__ == "__main__":
    print("I'm a module, can't run!")
