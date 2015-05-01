from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

all_chars = list(set(list(map(
    chr,
    list(range(0x0030, 0x0039 + 1)) +
    list(range(0x0041, 0x005A + 1)) +
    # list(range(0x0061, 0x0079 + 1)) +
    list(range(0x0061, 0x007A + 1)) +
    list(range(0x00C0, 0x00D6 + 1)) +
    list(range(0x00D8, 0x00F6 + 1)) +
    list(range(0x00F8, 0x00FF + 1)) +
    list(range(0x0100, 0x017E + 1)) +
    list(range(0x0374, 0x0378 + 1)) +
    list(range(0x037b, 0x037e + 1)) +
    list(range(0x0386, 0x038a + 1)) +
    list(range(0x038e, 0x03a1 + 1)) +
    list(range(0x03a3, 0x03FC + 1)) +
    list(range(0x0400, 0x0481 + 1)) +
    list(range(0x048A, 0x04FF + 1)) +
    list(range(0x0531, 0x053B + 1)) +
    list(range(0x05F0, 0x05F2 + 1)) +
    list(range(0x1F300, 0x1F32C + 1)) +
    list(range(0x1F330, 0x1F37D + 1)) +
    list(range(0x1F380, 0x1F3CE + 1)) +
    list(range(0x1F3D4, 0x1F3F7 + 1)) +
    list(range(0x1F400, 0x1F4FE + 1)) +
    list(range(0x1F500, 0x1F54A + 1)) +
    list(range(0x1F550, 0x1F579 + 1)) +
    list(range(0x1F57B, 0x1F5A3 + 1)) +
    list(range(0x1F5A5, 0x1F5FF + 1))
))))

not_leading_chars = list(map(
    chr,
    [0x0021, 0x002A, 0x002B, 0x002D, 0x005F, 0x002E, 0x0040]
))

# print ' '.join(all_chars)
# print ' '.join(not_leading_chars)
