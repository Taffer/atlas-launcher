#!/usr/bin/env python3
#
# Test interleaving reads/MD5 updates.
#
# Results: 1MB seems to do well.

import hashlib
import time


def sum_all(filename):
    with open(filename, 'rb') as fp:
        data = fp.read()
    md5 = hashlib.md5()
    md5.update(data)

    return md5.hexdigest()


def sum_block(filename, block_size):
    md5 = hashlib.md5()
    with open(filename, 'rb') as fp:
        data = fp.read(block_size)
        while len(data) != 0:
            md5.update(data)
            data = fp.read(block_size)

    return md5.hexdigest()


def main():
    all_times = []
    block_times = []
    big_block_times = []

    for i in range(10):
        t1 = time.time()
        hd = sum_all('testdata.dat')
        dt = time.time() - t1
        all_times.append(dt)

        t1 = time.time()
        hd = sum_block('testdata.dat', 1024 * 64)
        dt = time.time() - t1
        block_times.append(dt)

        t1 = time.time()
        hd = sum_block('testdata.dat', 1024 * 1024)
        dt = time.time() - t1
        big_block_times.append(dt)

    print('All at once: {0}'.format(all_times))
    print('           = {0}'.format(sum(all_times)))
    print('Block read : {0}'.format(block_times))
    print('           = {0}'.format(sum(block_times)))
    print('Big read   : {0}'.format(big_block_times))
    print('           = {0}'.format(sum(big_block_times)))


if __name__ == '__main__':
    main()
