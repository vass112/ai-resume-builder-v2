c = open('C:/Users/DELL/my-board/step2.kicad_sch').read()
# Find where (lib_symbols closes
ls = c.index('(lib_symbols')
depth = 1
ls_end = -1
for i in range(ls+1, len(c)):
    if c[i] == '(':
        depth += 1
    elif c[i] == ')':
        depth -= 1
        if depth == 0:
            ls_end = i + 1
            break
print('lib_symbols from %d to %d' % (ls, ls_end))
print('After lib_symbols: %s' % repr(c[ls_end:ls_end+80]))
print('Context around ls_end-10: %s' % repr(c[ls_end-10:ls_end+50]))
# Check full structure
full = c
print('Full balance: (=%d, )=%d' % (full.count('('), full.count(')')))
# Now check the balance of the instances section
inst = c[ls_end:]
depth = 0
for i, ch in enumerate(inst):
    if ch == '(': depth += 1
    elif ch == ')':
        depth -= 1
    if depth == 0 and ch == ')':
        print('First complete block after lib_symbols (at offset %d): %s' % (i, repr(inst[i-20:i+20])))
        break
