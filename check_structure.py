text = open('C:/Users/DELL/my-board/my-board.kicad_sch', 'r', encoding='utf-8').read()

print('File size:', len(text))

# Find positions of major sections  
ls_pos = text.index('(lib_symbols')
si_pos = text.index('(sheet_instances')

print(f'lib_symbols at {ls_pos}')
print(f'sheet_instances at {si_pos}')

# Count top-level instances between lib_symbols and sheet_instances
between = text[ls_pos + 1:si_pos]

# Find all \n\tsymbol\n patterns (instances, not in lib_symbols)
ls_depth = 0
in_ls = True
instance_count = 0
for i, ch in enumerate(text):
    if i < ls_pos:
        continue
    if in_ls:
        if ch == '(':
            ls_depth += 1
        elif ch == ')':
            ls_depth -= 1
            if ls_depth == 0:
                in_ls = False
    else:
        if i > si_pos:
            break
        # Check for instance start
        if ch == '(' and text[i:i+8] == '(symbol ':
            instance_count += 1
            # Find lib_id
            lid = text.find('(lib_id', i, i + 500)
            if lid > 0:
                end = text.find(')', lid)
                lib_id_val = text[lid:end+1]
                print(f'Instance {instance_count}: {lib_id_val}')

print(f'Total instances: {instance_count}')
