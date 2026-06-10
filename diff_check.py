import re

# Compare working min.kicad_sch with failing my-board.kicad_sch
min_f = open('C:/Users/DELL/my-board/min.kicad_sch').read()
my_f = open('C:/Users/DELL/my-board/my-board.kicad_sch').read()

print('=== min.kicad_sch ===')
print(f'Size: {len(min_f)} chars')
print(f'CRLF: {min_f.count(chr(13)+chr(10))} / LF: {min_f.count(chr(10)) - min_f.count(chr(13)+chr(10))}')
print(f'Starts with BOM: {min_f.startswith(chr(0xFEFF))}')
print(f'First 80 bytes: {repr(min_f[:80])}')

print()
print('=== my-board.kicad_sch ===')
print(f'Size: {len(my_f)} chars')
print(f'CRLF: {my_f.count(chr(13)+chr(10))} / LF: {my_f.count(chr(10)) - my_f.count(chr(13)+chr(10))}')
print(f'Starts with BOM: {my_f.startswith(chr(0xFEFF))}')
print(f'First 80 bytes: {repr(my_f[:80])}')

# Check what comes after lib_symbols in my file
lib_end = my_f.index(')', my_f.index('(lib_symbols'))
after = my_f[lib_end+1:]
# Find the first few non-whitespace characters
for i, ch in enumerate(after):
    if not ch in ' \t\n\r':
        print(f'\nAfter lib_symbols closing, first non-ws at offset {i}: {repr(after[i:i+100])}')
        break

# Check if there's extra ) between lib_symbols and instances
ls_start = my_f.index('(lib_symbols')
# Find proper end of lib_symbols
depth = 1
ls_end = ls_start + 10
for i in range(ls_start+1, len(my_f)):
    if my_f[i] == '(': depth += 1
    elif my_f[i] == ')':
        depth -= 1
        if depth == 0:
            ls_end = i + 1
            break
print(f'\nlib_symbols from {ls_start} to {ls_end}')
print(f'After lib_symbols: {repr(my_f[ls_end:ls_end+100])}')
