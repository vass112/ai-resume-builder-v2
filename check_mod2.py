import re
text = open('C:/Users/DELL/my-board/test_template_mod2.kicad_sch', 'r', encoding='utf-8').read()

# Find lib_symbols
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
print('lib_symbols section:')
print(ls_block)

# Check paren balance
opens = ls_block.count('(')
closes = ls_block.count(')')
print(f'\nlib_symbols: (={opens}, )={closes} {"OK" if opens==closes else "UNBALANCED!"}')

# Check ALL R symbol occurrences 
for m in re.finditer(r'\(symbol "([^"]+)"', ls_block):
    print(f'Symbol: {m.group(1)}')
