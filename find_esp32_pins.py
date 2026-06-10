import re

with open('C:/Program Files/KiCad/8.0/share/kicad/symbols/MCU_Module.kicad_sym', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.index('(symbol "Arduino_Nano_ESP32"')
depth, i = 0, start
while i < len(text):
    if text[i] == '(': depth += 1
    elif text[i] == ')':
        depth -= 1
        if depth == 0:
            symbol_text = text[start:i+1]
            break
    i += 1

# Find all pin sections by depth matching
pos = 0
while True:
    p_start = symbol_text.find('(pin ', pos)
    if p_start < 0:
        break
    depth, i = 0, p_start
    while i < len(symbol_text):
        if symbol_text[i] == '(': depth += 1
        elif symbol_text[i] == ')':
            depth -= 1
            if depth == 0:
                pin_text = symbol_text[p_start:i+1]
                break
        i += 1
    at_m = re.search(r'\(at[ \t]+([0-9.\-]+)[ \t]+([0-9.\-]+)[ \t]+([0-9.]+)\)', pin_text)
    num_m = re.search(r'\(number[ \t]+"([^"]+)"', pin_text)
    name_m = re.search(r'\(name[ \t]+"([^"]+)"', pin_text)
    if at_m and num_m:
        x, y, angle, num = at_m.group(1), at_m.group(2), at_m.group(3), num_m.group(1)
        name = name_m.group(1) if name_m else '?'
        print(f'Pin {num} ({name}): at ({x}, {y}) angle={angle}')
    pos = i + 1
