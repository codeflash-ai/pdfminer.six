"""Python implementation of Arcfour encryption algorithm.
See https://en.wikipedia.org/wiki/RC4
This code is in the public domain.

"""

from collections.abc import Sequence


class Arcfour:
    def __init__(self, key: Sequence[int]) -> None:
        # because Py3 range is not indexable
        s = list(range(256))
        j = 0
        klen = len(key)
        k_index = 0
        for i in range(256):
            j = (j + s[i] + key[k_index]) & 255
            (s[i], s[j]) = (s[j], s[i])
            k_index += 1
            if k_index == klen:
                k_index = 0
        self.s = s
        (self.i, self.j) = (0, 0)

    def process(self, data: bytes) -> bytes:
        (i, j) = (self.i, self.j)
        s = self.s
        r = bytearray()
        for c in data:
            i = (i + 1) & 255
            si = s[i]
            j = (j + si) & 255
            sj = s[j]
            # swap using cached values to avoid extra indexing
            s[i] = sj
            s[j] = si
            k = s[(si + sj) & 255]
            r.append(c ^ k)
        (self.i, self.j) = (i, j)
        return bytes(r)

    encrypt = decrypt = process
