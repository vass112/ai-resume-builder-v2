import re
c = open('C:/Users/DELL/my-board/my-board.kicad_sch').read()

# Find the ESP32 lib symbol area
lib_start = c.index('(lib_symbols')
# Find the ESP32 symbol
esp_start = c.find('(symbol "Arduino_Nano_ESP32"', lib_start)
if esp_start < 0:
    print('ESP32 symbol NOT FOUND in lib_symbols!')
else:
    # Find the matching close
    depth = 0
    end = esp_start
    for i in range(esp_start, len(c)):
        if c[i] == '(': depth += 1
        elif c[i] == ')':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    block = c[esp_start:end]
    o = block.count('(')
    cl = block.count(')')
    print(f'ESP32 lib symbol: (={o}, )={cl}, balanced={o==cl}')
    print(f'Length: {len(block)} chars')
    
    # Check if the symbol ends properly (should be followed by ) or newline+)
    after = c[end:end+50]
    print(f'After ESP32 symbol: {repr(after)}')
    
    # Check for any ( before the next instance symbol
    rest = c[end:]
    next_sym = rest.find('(symbol')
    print(f'Next (symbol found at offset {next_sym} in rest')
    print(f'Rest starts with: {repr(rest[:100])}')
    
    # Now let's also check the whole lib_symbols section
    ls_end = rest.find(')')
    actual_ls_end = -1
    depth = 1
    for i in range(len(block)-1, len(c)):
        pass
    
    # Check from ESP32 to the next (symbol instance
    next_inst = c.find('(symbol\n\t\t(lib_id', end)
    if next_inst < 0:
        next_inst = c.find('(symbol', end)
    print(f'Next instance symbol at {next_inst}')
    print(f'Between ESP32 and next instance: {repr(c[end:next_inst+100])}')
