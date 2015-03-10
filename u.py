# Unicode emoji will only work with correctly compiled Python for wide unicode
# if the heroku Python is wrong, we can probably remove the emoji.  Though it is cool if we can

lst = range(0x0030, 0x0039 + 1) + \
range(0x0041, 0x005A + 1) + \
range(0x0061, 0x0079 + 1) + \
range(0x00C0, 0x00D6 + 1) + \
range(0x00D8, 0x00F6 + 1) + \
range(0x00F8, 0x00FF + 1) + \
range(0x0100, 0x017E + 1) + \
range(0x0374, 0x0378 + 1) + \
range(0x037b, 0x037e + 1) + \
range(0x0386, 0x038a + 1) + \
range(0x038e, 0x03a1 + 1) + \
range(0x03a3, 0x03FC + 1) + \
range(0x0400, 0x0481 + 1) + \
range(0x048A, 0x04FF + 1) + \
range(0x0531, 0x053B + 1) + \
range(0x05F0, 0x05F2 + 1) + \
range(0x1F300, 0x1F32C + 1) + \
range(0x1F330, 0x1F37D + 1) + \
range(0x1F380, 0x1F3CE + 1) + \
range(0x1F3D4, 0x1F3F7 + 1) + \
range(0x1F400, 0x1F4FE + 1) + \
range(0x1F500, 0x1F54A + 1) + \
range(0x1F550, 0x1F579 + 1) + \
range(0x1F57B, 0x1F5A3 + 1) + \
range(0x1F5A5, 0x1F5FF + 1)


lst2 = [0x0021, 0x002A, 0x002B, 0x002D, 0x002E, 0x0040]

u = map(unichr, lst)

u2 = map(unichr, lst2)

for i, ch in zip(list(lst+lst2), list(u+u2)):
    print format(i, '04x'), ch
