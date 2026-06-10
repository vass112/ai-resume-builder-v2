import re
from collections import Counter

text = open('C:/Users/DELL/my-board/my-board.kicad_sch', 'r', encoding='utf-8').read()
ls = text.index('(lib_symbols')
depth, i = 0, ls
while i < len(text):
    if text[i] == '(': depth += 1
    elif text[i] == ')':
        depth -= 1
        if depth == 0:
            ls_end = i + 1
            break
    i += 1

ls_block = text[ls:ls_end]
syms = re.findall(r'\(symbol "([^"]+)"', ls_block)
print('Symbols in lib_symbols:')
for s in syms:
    print(f'  {s}')

c = Counter(syms)
for s, count in c.items():
    if count > 1:
        print(f'  DUPLICATE: {s} ({count}x)')

# Also check instance lib_ids
inst_ids = re.findall(r'\(lib_id "([^"]+)"', text)
print('\nInstance lib_ids:')
for s in inst_ids:
    print(f'  {s}')
# Check which lib_ids don't have a matching symbol
sym_set = set(syms)
for s in inst_ids:
    if s not in sym_set:
        print(f'  MISSING: {s}')
