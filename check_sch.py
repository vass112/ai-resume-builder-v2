import re
c = open('C:/Users/DELL/my-board/my-board.kicad_sch').read()

# Check lib_symbols balance
lib_start = c.index('(lib_symbols')
lib_end = c.index(')', lib_start)
lib_content = c[lib_start:lib_end+1]
o = lib_content.count('(')
cl = lib_content.count(')')
print(f'lib_symbols: (={o}, )={cl}, balanced={o==cl}')

# Check all instance symbols
syms = list(re.finditer(r'\(symbol\n\s+\(lib_id', c))
print(f'Total instance symbols: {len(syms)}')

# Check each symbol for proper structure
for m in syms:
    start = m.start()
    depth = 0
    end = start
    for i in range(start, len(c)):
        if c[i] == '(': depth += 1
        elif c[i] == ')':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    block = c[start:end]
    lib_match = re.search(r'lib_id "([^"]+)"', block)
    ref_match = re.search(r'property "Reference" "([^"]+)"', block)
    lib = lib_match.group(1) if lib_match else 'UNKNOWN'
    ref = ref_match.group(1) if ref_match else 'UNKNOWN'
    o2 = block.count('(')
    c2 = block.count(')')
    print(f'  {ref} ({lib}): (={o2}, )={c2} {"OK" if o2==c2 else "UNBALANCED!"}')
    if o2 != c2:
        print(f'    First 150: {repr(block[:150])}')

# Check file balance
print(f'File: (={c.count("(")}, )={c.count(")")}')
print(f'File ends with: {repr(c[-30:])}')
print(f'File starts with: {repr(c[:30])}')

# Check for structure: what's between lib_symbols end and first symbol?
after_lib = c[lib_end+1:]
print(f'\nContent after lib_symbols (first 500 chars):')
print(repr(after_lib[:500]))
