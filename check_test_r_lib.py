c = open('C:/Users/DELL/my-board/test_r_lib.kicad_sch').read()
ls = c.index('(lib_symbols')
print('lib_symbols section:')
print(c[ls:ls+200])
gnd_idx = c.find('(symbol "power:GND"', ls)
r_idx = c.find('(symbol "R"', ls)
print()
print('GND at', gnd_idx)
print('R at', r_idx)
print()
print('Before R:')
print(repr(c[r_idx-100:r_idx]))
# find GND end
depth = 0
gnd_end = gnd_idx
for i in range(gnd_idx, len(c)):
    if c[i] == '(': depth += 1
    elif c[i] == ')':
        depth -= 1
        if depth == 0:
            gnd_end = i + 1
            break
print('GND ends at', gnd_end)
print('Between GND end and R:', repr(c[gnd_end:r_idx]))
print()
# Check the whole lib_symbols end
depth = 0
ls_end = ls
for i in range(ls, len(c)):
    if c[i] == '(': depth += 1
    elif c[i] == ')':
        depth -= 1
        if depth == 0:
            ls_end = i + 1
            break
print('lib_symbols from', ls, 'to', ls_end)
print('After lib_symbols:', repr(c[ls_end:ls_end+100]))
