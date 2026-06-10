import re

def read_lib_sym(lib, name):
    with open(f'C:/Program Files/KiCad/8.0/share/kicad/symbols/{lib}.kicad_sym', 'r', encoding='utf-8') as f:
        text = f.read()
    start = text.index(f'(symbol "{name}"')
    depth, i = 0, start
    while i < len(text):
        if text[i] == '(': depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                sym = text[start:i+1]
                sym = sym.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"')
                sym = sym.replace(f'(symbol "{name}_', f'(symbol "{lib}:{name}_')
                return sym
        i += 1
    return text[start:]

for lib, name in [('power', 'GND'), ('MCU_Module', 'Arduino_Nano_ESP32')]:
    sym = read_lib_sym(lib, name)
    symbols = re.findall(r'\(symbol "([^"]+)"', sym)
    print(f'{lib}:{name} -> ALL symbols:')
    for s in symbols:
        print(f'  {s}')
    print()
